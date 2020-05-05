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

import signal
import time
from contextlib import ContextDecorator
from functools import partial
from multiprocessing.pool import ThreadPool
from typing import Any
from unittest import mock
from unittest.mock import patch, call

from pytest import fixture
from tethys.core.networks.network_zero import ZeroNetwork
from tethys.core.nodes.node_zero import ZeroNode
from tethys.core.nodes.operators.operator_base import OperatorBase
from tethys.core.pipes.pipe_zero import ZeroPipe
from tethys.core.sessions.sess_zero import ZeroSession
from tethys.core.stations.station_zero import ZeroStation
from tethys.core.streams import ZeroStream


class MockOperator(OperatorBase):
    def process(
        self, data_packet: Any, stream: "ZeroStream", message_key: str = None, **kwargs
    ):
        pass


class MockSession(ZeroSession):
    def __init__(self):
        pass


class TimeoutContext(ContextDecorator):
    def __init__(self, seconds=2):
        self._seconds = seconds

    def _raise(self, signum, _):
        if signum == signal.SIGALRM:
            raise AssertionError("Test timeout ({} seconds)".format(self._seconds))

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._raise)
        signal.alarm(self._seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


class TestZeroStation:
    @fixture
    def session(self):
        session = mock.MagicMock(spec=ZeroSession)
        session.id = "test"
        return session

    @fixture
    def station(self):
        station = ZeroStation()
        station._stream_waiting_pool = mock.MagicMock()
        station._stream_processing_pool = mock.MagicMock()
        return station

    @fixture
    def stream(self, station):
        stream = mock.MagicMock()
        stream.station = station
        return stream

    # _try_stream

    def test_try_stream(self, station, stream):
        real_network = ZeroNetwork(_id="321")
        real_node = ZeroNode(MockOperator(), _id="312")
        real_pipe = ZeroPipe(real_node, real_node, _id="123")

        stream.is_busy = False
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.station = None
        stream.pipe = mock.MagicMock()
        stream.pipe.id = "123"
        stream.pipe.node_a = real_node
        stream.pipe.node_b = real_node
        stream.session = mock.MagicMock()
        stream.session.network = real_network

        station.pipes = [real_pipe]
        station.nodes_a = [real_node]
        station.nodes_b = [real_node]
        station.networks = [real_network]

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is True

        stream.lock_context.assert_called_once_with(
            blocking=station.stream_lock_blocking,
            lock_ttl=station.stream_lock_ttl,
            wait_timeout=station.stream_lock_ttl,
        )
        stream.redirect_to.assert_called_once_with(station)

    def test_try_stream_fail_with_lock(self, station, stream):
        context = mock.MagicMock()
        context.__enter__ = mock.MagicMock(return_value=False)

        stream.is_busy = False
        stream.lock_context = mock.MagicMock(return_value=context)

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock(spec=ZeroNode)

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_called_once_with(
            blocking=station.stream_lock_blocking,
            lock_ttl=station.stream_lock_ttl,
            wait_timeout=station.stream_lock_ttl,
        )
        stream.redirect_to.assert_not_called()

    def test_try_stream_fail_with_busy_state(self, station, stream):
        stream.is_busy = True
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.station = None
        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock(spec=ZeroNode)

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_called_once_with(
            blocking=station.stream_lock_blocking,
            lock_ttl=station.stream_lock_ttl,
            wait_timeout=station.stream_lock_ttl,
        )
        stream.redirect_to.assert_not_called()

    def test_try_stream_fail_with_virtual_out(self, station, stream):
        stream.is_busy = False
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = "<out>"

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_not_called()
        stream.redirect_to.assert_not_called()

    def test_try_stream_fail_filter_pipes(self, station, stream):
        stream.is_busy = False
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock(spec=ZeroNode)

        station.pipes = [mock.MagicMock(spec=ZeroPipe)]

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_not_called()
        stream.redirect_to.assert_not_called()

    def test_try_stream_fail_filter_nodes_a(self, station, stream):
        stream.is_busy = False
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.pipe = mock.MagicMock()
        stream.pipe.node_a = mock.MagicMock(spec=ZeroNode)

        station.pipes = [mock.MagicMock(spec=ZeroPipe)]

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_not_called()
        stream.redirect_to.assert_not_called()

    def test_try_stream_fail_filter_nodes_b(self, station, stream):
        stream.is_busy = False
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock(spec=ZeroNode)

        station.nodes_b = [mock.MagicMock(spec=ZeroNode)]

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_not_called()
        stream.redirect_to.assert_not_called()

    def test_try_stream_fail_filter_networks(self, station, stream):
        stream.is_busy = False
        stream.lock_context = mock.MagicMock()
        stream.redirect_to = mock.MagicMock()

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock(spec=ZeroNode)

        station.networks = [mock.MagicMock(spec=ZeroNetwork)]

        station.stream_lock_blocking = True
        station.stream_lock_ttl = 2

        assert station._try_stream(stream) is False

        stream.lock_context.assert_not_called()
        stream.redirect_to.assert_not_called()

    # _wait_stream

    def test_wait_stream(self, station, stream, session):
        from tethys.core.streams.stream_zero import ZeroStream

        ZeroStream.list = mock.MagicMock(return_value=[..., stream])

        shuffle = mock.MagicMock(side_effect=lambda x: x)

        station.sessions = [session]
        station.to_shuffle_stream = True
        station.heartbeat_fail_delay = 1

        station._try_stream = mock.MagicMock(side_effect=lambda x: x == stream)

        with patch("time.time", lambda: 2):
            with patch("random.shuffle", shuffle):
                result = station._wait_stream()

        assert result == stream
        ZeroStream.list.assert_called_once_with(
            list_filter={
                "closed": False,
                "heartbeat_ts<=": 1,
                "session->": [session.id],
            }
        )
        station._try_stream.assert_has_calls(
            [call(...), call(stream),]
        )
        assert shuffle.call_count == 1

    def test_wait_stream_none(self, station, stream, session):
        from tethys.core.streams.stream_zero import ZeroStream

        ZeroStream.list = mock.MagicMock(return_value=[...])

        station.sessions = []
        station.heartbeat_fail_delay = 1

        station._try_stream = mock.MagicMock(side_effect=lambda x: x == stream)

        with patch("time.time", lambda: 2):
            result = station._wait_stream()

        assert result is None
        ZeroStream.list.assert_called_once_with(
            list_filter={"closed": False, "heartbeat_ts<=": 1}
        )
        station._try_stream.assert_has_calls([call(...)])

    # _process_stream

    def test_process_stream(self, station, stream):
        station._process_stream_start = mock.MagicMock()
        station.stream_waiting_timeout = 0

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock()
        stream.pipe.node_b.process = mock.MagicMock()

        process = mock.MagicMock()
        process_cls = mock.MagicMock(side_effect=lambda *_, **__: process)
        event = mock.MagicMock()
        event_cls = mock.MagicMock(side_effect=lambda: event)

        with patch("multiprocessing.Process", process_cls):
            with patch("multiprocessing.Event", event_cls):
                station._process_stream(stream)

        process_cls.assert_called_once_with(
            target=station._process_worker, args=[stream, event],
        )
        assert process.start.call_count == 1
        assert station._processes == {stream: (process, event)}

    def test_process_stream_x2(self, station, stream):
        event = mock.MagicMock()
        event_cls = mock.MagicMock(side_effect=lambda: event)

        process = mock.MagicMock()
        process.is_alive = mock.MagicMock(side_effect=lambda: True)
        process_cls = mock.MagicMock(side_effect=lambda *_, **__: process)

        process_tuple = (process, event)

        station._processes[stream] = process_tuple

        station._process_stream_start = mock.MagicMock()
        station._stream_processing_pool = mock.MagicMock()
        station._stream_processing_pool.apply_async = mock.MagicMock()
        station.stream_waiting_timeout = 0

        stream.pipe = mock.MagicMock()
        stream.pipe.node_b = mock.MagicMock()

        with patch("multiprocessing.Process", process_cls):
            with patch("multiprocessing.Event", event_cls):
                station._process_stream(stream)

        process_cls.assert_not_called()
        station._stream_processing_pool.apply_async.assert_not_called()
        assert station._processes == {stream: process_tuple}

    # _spawn_stream_process

    def test_spawn_stream_process_worker(self, station, stream):
        delay = 0.12345
        counter = {"waiting_loop_iter": 0}

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != 0.12345:
                orig_sleep(sleep_delay)

        def wait_stream():
            counter["waiting_loop_iter"] += 1
            if counter["waiting_loop_iter"] >= 3:
                return stream

        station._stopped = False
        station._wait_stream = mock.MagicMock(side_effect=wait_stream)
        station._process_stream = mock.MagicMock()
        station.monitor_checks_delay = delay

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        with TimeoutContext():
            with patch("time.sleep", sleep):
                result = station._spawn_stream_process_worker()

        assert result == stream
        assert station._wait_stream.call_count == 3
        station._process_stream.assert_called_once_with(stream)
        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    def test_spawn_stream_process_worker_when_stopped(self, station, stream):
        delay = 0.12345
        counter = {"waiting_loop_iter": 0}

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != delay:
                orig_sleep(sleep_delay)

        def wait_stream():
            counter["waiting_loop_iter"] += 1
            if counter["waiting_loop_iter"] >= 3:
                station._stopped = True

        station._stopped = False
        station._wait_stream = mock.MagicMock(side_effect=wait_stream)
        station._process_stream = mock.MagicMock()
        station.monitor_checks_delay = delay

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        with TimeoutContext():
            with patch("time.sleep", sleep):
                result = station._spawn_stream_process_worker()

        assert result is None
        assert station._wait_stream.call_count == 3
        station._process_stream.assert_not_called()
        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    def test_spawn_stream_process(self, station):
        station._spawn_process_start = mock.MagicMock()
        station._stream_waiting_pool = mock.MagicMock()
        station._stream_waiting_pool.apply_async = mock.MagicMock(return_value=...)

        random_token = "12345"

        station._spawn_process_start()

        with patch("time.perf_counter", lambda: int(random_token)):
            with patch("functools.partial", lambda x, *_: x):
                station._spawn_stream_process()

        station._spawn_process_start.assert_has_calls([call(), call(random_token)])
        station._stream_waiting_pool.apply_async.assert_called_once_with(
            station._spawn_stream_process_worker,
            callback=station._spawn_process_result,
            error_callback=station._spawn_process_error,
        )
        assert station._processes_spawners == [random_token]

    # _start_loop

    def test_start_loop_when_closed(self, station):
        monotonic = mock.MagicMock(side_effect=lambda: 0)

        with TimeoutContext():
            with patch("time.monotonic", monotonic):
                station._start_loop()
        monotonic.assert_not_called()

    def test_start_loop_when_sessions_closed(self, station, session):
        station._stopped = False
        session.closed = True

        station.sessions = [session]
        monotonic = mock.MagicMock(side_effect=lambda: 0)

        with TimeoutContext():
            with patch("time.monotonic", monotonic):
                station._start_loop()
        monotonic.assert_not_called()

    def test_start_loop_spawn(self, station):
        delay = 0.71
        counter = {"loop_iter": 0}

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != delay:
                orig_sleep(sleep_delay)
                return

            assert counter["loop_iter"] < 4

            counter["loop_iter"] += 1
            if counter["loop_iter"] == 3:
                station._stopped = True

        def spawn():
            station._processes_spawners.append("test")

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        station._stopped = False
        station._spawn_stream_process = mock.MagicMock(side_effect=spawn)
        station.monitor_checks_delay = delay

        with TimeoutContext():
            with patch("time.sleep", sleep):
                station._start_loop()

        assert station._spawn_stream_process.call_count == 1
        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    def test_start_loop_stream_close(self, station, stream):
        delay = 0.71
        counter = {"loop_iter": 0}

        event = mock.MagicMock()
        process = mock.MagicMock()
        process.is_alive = mock.MagicMock(side_effect=lambda: False)
        process_tuple = (process, event)

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != delay:
                orig_sleep(sleep_delay)
                return

            assert counter["loop_iter"] < 4

            counter["loop_iter"] += 1
            if counter["loop_iter"] == 3:
                station._stopped = True

        def spawn():
            station._processes[stream] = process_tuple

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        station._stopped = False
        station._spawn_stream_process = mock.MagicMock(side_effect=spawn)
        station.monitor_checks_delay = delay
        station.update_min_delay = 0

        with TimeoutContext():
            with patch("time.sleep", sleep):
                station._start_loop()

        assert stream.close.call_count == 2
        assert station._spawn_stream_process.call_count == 3
        assert station._processes == {stream: process_tuple}
        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    def test_start_loop_stream_heartbeat(self, station, stream):
        delay = 0.71
        counter = {"loop_iter": 0}

        process = mock.MagicMock()
        process.is_alive = mock.MagicMock(side_effect=lambda: True)
        process_tuple = (process, "event")

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != delay:
                orig_sleep(sleep_delay)
                return

            assert counter["loop_iter"] < 4

            counter["loop_iter"] += 1
            if counter["loop_iter"] == 3:
                station._stopped = True

        def spawn():
            station._processes[stream] = process_tuple

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        station._spawn_stream_process = mock.MagicMock(side_effect=spawn)
        station._stopped = False
        station.monitor_checks_delay = delay
        station.update_min_delay = 0

        with TimeoutContext():
            with patch("time.sleep", sleep):
                station._start_loop()

        assert station._spawn_stream_process.call_count == 1
        assert station._processes == {stream: process_tuple}
        assert stream.close.call_count == 0
        assert stream.heartbeat.call_count == 2
        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    def test_start_loop_stream_error(self, station, stream):
        delay = 0.71
        counter = {"loop_iter": 0}

        process = mock.MagicMock()
        process.is_alive = mock.MagicMock(side_effect=lambda: True)
        process_tuple = (process, "event")

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != delay:
                orig_sleep(sleep_delay)
                return

            assert counter["loop_iter"] < 4

            counter["loop_iter"] += 1
            if counter["loop_iter"] == 3:
                station._stopped = True

        def spawn():
            stream.station = station
            station._processes[stream] = process_tuple

        def fake_heartbeat():
            raise RuntimeError

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        station._stopped = False
        station._spawn_stream_process = mock.MagicMock(side_effect=spawn)
        station.monitor_checks_delay = delay
        station.update_min_delay = 0

        stream.heartbeat = mock.MagicMock(side_effect=fake_heartbeat)

        with TimeoutContext():
            with patch("time.sleep", sleep):
                station._start_loop()

        assert station._spawn_stream_process.call_count == 3
        assert station._processes == {stream: process_tuple}
        assert stream.close.call_count == 0
        assert stream.heartbeat.call_count == 2
        assert stream.station is station

        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    def test_start_loop_streams_refresh(self, station, stream):
        delay = 0.71
        counter = {"loop_iter": 0, "stream_refresh": 0}

        process = mock.MagicMock()
        process.is_alive = mock.MagicMock(side_effect=lambda: True)
        process_tuple = (process, mock.MagicMock())

        sess1 = MockSession()
        sess1._id = 1
        sess1.closed = False
        sess1.refresh = mock.MagicMock()

        sess2 = mock.MagicMock(spec=ZeroSession)
        sess2.id = 2
        sess2.closed = False

        def sleep(orig_sleep, sleep_delay):
            if sleep_delay != delay:
                orig_sleep(sleep_delay)
                return

            assert counter["loop_iter"] < 4

            counter["loop_iter"] += 1
            if counter["loop_iter"] == 3:
                station._stopped = True

        def spawn():
            station._processes[stream] = process_tuple

        def refresh(**__):
            if counter["stream_refresh"] == 1:
                raise RuntimeError
            counter["stream_refresh"] += 1

        sleep = mock.MagicMock(side_effect=partial(sleep, time.sleep))

        station._stopped = False
        station._spawn_stream_process = mock.MagicMock(side_effect=spawn)
        station.monitor_checks_delay = delay
        station.update_min_delay = 0
        station.sessions = [sess1]

        stream.refresh = mock.MagicMock(side_effect=refresh)
        stream.session = sess2

        with TimeoutContext():
            with patch("time.sleep", sleep):
                station._start_loop()

        assert station._spawn_stream_process.call_count == 2
        assert station._processes == {stream: process_tuple}
        assert stream.close.call_count == 0
        assert stream.refresh.call_count == 2
        assert sess1.refresh.call_count == 3
        assert sess2.refresh.call_count == 1

        sleep.assert_has_calls(
            [call(delay), call(delay), call(delay),]
        )

    # start

    def test_start(self, station):
        station._add_signals = mock.MagicMock()
        station._start_loop = mock.MagicMock()
        station.stop = mock.MagicMock()

        station.start()

        assert isinstance(station._stream_waiting_pool, ThreadPool)
        assert station._add_signals.call_count == 1
        assert station._start_loop.call_count == 1
        assert station.stop.call_count == 1

    def test_start_when_process(self, station):
        station._stopped = False

        station.start()

        assert not isinstance(station._stream_waiting_pool, ThreadPool)

    # stop

    def test_stop(self, station):
        process_mock = mock.MagicMock()

        station._stopped = False
        station._processes_spawners = ["test"]
        station._processes = {"test": (process_mock, "event")}

        station.stop()

        assert station._stream_waiting_pool.terminate.call_count == 1
        assert process_mock.kill.call_count == 1
        assert station._processes_spawners == []
        assert station._processes == {}

    def test_stop_when_stopped(self, station):
        station.stop()

        station._stream_waiting_pool.terminate.assert_not_called()
        station._stream_processing_pool.terminate.assert_not_called()
