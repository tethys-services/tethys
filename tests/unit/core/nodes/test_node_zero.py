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

from unittest import mock

import pytest
from pytest import fixture

from tethys.core.nodes import ZeroNode
from tethys.core.nodes.operators.operator_base import OperatorBase


def side_effect_process(data_packet, *_, **kwargs):
    if data_packet is None:
        return None
    if data_packet == "exception":
        raise ValueError()
    return "TEST {}".format(data_packet)


class MockOperator(OperatorBase):
    def process(self, *args, **kwargs):
        pass


class MockNode(ZeroNode):
    def __init__(self, **kwargs):
        operator = MockOperator()
        operator.process = mock.MagicMock(side_effect=side_effect_process)
        super().__init__(operator, **kwargs)


class TestZeroNode:
    @fixture
    def pipe_mock(self):
        return mock.MagicMock()

    @fixture
    def pipes_map_mock(self, pipe_mock):
        pipes_map_mock = mock.MagicMock()
        pipes_map_mock.__getitem__ = mock.MagicMock(
            return_value={
                "node_b_1": {"pipe_1": pipe_mock, "pipe_2": pipe_mock},
                "node_b_2": {"pipe_3": pipe_mock},
            }
        )

        return pipes_map_mock

    @fixture
    def network_mock(self, pipes_map_mock):
        network_mock = mock.MagicMock()
        network_mock.get_pipes_map = mock.MagicMock(return_value=pipes_map_mock)

        return network_mock

    @fixture
    def session_mock(self, network_mock):
        session_mock = mock.MagicMock()
        session_mock.network = network_mock
        session_mock.closing_mode = None
        session_mock.closed = False

        return session_mock

    @fixture
    def stream_read_mock(self):
        return mock.MagicMock(return_value=enumerate(["test1", "test2", "test3", None]))

    @fixture
    def stream_read_mock_with_exception(self):
        return mock.MagicMock(
            return_value=enumerate(["test1", "test2", "test3", None, "exception"])
        )

    @fixture
    def stream_mock(self, stream_read_mock, session_mock):
        stream_mock = mock.MagicMock()
        stream_mock.session = session_mock
        stream_mock.read = stream_read_mock
        stream_mock.closed = False

        return stream_mock

    @fixture
    def stream_mock_with_exception(self, stream_read_mock_with_exception, session_mock):
        stream_mock = mock.MagicMock()
        stream_mock.session = session_mock
        stream_mock.read = stream_read_mock_with_exception
        stream_mock.closed = False

        return stream_mock

    def test_process(self, stream_mock, pipe_mock):
        node = MockNode()
        send_mock = mock.MagicMock()
        node.send = send_mock

        node.process(stream_mock)

        stream_mock.read.assert_called_once_with(wait_timeout=None)

        assert node.operator.process.call_count == 4

        node.operator.process.assert_has_calls(
            [
                mock.call("test{}".format(i + 1), stream_mock, message_key=i)
                for i in range(3)
            ]
            + [mock.call(None, stream_mock, message_key=3)]
        )

        assert send_mock.call_count == 3
        send_mock.assert_has_calls(
            [
                mock.call("TEST test{}".format(i + 1), stream_mock.session)
                for i in range(3)  # for 3 data_packets (not None)
            ]
        )

    def test_process_with_exception(self, stream_mock_with_exception, pipe_mock):
        stream_mock = stream_mock_with_exception

        node = MockNode()
        send_mock = mock.MagicMock()
        node.send = send_mock

        with pytest.raises(ValueError):
            node.process(stream_mock)

        stream_mock.read.assert_called_once_with(wait_timeout=None)

        assert node.operator.process.call_count == 5
        assert send_mock.call_count == 3

    def test_send_in_process(self, stream_mock, pipe_mock):
        node = MockNode()
        node.process(stream_mock)

        assert stream_mock.session.network.get_pipes_map.call_count == 3
        stream_mock.session.network.get_pipes_map.assert_has_calls([mock.call()] * 3)

        assert pipe_mock.push.call_count == 9
        pipe_mock.push.assert_has_calls(
            [
                mock.call("TEST test{}".format(i + 1), stream_mock.session, many=False)
                for i in range(3)  # for 3 data_packets (not None)
                for _ in range(3)  # for 3 pipes in network
            ]
        )
