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

import functools
import logging
import multiprocessing
import os
import random
import signal
import time
from multiprocessing.pool import ThreadPool
from multiprocessing.synchronize import Event
from threading import Lock
from typing import Callable, List, Union, Tuple, Dict

from tethys.core.exceptions import TethysRuntimeError
from tethys.core.networks import NetworkBase
from tethys.core.nodes import NodeBase
from tethys.core.pipes import PipeBase
from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject
from tethys.core.sessions import SessionBase
from tethys.core.sessions.sess_zero import ZeroSession
from tethys.core.stations.station_base import StationBase
from tethys.core.streams import ZeroStream

log = logging.getLogger(__name__)


class ZeroStation(ZeroRegistrableObject, StationBase):
    """
    The Station entity class of the Zero generation.
    The ZeroStation is a worker that processes streams data.

    """

    CLASS_PATH = "/stations/"
    ":class:`ZeroStation` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "sessions": {
            "type": "list",
            "schema": {"type": ["string", "ZeroSession"]},
            "nullable": True,
            "default": [],
        },
        "networks": {
            "type": "list",
            "schema": {"type": ["string", "ZeroNetwork"]},
            "nullable": True,
            "default": [],
        },
        "pipes": {
            "type": "list",
            "schema": {"type": ["string", "ZeroPipe"]},
            "nullable": True,
            "default": [],
        },
        "nodes_a": {
            "type": "list",
            "schema": {"type": ["string", "ZeroNode"]},
            "nullable": True,
            "default": [],
        },
        "nodes_b": {
            "type": "list",
            "schema": {"type": ["string", "ZeroNode"]},
            "nullable": True,
            "default": [],
        },
        "to_shuffle_stream": {"type": "boolean", "nullable": False, "default": False,},
        "stream_lock_ttl": {"type": "float", "nullable": False, "default": 4,},
        "stream_lock_blocking": {
            "type": "boolean",
            "nullable": False,
            "default": False,
        },
        "stream_waiting_timeout": {"type": "float", "nullable": True, "default": None,},
        "max_processes_count": {"type": "integer", "nullable": False, "default": 1,},
        "monitor_checks_delay": {"type": "float", "nullable": False, "default": 1,},
        "refresh_min_delay": {"type": "float", "nullable": False, "default": 1,},
        "heartbeat_min_delay": {"type": "float", "nullable": False, "default": 10,},
        "heartbeat_fail_delay": {"type": "float", "nullable": False, "default": 60,},
        "process_start_callback": {
            "type": "Callable",
            "nullable": True,
            "default": None,
        },
        "process_stop_callback": {
            "type": "Callable",
            "nullable": True,
            "default": None,
        },
        "process_error_callback": {
            "type": "Callable",
            "nullable": True,
            "default": None,
        },
        "spawn_process_start_callback": {
            "type": "Callable",
            "nullable": True,
            "default": None,
        },
        "spawn_process_stop_callback": {
            "type": "Callable",
            "nullable": True,
            "default": None,
        },
        "spawn_process_error_callback": {
            "type": "Callable",
            "nullable": True,
            "default": None,
        },
    }
    ":class:`ZeroStation` fields validators"

    def __init__(
        self,
        sessions: List[SessionBase] = None,
        networks: List[NetworkBase] = None,
        pipes: List[PipeBase] = None,
        nodes_a: List[NodeBase] = None,
        nodes_b: List[NodeBase] = None,
        to_shuffle_stream: bool = False,
        stream_lock_ttl: float = 1,
        stream_lock_blocking: bool = False,
        stream_waiting_timeout: float = None,
        max_processes_count: int = 1,
        monitor_checks_delay: float = 1,
        update_min_delay: float = 1,
        heartbeat_fail_delay: float = 60,
        process_start_callback: Callable = None,
        process_stop_callback: Callable = None,
        process_error_callback: Callable = None,
        spawn_process_start_callback: Callable = None,
        spawn_process_stop_callback: Callable = None,
        spawn_process_error_callback: Callable = None,
        **kwargs  # for __new__ args, like '_id'
    ):
        """

        :param sessions: Sessions that will be processed in the station
        :type sessions: Iterable[ZeroSession]
        :param networks: Networks that will be processed in the station
        :type networks: Iterable[ZeroNetwork]
        :param pipes: Pipes that will be processed in the station
        :type pipes: Iterable[ZeroPipe]
        :param nodes_a: Input nodes (bode_a) that will be processed in the station
        :type nodes_a: Iterable[ZeroNode]
        :param nodes_b: Output nodes that will be processed in the station
        :type nodes_b: Iterable[ZeroNode]

        :param to_shuffle_stream: To shuffle streams list in the waiting process
        :type to_shuffle_stream: bool
        :param stream_lock_ttl: Stream lock timeout in the try_stream function
        :type stream_lock_ttl: float
        :param stream_lock_blocking: Block lock acquire in the try_stream function (affects the streams order)
        :type stream_lock_blocking: bool
        :param stream_waiting_timeout: How long do streams instances wait for data
        :type stream_waiting_timeout: float

        :param max_processes_count: The max count multiprocessing processes
        :type max_processes_count: int
        :param monitor_checks_delay: The delay between monitoring iterations
        :type monitor_checks_delay: float
        :param update_min_delay: The delay between iterations updates
        :type update_min_delay: float
        :param heartbeat_fail_delay: The timeout of the streams processes without heartbeats
        :type heartbeat_fail_delay: float

        :param process_start_callback: The callback called when streams processes start on the station
        :type process_start_callback: Callable
        :param process_stop_callback: The callback called when streams processes stop on the station
        :type process_stop_callback: Callable
        :param process_error_callback: The callback called when streams processes stop with an error
            on the station
        :type process_error_callback: Callable
        :param spawn_process_start_callback: The callback called when start streams loading
        :type spawn_process_start_callback: Callable
        :param spawn_process_stop_callback: The callback called when a stream is found
        :type spawn_process_stop_callback: Callable
        :param spawn_process_error_callback: The callback called when streams loading error caused
        :type spawn_process_error_callback: Callable

        """

        self.sessions = sessions or []
        self.networks = networks or []
        self.pipes = pipes or []
        self.nodes_a = nodes_a or []
        self.nodes_b = nodes_b or []

        self.to_shuffle_stream = to_shuffle_stream
        self.stream_lock_ttl = stream_lock_ttl
        self.stream_lock_blocking = stream_lock_blocking
        self.stream_waiting_timeout = stream_waiting_timeout

        self.max_processes_count = max_processes_count or 1
        self.monitor_checks_delay = monitor_checks_delay
        self.update_min_delay = update_min_delay
        self.heartbeat_fail_delay = heartbeat_fail_delay

        self.process_start_callback = process_start_callback
        self.process_stop_callback = process_stop_callback
        self.process_error_callback = process_error_callback

        self.spawn_process_start_callback = spawn_process_start_callback
        self.spawn_process_stop_callback = spawn_process_stop_callback
        self.spawn_process_error_callback = spawn_process_error_callback

        self._stopped = True
        self._processes = (
            {}
        )  # type: Dict[ZeroStream, Tuple[multiprocessing.Process, Event]]
        self._processes_spawners = []  # type: List[str]
        self._stream_waiting_pool = None
        self._next_update = 0

        self._station_threads_lock = Lock()

    def _stop_signal_handler(self, signum, _):
        cur_process_name = multiprocessing.current_process().name

        if cur_process_name == "MainProcess":
            self.stop()
            log.info("Stop main process after %s signal", signum)
        else:
            log.info("Stop %s process after %s signal", cur_process_name, signum)

        exit(os.EX_OK)

    def _add_signals(self):
        signal.signal(signal.SIGINT, self._stop_signal_handler)
        signal.signal(signal.SIGTERM, self._stop_signal_handler)

    def _process_stream_start(self, stream: ZeroStream):
        self.process_start_callback and self.process_start_callback(
            stream=stream, station=self
        )

    def _process_stream_result(self, stream: ZeroStream):
        self.process_stop_callback and self.process_stop_callback(
            stream=stream, station=self
        )

    def _process_stream_error(self, stream: ZeroStream, error: Exception):
        if not self.process_error_callback:
            log.error(
                "Error while processing %s stream on %s station: %s",
                stream.id,
                self.id,
                error,
                exc_info=error,
            )
        else:
            self.process_error_callback(error, stream=stream, station=self)

    def _spawn_process_start(self, token: str):
        if self.spawn_process_start_callback:
            self.spawn_process_start_callback(token=token, station=self)

    def _spawn_process_result(self, token: str, stream: ZeroStream):
        self._processes_spawners.remove(token)

        if stream and self.spawn_process_stop_callback:
            self.spawn_process_stop_callback(token=token, stream=stream, station=self)

    def _spawn_process_error(self, token: str, error: Exception):
        self._processes_spawners.remove(token)

        if not self.spawn_process_error_callback:
            log.error(
                "Error while spawning a stream (token: %s) on %s station: %s",
                token,
                self.id,
                error,
                exc_info=error,
            )
        else:
            self.spawn_process_error_callback(error, token=token, station=self)

    def _try_stream(self, stream: ZeroStream) -> bool:
        if not isinstance(stream.pipe.node_b, NodeBase):
            return False

        if self.pipes and stream.pipe.id not in self.pipes:
            return False
        if self.nodes_a and stream.pipe.node_a.id not in self.nodes_a:
            return False
        if self.nodes_b and stream.pipe.node_b.id not in self.nodes_b:
            return False
        if self.networks and stream.session.network.id not in self.networks:
            return False

        with stream.lock_context(
            blocking=self.stream_lock_blocking,
            lock_ttl=self.stream_lock_ttl,
            wait_timeout=self.stream_lock_ttl,
        ) as is_lock_ready:

            log.debug("Try to spawn stream process (ID: %s)", stream.id)

            if is_lock_ready:
                if stream.station == self:
                    return True

                if not stream.is_busy:
                    with self._station_threads_lock:
                        stream.redirect_to(self)
                    return True

            reason = "locked" if not is_lock_ready else "busy"
            log.debug(
                "Stream process spawning fail (ID: %s, Reason: %s)", stream.id, reason
            )

        return False

    def _wait_stream(self) -> Union["ZeroStream", None]:
        list_filter = {
            "closed": False,
            "heartbeat_ts<=": time.time() - self.heartbeat_fail_delay,
        }
        if self.sessions:
            list_filter.update(
                {
                    "session->": [
                        sess.id if isinstance(sess, ZeroSession) else str(sess)
                        for sess in self.sessions
                    ]
                }
            )

        streams = ZeroStream.list(list_filter=list_filter)

        if self.to_shuffle_stream:
            random.shuffle(streams)

        for stream in streams:
            if self._try_stream(stream):
                return stream
        return None

    def _process_worker(
        self, stream: ZeroStream, successful_event: multiprocessing.synchronize.Event
    ):
        node = stream.pipe.node_b
        if isinstance(node, str):
            return

        self._process_stream_start(stream)

        try:
            node.process(stream, wait_timeout=self.stream_waiting_timeout)
        except Exception as e:
            return self._process_stream_error(stream, e)

        self._process_stream_result(stream)

        successful_event.set()

    def _process_stream(self, stream: ZeroStream):
        process_tuple = self._processes.get(stream)
        if process_tuple and process_tuple[0].is_alive():
            log.error("[%s] stream process is already running", stream.id)
            return

        log.info("Start %s stream process", stream.id)

        successful_event = multiprocessing.Event()

        process = multiprocessing.Process(
            target=self._process_worker, args=[stream, successful_event],
        )
        process.daemon = True
        process.start()

        self._processes[stream] = (process, successful_event)

    def _spawn_stream_process_worker(self):
        stream = None
        while not stream and not self._stopped:
            stream = self._wait_stream()
            if self.monitor_checks_delay:
                time.sleep(self.monitor_checks_delay)

        if self._stopped:
            return

        if stream:
            self._process_stream(stream)

        return stream

    def _spawn_stream_process(self):
        random_token = str(
            time.perf_counter()
            if hasattr(time, "perf_counter")
            else time.perf_counter()
        )

        self._spawn_process_start(random_token)

        self._stream_waiting_pool.apply_async(
            self._spawn_stream_process_worker,
            callback=functools.partial(self._spawn_process_result, random_token),
            error_callback=functools.partial(self._spawn_process_error, random_token),
        )
        self._processes_spawners.append(random_token)

    def _stop_stream_process(self, stream: ZeroStream, exception: Exception = None):
        process_tuple = self._processes.get(stream)

        if not process_tuple:
            raise ValueError("Stream process not found!")

        process_tuple[0].kill()

        del self._processes[stream]

        if exception:
            self._process_stream_error(stream, exception)

    def _check_and_update_process(self, stream: ZeroStream) -> bool:
        process, successful_event = self._processes[stream]

        if not process.is_alive():
            if successful_event.is_set() and stream.session.closing_mode:
                stream.close()

            del self._processes[stream]

            log.info(
                "The process of the stream (ID: %s) was stopped (Station ID: %s)",
                stream.id,
                self.id,
            )

            return False

        return True

    def _check_and_update_streams(self):
        now = time.monotonic()
        streams = list(self._processes.keys())

        for session in self.sessions:
            session.refresh()

        for stream in streams:
            try:

                stream.refresh(ignore_errors=False)

                if stream.station != self:
                    raise TethysRuntimeError(
                        "stream's station was changed to [{}]".format(stream.station)
                    )

                if self._check_and_update_process(stream):
                    stream.heartbeat()

                stream.session.refresh(ignore_errors=False)

            except Exception as e:
                log.exception(e)

                if self._next_update < now:
                    log.warning(
                        "The stream (ID: %s) disconnected from the station (ID: %s)",
                        stream.id,
                        self.id,
                    )
                    stream.station = None
                    self._stop_stream_process(stream, e)

    def _start_loop(self):
        self._next_update = 0

        while not self._stopped and (
            not self.sessions or not all([s.closed for s in self.sessions])
        ):
            now = time.monotonic()

            if self._next_update < now:
                with self._station_threads_lock:
                    self._check_and_update_streams()
                self._next_update = now + self.update_min_delay

            if (
                len(self._processes) + len(self._processes_spawners)
                < self.max_processes_count
            ):
                self._spawn_stream_process()

            time.sleep(max([0, self.monitor_checks_delay]))

    def start(self, **kwargs):
        """Start the worker process"""

        if self._stopped:
            self._stopped = False
            self._stream_waiting_pool = ThreadPool(processes=self.max_processes_count)

            self._add_signals()
            self._start_loop()

            if not self._stopped:
                log.info("Stop the main process after stopping the main loop")
                self.stop()

    def stop(self, **kwargs):
        """Stop the worker process"""

        if not self._stopped:
            self._stopped = True
            self._stream_waiting_pool.terminate()

            for random_token in self._processes_spawners:
                self._processes_spawners.remove(random_token)

            for stream in list(self._processes.keys()):
                self._stop_stream_process(stream)
