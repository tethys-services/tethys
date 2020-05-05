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

from collections import OrderedDict
from typing import Iterable, Union, Iterator, Dict, Any

from tethys.core.networks.network_base import NetworkBase
from tethys.core.nodes.node_zero import ZeroNode
from tethys.core.pipes.pipe_zero import ZeroPipe
from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject
from tethys.utils.iterable import flat_iter


class ZeroNetwork(ZeroRegistrableObject, NetworkBase):
    """
    The Network entity class of the Zero generation.
    The ZeroNetwork is a container of the Pipes.

    **Example:**
        .. code-block:: python

            pipe1 = ZeroPipe(
                node_a=node1,
                node_b=node2
            )

            pipe2 = ZeroPipe(
                node_a=node2,
                node_b=node1
            )

            pipe3 = ZeroPipe(
                node_a=node3,
                node_b=node1
            )

            pipe4 = ZeroPipe(
                node_a=node3,
                node_b=node2
            )

            network_template = ZeroNetwork([pipe1, pipe2])

            network = ZeroNetwork()
            network.add_pipes(pipe3, pipe4)

            result_network = network_template + network

    """

    CLASS_PATH = "/networks/"
    ":class:`ZeroNetwork` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "pipes_list": {
            "type": ["list"],
            "valuesrules": {"type": "string"},
            "nullable": True,
            "default": [],
        },
    }
    ":class:`ZeroNetwork` fields validators"

    def __init__(
        self,
        *pipes: Union[Iterable[Union["ZeroPipe", str]], Union["ZeroPipe", str]],
        **kwargs
    ):
        """

        :param pipes: list of args of the pipes (str or PipeZero instances) - can be empty
        :type pipes: Iterable[Union[ZeroPipe, str]
        """

        self.pipes_list = []

        if pipes:
            self.add_pipes(*pipes)

    @property
    def pipes(self) -> Dict[str, ZeroPipe]:
        return OrderedDict(
            (pipe_id, ZeroPipe.load(pipe_id)) for pipe_id in self.pipes_list
        )

    @property
    def input_nodes(self) -> Iterator["ZeroNode"]:
        """
        It returns `input nodes`

        Example:
            <in> ---> **Node1** ---> Node2 ---> <out>

            **Node1** - input node

        :return: list of the input nodes
        :rtype: Iterable[ZeroNode]
        """

        pipes_map = self.get_pipes_map()

        return iter(
            list(p_dict.values())[0].node_b
            for p_dict in pipes_map.get(ZeroNode.IN, {}).values()
            if p_dict
        )

    @property
    def output_nodes(self) -> Iterator["ZeroNode"]:
        """
        It returns `output nodes`

        Example:
            <in> ---> Node1 ---> **Node2** ---> <out>

            **Node2** - output node (because --> <out>)

        :return: list of the output nodes
        :rtype: Iterable[ZeroNode]
        """

        reversed_pipes_map = self.get_pipes_map(reverse=True)

        return iter(
            list(p_dict.values())[0].node_a  # The first pipe between node_a and <out>
            for p_dict in reversed_pipes_map.get(ZeroNode.OUT, {}).values()
            if p_dict
        )

    @property
    def input_pipes(self) -> Iterator[ZeroPipe]:
        """
        It returns `input pipes`

        Example:
            <in> **--pipe1-->** N --pipe2--> N --pipe3--> <out>

            **pipe1** - input pipe

        :return: list of the input pipes
        :rtype: Iterable[ZeroPipe]
        """

        pipes_map = self.get_pipes_map()

        return iter(
            flat_iter(
                [
                    list(p_dict.values())
                    for p_dict in pipes_map.get(ZeroNode.IN, {}).values()
                    if p_dict
                ]
            )
        )

    @property
    def output_pipes(self) -> Iterator[ZeroPipe]:
        """
        It returns `input pipes`

        Example:
            <in> --pipe1--> N --pipe2--> N **--pipe3-->** <out>  **<--pipe4--** N

            **pipe3** and **pipe4** - output pipes

        :return: list of the output pipes
        :rtype: Iterable[ZeroPipe]
        """

        reversed_pipes_map = self.get_pipes_map(reverse=True)

        return iter(
            flat_iter(
                list(p_dict.values())
                for p_dict in reversed_pipes_map.get(ZeroNode.OUT, {}).values()
                if p_dict
            )
        )

    def get_forward_pipes(
        self, pipe_or_node: Union[ZeroNode, ZeroPipe]
    ) -> Iterator[ZeroPipe]:
        """
        Get all pipes that go after the `pipe_or_node` instance.

        Example:
            <in> --p1--> N1 --p2--> N2 --p3--> <out>

            If p1 or N1 - target instance (`pipe_or_node`) then p2- forward pipe

        :param pipe_or_node: specify target pipe or node
        :type pipe_or_node: Union[ZeroNode, ZeroPipe]
        :return: all pipes after the `pipe_or_node`
        :rtype: Iterator[ZeroPipe]
        """
        pipes_map = self.get_pipes_map()

        if isinstance(pipe_or_node, ZeroPipe):
            node = pipe_or_node.node_b
        elif isinstance(pipe_or_node, ZeroNode):
            node = pipe_or_node
        else:
            raise ValueError("Bad 'pipe_or_node' argument type")

        if isinstance(node, str):
            return []

        return iter(
            flat_iter(
                list(p_dict.values())
                for p_dict in pipes_map.get(node.id, {}).values()
                if p_dict
            )
        )

    def get_backward_pipes(
        self, pipe_or_node: Union[ZeroNode, ZeroPipe]
    ) -> Iterator[ZeroPipe]:
        """
        Get all pipes that go after the `pipe_or_node` instance.

        Example:
            <in> --p1--> N1 --p2--> N2 --p4--> <out>

            If N1 or p2 - target instance (`pipe_or_node`) then p1 - backward pipe

        :param pipe_or_node: specify target pipe or node
        :type pipe_or_node: Union[ZeroNode, ZeroPipe]
        :return: all pipes before the `pipe_or_node`
        :rtype: Iterator[ZeroPipe]
        """

        reversed_pipes_map = self.get_pipes_map(reverse=True)

        if isinstance(pipe_or_node, ZeroPipe):
            node = pipe_or_node.node_a
        elif isinstance(pipe_or_node, ZeroNode):
            node = pipe_or_node
        else:
            raise ValueError("Bad 'pipe_or_node' argument type")

        if isinstance(node, str):
            return []

        return flat_iter(
            list(p_dict.values())
            for p_dict in reversed_pipes_map.get(node.id, {}).values()
            if p_dict
        )

    def get_pipes_map(
        self, reverse: bool = False, **kwargs
    ) -> Dict[str, Dict[str, Dict[str, Union[ZeroPipe, None]]]]:
        """
        It returns `pipes map` like 3d array

        :param reverse: if true then 3d array -> map["node_b_id"]["node_a_id"]["pipe_id"]
        :type reverse: bool
        :return: return 3d array -> map["node_a_id"]["node_b_id"]["pipe_id"] = ZeroPipe()
        :rtype: Dict[str, Dict[str, Dict[str, ZeroPipe]]]
        """

        pipes_map = (
            OrderedDict()
        )  # type: Dict[str, Dict[str, Dict[str, Union[ZeroPipe, None]]]]

        def _set(node_1, node_2, pipe_obj):
            if node_1 not in pipes_map:
                pipes_map[node_1] = OrderedDict()
            if node_2 not in pipes_map[node_1]:
                pipes_map[node_1][node_2] = OrderedDict()

            pipes_map[node_1][node_2][pipe_obj.id] = pipe_obj

        for pipe in self.pipes.values():
            node_a = (
                pipe.node_a.id
                if isinstance(pipe.node_a, ZeroNode)
                else str(pipe.node_a)
            )
            node_b = (
                pipe.node_b.id
                if isinstance(pipe.node_b, ZeroNode)
                else str(pipe.node_b)
            )

            if reverse:
                _set(node_b, node_a, pipe)
            else:
                _set(node_a, node_b, pipe)

        return pipes_map

    def add_pipes(
        self, *pipes: Union[Iterable[Union[ZeroPipe, str]], Union[ZeroPipe, str]]
    ):
        """
        It adds pipes to the ZeroNetwork instance

        :param pipes: list of args of the pipes (str or ZeroPipe instances)
        :type pipes: Iterable[Union[ZeroPipe, str]
        """

        assert pipes, "`pipes` can't be empty"

        for pipe in flat_iter(pipes, depth=1):
            if isinstance(pipe, str):
                pipe = ZeroPipe.load(pipe)
            elif not isinstance(pipe, ZeroPipe):
                raise ValueError("'{}' is not PipeBase instance")

            if pipe.id in self.pipes_list:
                self.pipes_list.remove(pipe.id)

            self.pipes_list.append(pipe.id)

    def remove_pipes(
        self, *pipes: Union[Iterable[Union["ZeroPipe", str]], Union["ZeroPipe", str]]
    ):
        """
        It removes pipes from the Network

        :param pipes: list of args of the pipes (str or ZeroPipe instances)
        :type pipes: Iterable[Union[ZeroPipe, str]]
        """

        for pipe in pipes or list(self.pipes_list):
            if isinstance(pipe, str):
                pipe = ZeroPipe.load(pipe)
            elif not isinstance(pipe, ZeroPipe):
                raise ValueError("'{}' is not PipeBase instance")

            try:
                self.pipes_list.remove(pipe.id)
            except ValueError:
                continue

    def save(self, save_dependency: bool = True, **kwargs):
        obj = super().save(save_dependency=save_dependency, **kwargs)

        # save pipes from the dict
        if save_dependency:
            for pipe in self.pipes.values():
                pipe.save(save_dependency=True)

        return obj

    def __eq__(self, other: Any):
        if isinstance(other, ZeroNetwork):
            return self.pipes_list == other.pipes_list
        return super().__eq__(other)

    def __ne__(self, other: Any):
        if isinstance(other, ZeroNetwork):
            return self.pipes_list != other.pipes_list
        return True

    def __add__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        graph_copy = self.copy()
        graph_copy.add_pipes(other.pipes_list)
        return graph_copy

    def __iadd__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        self.add_pipes(other.pipes_list)
        return self

    def __sub__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        graph_copy = self.copy()
        graph_copy.remove_pipes(*other.pipes_list)
        return graph_copy

    def __isub__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        self.remove_pipes(*other.pipes_list)
        return self

    def __and__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        pipes = []

        for pipe_id in self.pipes_list:
            if pipe_id in other.pipes_list:
                pipes.append(pipe_id)

        return self.__class__(pipes)

    def __iand__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        pipes = []

        for pipe_id in self.pipes_list:
            if pipe_id in other.pipes_list:
                pipes.append(pipe_id)

        self.remove_pipes()
        if pipes:
            self.add_pipes(*pipes)

        return self

    def __or__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        return self.__add__(other)

    def __ior__(self, other: "ZeroNetwork") -> "ZeroNetwork":
        return self.__iadd__(other)
