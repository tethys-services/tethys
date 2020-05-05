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
import gc
import platform
import time
from unittest import mock
from unittest.mock import patch, call

from pytest import fixture

from tethys.core.pipes.pipe_zero import ZeroPipe
from tethys.core.sessions.sess_zero import ZeroSession
from tethys.core.stations.station_zero import ZeroStation
from tethys.core.streams.stream_zero import ZeroStream
from tethys.core.transports.transport_zero import ZeroTransport


class MockTransport(ZeroTransport):
    def __init__(self):
        pass

    connect = mock.MagicMock()
    disconnect = mock.MagicMock()


class MockSession(ZeroSession):
    closing_mode = None

    def __init__(self):
        self._closed = False

    @property
    def closed(self):
        return self._closed


class MockStation(ZeroStation):
    def __init__(self):
        pass


class TestZeroStream:
    @staticmethod
    def teardown_method():
        MockTransport.connect.reset_mock()
        MockTransport.disconnect.reset_mock()

    @fixture
    def pipe(self):
        pipe = mock.MagicMock(spec=ZeroPipe)
        return pipe

    @fixture
    def session(self):
        session = MockSession()
        return session

    @fixture
    def transport(self):
        return MockTransport()

    @fixture
    def station(self):
        return MockStation()

    @fixture
    def stream(self, pipe, session, transport):
        return ZeroStream(pipe, session, transport)

    # init

    def test_init_with_transport_cb(self, pipe, session, transport):
        def get_transport(_):
            return transport

        get_transport = mock.MagicMock(side_effect=get_transport)

        stream = ZeroStream(pipe, session, get_transport)

        assert stream.transport == transport

    # conn context

    def test_new_connection_context(self, stream):
        with stream.connection_context():
            MockTransport.connect.assert_called_once_with(stream)
            MockTransport.disconnect.assert_not_called()
        MockTransport.disconnect.assert_called_once_with(stream)

    def test_old_connection_context(self, stream):
        MockTransport._connections[stream.id] = stream

        with stream.connection_context():
            MockTransport.connect.assert_not_called()
        MockTransport.disconnect.assert_not_called()

    # heartbeat

    def test_heartbeat_fail_delay(self, stream):
        assert stream.heartbeat_fail_delay == stream.DEFAULT_HEARTBEAT_FAIL_DELAY

        stream.station = mock.MagicMock(spec=ZeroStation)
        stream.station.heartbeat_fail_delay = 0
        assert stream.heartbeat_fail_delay == stream.DEFAULT_HEARTBEAT_FAIL_DELAY

        stream.station.heartbeat_fail_delay = 12345
        assert stream.heartbeat_fail_delay == 12345

    def test_busy_false(self, stream):
        stream.refresh = mock.MagicMock()
        stream.station = mock.MagicMock(spec=ZeroStation)
        stream.station.heartbeat_fail_delay = 1
        stream.heartbeat_ts = time.time() - 10

        assert stream.is_busy is False
        assert stream.refresh.call_count == 1

    def test_busy_true(self, stream):
        stream.refresh = mock.MagicMock()
        stream.station = mock.MagicMock(spec=ZeroStation)
        stream.station.heartbeat_fail_delay = 1000
        stream.heartbeat_ts = time.time()

        assert stream.is_busy is True
        assert stream.refresh.call_count == 1

    def test_heartbeat(self, stream):
        stream.save = mock.MagicMock()

        with patch("time.time", lambda: 12345):
            stream.heartbeat()

        assert stream.heartbeat_ts == 12345
        stream.save.assert_called_once_with(save_dependency=False)

    # open

    def test_open(self, stream):
        stream.save = mock.MagicMock()
        stream.closed = True

        assert stream.open() is stream
        assert stream.closed is False
        stream.save.assert_called_once_with(save_dependency=False)

    def test_open_no_commit(self, stream):
        stream.save = mock.MagicMock()
        stream.closed = True

        assert stream.open(save=False) is stream
        assert stream.closed is False
        stream.save.assert_not_called()

    # close

    def test_close(self, stream):
        stream.save = mock.MagicMock()

        assert stream.close() is stream
        assert stream.closed is True
        stream.save.assert_called_once_with(save_dependency=False)

    def test_close_no_commit(self, stream):
        stream.save = mock.MagicMock()

        assert stream.close(save=False) is stream
        assert stream.closed is True
        stream.save.assert_not_called()

    # read

    def test_read(self, stream):
        data = ["packet", 0, {}, "", None] + [None, "packet"] * 5
        result_data = list(filter(lambda x: x is not None, data))
        iter_data = iter(data)

        def recv_cb(*_, **__):
            try:
                return next(iter_data)
            except StopIteration:
                return ...

        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.recv = mock.MagicMock(side_effect=recv_cb)

        result = []

        for item in stream.read(test_kw=1):
            if item is ...:
                break
            result.append(item)

        if platform.python_implementation().lower() == "pypy":
            gc.collect()

        assert result == result_data
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1
        stream.transport.recv.assert_has_calls(
            [call(stream, wait_timeout=None, test_kw=1) for _ in data]
        )

    def test_read_n_packets(self, stream):
        iter_data = iter([None, "packet"] + ["packet"] * 10)

        def recv_cb(*_, **__):
            try:
                return next(iter_data)
            except StopIteration:
                return ...

        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.recv = mock.MagicMock(side_effect=recv_cb)

        result = []

        for item in stream.read(count=5, test_kw=1):
            if item is ...:
                break
            result.append(item)

        assert result == ["packet"] * 5
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1
        stream.transport.recv.assert_has_calls(
            [call(stream, wait_timeout=None, test_kw=1) for _ in range(6)]
        )

    def test_read_while_stream_open(self, stream):
        iter_data = iter(range(10))

        def recv_cb(*_, **__):
            try:
                return next(iter_data)
            except StopIteration:
                return ...

        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.recv = mock.MagicMock(side_effect=recv_cb)

        result = []

        for item in stream.read(test_kw=1):
            if item == 4:
                stream.closed = True

            if item is ...:
                break

            result.append(item)

        assert result == list(range(5))
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1
        stream.transport.recv.assert_has_calls(
            [call(stream, wait_timeout=None, test_kw=1) for _ in range(5)]
        )

    def test_read_while_sess_open(self, stream):
        stream.session._closed = True

        iter_data = iter([0, 1, 2, 3, None, 4])

        def recv_cb(*_, **__):
            try:
                return next(iter_data)
            except StopIteration:
                return ...

        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.recv = mock.MagicMock(side_effect=recv_cb)

        result = []

        for item in stream.read(test_kw=1):
            if item is ...:
                break

            result.append(item)

        assert result == list(range(4))
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1
        stream.transport.recv.assert_has_calls(
            [call(stream, wait_timeout=None, test_kw=1) for _ in range(5)]
        )

    def test_read_when_station_changed(self, stream, station):
        iter_data = iter(range(10))

        def recv_cb(*_, **__):
            try:
                return next(iter_data)
            except StopIteration:
                return ...

        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.recv = mock.MagicMock(side_effect=recv_cb)

        result = []

        for item in stream.read(test_kw=1):
            if item == 4:
                stream.station = station

            if item is ...:
                break

            result.append(item)

        assert result == list(range(5))
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1
        stream.transport.recv.assert_has_calls(
            [call(stream, wait_timeout=None, test_kw=1) for _ in range(5)]
        )

    def test_read_none(self, stream):
        iter_data = iter([None, "packet"] + ["packet"] * 10)

        def recv_cb(*_, **__):
            try:
                return next(iter_data)
            except StopIteration:
                return ...

        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.recv = mock.MagicMock(side_effect=recv_cb)

        result = []

        for item in stream.read(wait_timeout=1, test_kw=1):
            if item is ...:
                break
            result.append(item)

        assert result == []
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1
        stream.transport.recv.assert_called_once_with(stream, wait_timeout=1, test_kw=1)

    # write

    def test_write(self, stream):
        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.send = mock.MagicMock()

        stream.write("packet", test_kw=1)

        stream.transport.send.assert_called_once_with(stream, "packet", test_kw=1)
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1

    def test_write_many(self, stream):
        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.send = mock.MagicMock()

        stream.write("packet", many=True, test_kw=1)

        stream.transport.send.assert_has_calls(
            [call(stream, i, test_kw=1) for i in "packet"]
        )
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1

    def test_write_when_closed(self, stream):
        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.send = mock.MagicMock()
        stream.closed = True

        stream.write("packet", test_kw=1)

        stream.transport.send.assert_not_called()
        stream.connection_context.assert_not_called()
        connection_context.__enter__.assert_not_called()
        connection_context.__exit__.assert_not_called()

    def test_write_out(self, stream):
        connection_context = mock.MagicMock()
        stream.connection_context = mock.MagicMock(
            side_effect=lambda: connection_context
        )
        stream.transport.send = mock.MagicMock()
        stream.closed = True
        stream.pipe.node_b = "<out>"

        stream.write("packet", test_kw=1)

        stream.transport.send.assert_called_once_with(stream, "packet", test_kw=1)
        assert stream.connection_context.call_count == 1
        assert connection_context.__enter__.call_count == 1
        assert connection_context.__exit__.call_count == 1

    # ack

    def test_ack(self, stream):
        stream.transport.ack = mock.MagicMock()

        stream.ack("message", test_kw=1)

        stream.transport.ack.assert_called_once_with(stream, "message", test_kw=1)

    def test_ack_closed(self, stream):
        stream.closed = True
        stream.transport.ack = mock.MagicMock()

        stream.ack("message", test_kw=1)

        stream.transport.ack.assert_not_called()

    # redirect

    def test_redirect(self, stream, station):
        station.save = mock.MagicMock()
        station.stream_lock_ttl = 0

        stream.save = mock.MagicMock()

        stream.redirect_to(station)

        assert stream.station == station
        station.save.assert_called_once_with(save_dependency=False)
        stream.save.assert_called_once_with(save_dependency=False)

    # open/close context

    def test_context(self, stream):
        stream.open = mock.MagicMock()
        stream.close = mock.MagicMock()

        with stream:
            stream.open.assert_called_once_with(save=False)
            stream.close.assert_not_called()
        stream.close.assert_called_once_with(save=False)
