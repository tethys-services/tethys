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

import time
from unittest import mock
from unittest.mock import call

import pytest
from pytest import fixture

from tethys.core.streams.stream_zero import ZeroStream
from tethys.core.transports.connectors.connector_base import ConnectorBase
from tethys.core.transports.transport_zero import ZeroTransport


class MockConnector(ConnectorBase):
    def connect(self, channel_id: str, *args, **kwargs):
        return mock.MagicMock()


class TestZeroTransport:
    @staticmethod
    def teardown_method():
        ZeroTransport._connections = {}

    @fixture
    def connection(self):
        connector = mock.MagicMock()
        return connector

    @fixture
    def connector(self, connection):
        connector = MockConnector()
        connector.connect = mock.MagicMock(side_effect=lambda *_, **__: connection)
        return connector

    @fixture
    def transport(self, connector):
        transport = ZeroTransport(connector)

        def serializer(x):
            return str(x) + "_serialized"

        def deserializer(x):
            return str(x) + "_deserialized"

        transport.serializer = serializer
        transport.deserializer = deserializer
        return transport

    @fixture
    def stream(self):
        stream = mock.MagicMock(spec=ZeroStream)
        stream.id = "test"

        return stream

    # connect

    def test_connect_when_connected(self, transport, stream):
        ZeroTransport._connections = {stream.id: "connection"}
        assert transport.connect(stream) == "connection"
        assert transport.is_connected(stream)

    def test_connect_with_custom_connector_factory(self, transport, stream):
        connector = mock.MagicMock()
        connector.connect = mock.MagicMock()

        connector_factory = mock.MagicMock(side_effect=lambda *_, **__: connector)

        transport.connector = connector_factory
        transport.connect(stream, test_kw=1)

        assert transport.connector == connector_factory
        connector_factory.assert_called_once_with(transport, stream=stream)
        connector.connect.assert_called_with(stream.id, test_kw=1)
        assert transport.is_connected(stream)

    def test_connect_with_custom_connections_factory(self, transport, stream):
        connections_factory = mock.MagicMock()

        transport.connections_factory = connections_factory
        transport.connect(stream, test_kw=1)

        connections_factory.assert_called_once_with(transport.connector, stream=stream)
        assert transport.is_connected(stream)

    # disconnect

    def test_disconnect(self, transport, stream):
        conn = transport.connect(stream)
        transport.disconnect(stream)

        assert conn.close.call_count == 1
        assert not transport.is_connected(stream)

    # recv

    def test_recv_closed(self, transport, stream):
        conn = transport.connect(stream)
        stream.closed = True

        result = transport.recv(stream)

        assert result is None
        assert conn.recv_iter.call_count == 1
        conn.recv_iter.__next__.assert_not_called()

    def test_recv_none(self, transport, stream):
        def _iter_next():
            return None

        iterator = mock.MagicMock()
        iterator.__next__ = mock.MagicMock(side_effect=_iter_next)

        stream.closed = False

        conn = transport.connect(stream)
        conn.recv_iter = mock.MagicMock(side_effect=lambda: iterator)

        result = transport.recv(stream)

        assert result is None
        assert iterator.__next__.call_count == 1
        assert conn.recv_iter.call_count == 1

    def test_recv_stop_wait(self, transport, stream):
        def _iter_next():
            return None

        iterator = mock.MagicMock()
        iterator.__next__ = mock.MagicMock(side_effect=_iter_next)

        stream.closed = False

        conn = transport.connect(stream)
        conn.recv_iter = mock.MagicMock(side_effect=lambda: iterator)

        result = transport.recv(stream)

        assert result is None
        assert iterator.__next__.call_count == 1
        assert conn.recv_iter.call_count == 1

    def test_recv_stop_wait_0(self, transport, stream):
        def _iter_next():
            raise StopIteration

        iterator = mock.MagicMock()
        iterator.__next__ = mock.MagicMock(side_effect=_iter_next)

        stream.closed = False

        conn = transport.connect(stream)
        conn.recv_iter = mock.MagicMock(side_effect=lambda: iterator)

        result = transport.recv(stream, wait_timeout=0)

        assert result is None
        assert iterator.__next__.call_count == 1
        assert conn.recv_iter.call_count == 1

    def test_recv_wait_1(self, transport, stream):
        counter = {"_iter_next": 0}

        number = 5

        def _iter_next():
            time.sleep(1 / number)

            counter["_iter_next"] += 1

            if counter["_iter_next"] < number:
                raise StopIteration

            return 1, "data"

        iterator = mock.MagicMock()
        iterator.__next__ = mock.MagicMock(side_effect=_iter_next)

        stream.closed = False

        conn = transport.connect(stream)
        conn.recv_iter = mock.MagicMock(side_effect=lambda: iterator)

        transport.RECV_DELAY = 0
        result = transport.recv(stream, wait_timeout=1)

        iterator.__next__.assert_has_calls([call()] * number)
        conn.recv_iter.assert_has_calls([call()] * number)
        assert result == (1, "data_deserialized")

    def test_recv_timeout(self, transport, stream):
        number = 5

        def _iter_next():
            time.sleep(1 / number)
            raise StopIteration

        iterator = mock.MagicMock()
        iterator.__next__ = mock.MagicMock(side_effect=_iter_next)

        stream.closed = False

        conn = transport.connect(stream)
        conn.recv_iter = mock.MagicMock(side_effect=lambda: iterator)

        transport.RECV_DELAY = 0
        result = transport.recv(stream, wait_timeout=1)

        iterator.__next__.assert_has_calls([call()] * number)
        conn.recv_iter.assert_has_calls([call()] * number)
        assert result is None

    # send

    def test_send_without_connection(self, transport, stream):
        test_data = "test data"

        with pytest.raises(KeyError):
            transport.send(stream, test_data)

    def test_send(self, transport, stream):
        test_data = "test data"

        conn = transport.connect(stream)
        transport.send(stream, test_data, test_kw=1)

        conn.send.assert_called_once_with(test_data + "_serialized", test_kw=1)

    # ack

    def test_ack(self, transport, stream):
        message_key = "test ket"

        conn = transport.connect(stream)
        transport.ack(stream, message_key, test_kw=1)

        conn.ack.assert_called_once_with(message_key, test_kw=1)
