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

from contextlib import contextmanager
from unittest import mock

import pytest

from tethys.core.exceptions import TethysSessionClosed, TethysRONotFound
from tethys.core.networks.network_zero import ZeroNetwork
from tethys.core.nodes.node_zero import ZeroNode
from tethys.core.nodes.operators.operator_base import OperatorBase
from tethys.core.pipes import ZeroPipe
from tethys.core.pipes.filters.filter_function import FNFilter
from tethys.core.sessions.sess_zero import ZeroSession
from tethys.core.streams.stream_zero import ZeroStream
from tethys.core.transports.connectors.connector_base import ConnectorBase
from tethys.core.transports.transport_zero import ZeroTransport


def load(*_, **__):
    raise TethysRONotFound()


class MockOperator(OperatorBase):
    def process(self, *args, **kwargs):
        pass


class MockNode(ZeroNode):
    def __init__(self, **kwargs):
        operator = MockOperator()
        super().__init__(operator, **kwargs)


class MockConnector(ConnectorBase):
    def connect(self, channel_id: str, *args, **kwargs):
        pass


class MockSession(ZeroSession):
    pass


class MockNetwork(ZeroNetwork):
    pass


class TestZeroPipe:

    # set_transport_factory

    def test_set_transport_factory_and_create_pipe(self):
        node_a, node_b = MockNode(), MockNode()

        transport = ZeroTransport(MockConnector())
        transport_factory = mock.MagicMock(side_effect=lambda *_, **__: transport)

        ZeroPipe.set_transport_factory(transport_factory)

        pipe = ZeroPipe(node_a, node_b)

        assert ZeroPipe._transport_factory == transport_factory
        assert pipe.transport == transport
        ZeroPipe._transport_factory.assert_called_once_with(pipe)

    def test_set_transport_factory_as_transport(self):
        node_a, node_b = MockNode(), MockNode()
        pipe = ZeroPipe(node_a, node_b)
        transport = ZeroTransport(MockConnector())

        pipe.set_transport_factory(transport)

        assert pipe._transport_factory() == transport

    def test_transport_factory_context(self):
        node_a, node_b = MockNode(), MockNode()
        pipe = ZeroPipe(node_a, node_b)
        transport = mock.MagicMock()

        prev_method = pipe._transport_factory

        with pipe.transport_factory_context(transport):
            assert pipe._transport_factory == transport

        assert pipe._transport_factory == prev_method

    # filter_data_packet

    def test_filter_data_packet_empty(self):
        node_a, node_b = MockNode(), MockNode()
        session_mock = mock.MagicMock()
        pipe = ZeroPipe(node_a, node_b, filters=[])

        assert pipe.filter_data_packet(..., session_mock)

    def test_filter_data_packet_true(self):
        node_a, node_b = MockNode(), MockNode()
        session_mock = mock.MagicMock()

        def f1(data_packet, *_, **__):
            return data_packet

        def f2(data_packet, *_, **__):
            return data_packet / 2

        pipe = ZeroPipe(
            node_a, node_b, filters=[FNFilter(f1), FNFilter(f2)], filters_threshold=0.5
        )

        assert pipe.filter_data_packet(1, session_mock) is True

    def test_filter_data_packet_false(self):
        node_a, node_b = MockNode(), MockNode()
        session_mock = mock.MagicMock()

        def f1(data_packet, *_, **__):
            return data_packet

        def f2(data_packet, *_, **__):
            return data_packet / 2

        pipe = ZeroPipe(
            node_a, node_b, filters=[FNFilter(f1), FNFilter(f2)], filters_threshold=1.1
        )

        assert pipe.filter_data_packet(2, session_mock) is False

    # get_stream

    def test_get_stream_exists(self):
        node_a, node_b = MockNode(), MockNode()
        session_mock = mock.MagicMock(spec=ZeroSession)
        session_mock.id = "1"
        session_mock.closed = False
        session_mock.closing_mode = None

        stream_mock = mock.MagicMock()
        stream_cls_mock = mock.MagicMock(side_effect=lambda *_, **__: stream_mock)
        stream_cls_mock.load = mock.MagicMock(side_effect=lambda *_, **__: stream_mock)

        pipe = ZeroPipe(node_a, node_b)

        @contextmanager
        def patch():
            old_load = ZeroStream.load
            old_new = ZeroStream.__new__

            try:
                ZeroStream.load = lambda *_, **__: stream_mock
                ZeroStream.__new__ = lambda *_, **__: stream_mock
                yield ZeroStream
            finally:
                ZeroStream.load = old_load
                ZeroStream.__new__ = old_new

        with patch():
            assert pipe.get_stream(session_mock) == stream_mock

    def test_get_stream_new_with_transport(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"
        session_mock.closed = False
        session_mock.closing_mode = None

        transport_mock = ZeroTransport(MockConnector())

        pipe = ZeroPipe(node_a, node_b, transport=transport_mock)

        ZeroStream.load = load
        ZeroStream.save = mock.MagicMock()

        stream = pipe.get_stream(session_mock)

        ZeroStream.save.assert_called_once_with(save_dependency=False)
        assert stream.transport == transport_mock

    def test_get_stream_new_without_transport(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"
        session_mock.closed = False
        session_mock.closing_mode = None

        transport_mock = ZeroTransport(MockConnector())

        def transport_factory(_):
            return transport_mock

        transport_factory_mock = mock.MagicMock(side_effect=transport_factory)

        ZeroPipe.set_transport_factory(transport_factory_mock)

        pipe = ZeroPipe(node_a, node_b)

        ZeroStream.load = load
        ZeroStream.save = mock.MagicMock()

        stream = pipe.get_stream(session_mock)

        ZeroStream.save.assert_called_once_with(save_dependency=False)
        ZeroPipe._transport_factory.assert_called_once_with(pipe)
        assert stream.transport == transport_mock

    def test_get_stream_new_when_sess_closed(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"
        session_mock.closed = True
        session_mock.closing_mode = None

        pipe = ZeroPipe(node_a, node_b)

        with pytest.raises(TethysSessionClosed):
            pipe.get_stream(session_mock)

    def test_get_stream_new_when_sess_hard_closing(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"
        session_mock.closed = False
        session_mock.closing_mode = ZeroSession.HARD_CLOSING_MODE

        pipe = ZeroPipe(node_a, node_b)

        with pytest.raises(TethysSessionClosed):
            pipe.get_stream(session_mock)

    # pull

    def test_pull(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"
        session_mock.closed = False
        session_mock.closing_mode = ZeroSession.HARD_CLOSING_MODE

        stream_mock = mock.MagicMock()
        stream_mock.read = mock.MagicMock(
            side_effect=lambda *_, **__: iter([("key", "value")])
        )

        def get_stream(_):
            return stream_mock

        pipe = ZeroPipe(node_a, node_b)
        pipe.get_stream = mock.MagicMock(side_effect=get_stream)

        assert next(pipe.pull(session_mock, test_kw=1)) == "value"

        pipe.get_stream.assert_called_once_with(session_mock)
        stream_mock.read.assert_called_once_with(test_kw=1)

    # push

    def test_push(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"

        stream_mock = mock.MagicMock()

        def get_stream(_):
            return stream_mock

        pipe = ZeroPipe(node_a, node_b)
        pipe.get_stream = mock.MagicMock(side_effect=get_stream)

        res = pipe.push(..., session_mock, test_kw=1)

        assert res is True
        pipe.get_stream.assert_called_once_with(session_mock)
        stream_mock.write.assert_called_once_with(..., many=False, test_kw=1)

    def test_push_filter_return_false(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"

        stream_mock = mock.MagicMock()

        def get_stream(_):
            return stream_mock

        def lambda_null(*_, **__):
            return 0

        pipe = ZeroPipe(node_a, node_b, filters=[FNFilter(lambda_null)])
        pipe.get_stream = mock.MagicMock(side_effect=get_stream)

        res = pipe.push(..., session_mock, test_kw=1)

        assert res is False
        pipe.get_stream.assert_not_called()
        stream_mock.write.assert_not_called()

    def test_push_many(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"

        stream_mock = mock.MagicMock()

        def get_stream(_):
            return stream_mock

        pipe = ZeroPipe(node_a, node_b)
        pipe.get_stream = mock.MagicMock(side_effect=get_stream)

        res = pipe.push([...], session_mock, many=True, test_kw=1)

        assert res is True
        pipe.get_stream.assert_called_once_with(session_mock)
        stream_mock.write.assert_called_once_with([...], many=True, test_kw=1)

    def test_push_many_return_piece_of_data(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"

        stream_mock = mock.MagicMock()

        def get_stream(_):
            return stream_mock

        def lambda_dummy(x, *_, **__):
            return x

        pipe = ZeroPipe(
            node_a, node_b, filters=[FNFilter(lambda_dummy)], filters_threshold=2
        )
        pipe.get_stream = mock.MagicMock(side_effect=get_stream)

        res = pipe.push(list(range(5)), session_mock, many=True, test_kw=1)

        assert res is True
        pipe.get_stream.assert_called_once_with(session_mock)
        stream_mock.write.assert_called_once_with(
            list(range(2, 5)), many=True, test_kw=1
        )

    def test_push_many_return_empty(self):
        node_a, node_b = MockNode(), MockNode()

        session_mock = MockSession(MockNetwork())
        session_mock._id = "1"

        stream_mock = mock.MagicMock()

        def get_stream(_):
            return stream_mock

        def lambda_null(*_, **__):
            return 0

        pipe = ZeroPipe(node_a, node_b, filters=[FNFilter(lambda_null)])
        pipe.get_stream = mock.MagicMock(side_effect=get_stream)

        res = pipe.push(list(range(5)), session_mock, many=True, test_kw=1)

        assert res is False
        pipe.get_stream.assert_not_called()
        stream_mock.write.assert_not_called()
