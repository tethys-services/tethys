# Copyright 2020 Konstruktor, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict

import pytest

from tethys.core.networks import ZeroNetwork
from tethys.core.nodes import ZeroNode
from tethys.core.pipes import ZeroPipe
from tethys.core.sessions import SessionBase
from tethys.core.streams import StreamBase


def _split_lists(lst, count, cross=False):
    part_count = len(lst) // count
    return [
        lst[i * part_count : int((i + 1) * part_count * (1.5 if cross else 1))]
        for i in range(count - 1)
    ] + [lst[(count - 1) * part_count :]]


class NodeTest(ZeroNode):
    def __init__(self, *args, **kwargs):
        pass

    def send(self, data_packet, session: SessionBase, **kwargs):
        pass

    def process(self, stream: StreamBase, **kwargs):
        pass

    @classmethod
    def load(cls, obj_id, **kwargs):
        return NodeTest(_id=obj_id)


class PipeTest(ZeroPipe):
    def push(self, data_packet, session: SessionBase, **kwargs):
        pass

    def get_stream(self, session: SessionBase):
        pass


class TestZeroNetwork:
    @pytest.fixture
    def nodes_list(self):
        return [NodeTest(_id="node{}".format(i)) for i in range(10)]

    @pytest.fixture
    def input_pipes_list(self):
        return [
            PipeTest(ZeroNode.IN, NodeTest(_id="node1")),
            PipeTest(ZeroNode.IN, NodeTest(_id="node2")),
            PipeTest(ZeroNode.IN, NodeTest(_id="node3")),
        ]

    @pytest.fixture
    def output_pipes_list(self):
        return [
            PipeTest(NodeTest(_id="node1"), ZeroNode.OUT),
            PipeTest(NodeTest(_id="node2"), ZeroNode.OUT),
            PipeTest(NodeTest(_id="node3"), ZeroNode.OUT),
        ]

    @pytest.fixture
    def pipes_list(self, input_pipes_list, output_pipes_list):
        return (
            [
                PipeTest(
                    NodeTest(_id="node{}".format(i)), NodeTest(_id="node{}".format(j))
                )
                for i in range(10)
                for j in range(i + 1)
            ]
            + input_pipes_list
            + output_pipes_list
        )

    def test_create_without_args(self):
        network = ZeroNetwork()
        assert len(network.pipes) == 0

    def test_create_with_pipes(self, pipes_list):
        network = ZeroNetwork(pipes_list)
        assert list(network.pipes.values()) == pipes_list

    def test_add_pipes(self, pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)
        assert list(network.pipes.values()) == pipes_list

    def test_remove_pipes(self, pipes_list):
        network = ZeroNetwork()
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)
        network.add_pipes(*pipes_list)
        network.remove_pipes(*pipes_list1)

        assert list(network.pipes.values()) == list(pipes_list2)

    def test_pipes_map(self, pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)

        pipes_map = network.get_pipes_map()

        test_pipes_map = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )

        for pipe in pipes_list:
            node_a = pipe.node_a.id if not isinstance(pipe.node_a, str) else pipe.node_a
            node_b = pipe.node_b.id if not isinstance(pipe.node_b, str) else pipe.node_b
            test_pipes_map[node_a][node_b][pipe.id] = pipe

        assert pipes_map == test_pipes_map

    def test_reverse_pipes_map(self, pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)

        pipes_map = network.get_pipes_map(reverse=True)

        test_pipes_map = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: None))
        )

        for pipe in pipes_list:
            node_a = pipe.node_a.id if not isinstance(pipe.node_a, str) else pipe.node_a
            node_b = pipe.node_b.id if not isinstance(pipe.node_b, str) else pipe.node_b
            test_pipes_map[node_b][node_a][pipe.id] = pipe

        assert pipes_map == test_pipes_map

    def test_input_pipes(self, pipes_list, input_pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)

        assert list(network.input_pipes) == input_pipes_list

    def test_output_pipes(self, pipes_list, output_pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)

        assert list(network.output_pipes) == output_pipes_list

    def test_input_nodes(self, pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)

        assert list(network.input_nodes) == [
            pipe.node_b for pipe in pipes_list if pipe.node_a == ZeroNode.IN
        ]

    def test_output_nodes(self, pipes_list):
        network = ZeroNetwork()
        network.add_pipes(*pipes_list)

        assert list(network.input_nodes) == [
            pipe.node_a for pipe in pipes_list if pipe.node_b == ZeroNode.OUT
        ]

    def test_eq_network(self, pipes_list):
        network_a = ZeroNetwork(pipes_list)
        network_b = network_a.copy()

        assert id(network_a) != id(network_b)
        assert network_a == network_b

    def test_eq_similar_network(self, pipes_list):
        network_a = ZeroNetwork(pipes_list)
        network_b = ZeroNetwork(list(pipes_list))

        assert id(network_a) != id(network_b)
        assert network_a.id != network_b.id
        assert network_a == network_b

    def test_neq_network(self, pipes_list):
        first_batch, second_batch = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(first_batch)
        network_b = ZeroNetwork(second_batch)

        assert network_a != network_b

    def test_add_network(self, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a + network_b

        assert set(network_c.pipes) == set(network_a.pipes) | set(network_b.pipes)

    def test_iadd_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a.copy()
        network_c += network_b

        assert set(network_c.pipes) == set(network_a.pipes) | set(network_b.pipes)

    def test_sub_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2, cross=True)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a - network_b

        assert set(network_c.pipes) == set(network_a.pipes) - set(network_b.pipes)

    def test_isub_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a.copy()
        network_c -= network_b

        assert set(network_c.pipes) == set(network_a.pipes) - set(network_b.pipes)

    def test_and_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2, cross=True)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a & network_b

        assert set(network_c.pipes) == set(network_a.pipes) & set(network_b.pipes)

    def test_iand_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a.copy()
        network_c &= network_b

        assert set(network_c.pipes) == set(network_a.pipes) & set(network_b.pipes)

    def test_or_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a | network_b

        assert set(network_c.pipes) == set(network_a.pipes) | set(network_b.pipes)

    def test_ior_network(self, nodes_list, pipes_list):
        pipes_list1, pipes_list2 = _split_lists(pipes_list, 2)

        network_a = ZeroNetwork(pipes_list1)
        network_b = ZeroNetwork(pipes_list2)

        network_c = network_a.copy()
        network_c |= network_b

        assert set(network_c.pipes) == set(network_a.pipes) | set(network_b.pipes)
