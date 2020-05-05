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

try:
    import sqlite3

    getattr(sqlite3, "enable_callback_tracebacks")
except AttributeError:  # hack problem with pypy3
    sqlite3.enable_callback_tracebacks = lambda _: None

import os
from persistqueue import Empty, SQLiteQueue, Queue
from tethys.core.transports.connectors.connector_base import (
    ConnectorBase,
    ConnectionBase,
)


class PersistQueueConnection(ConnectionBase):
    def __init__(self, queue_path: str, queue_engine: str, recv_check_delay: float):
        self.queue_path = queue_path
        self.queue_engine = queue_engine
        self.recv_check_delay = recv_check_delay

        self._queue = None

    @property
    def queue(self):
        return self._queue

    def recv_iter(self, **kwargs):
        while True:
            try:
                yield "", self.queue.get(timeout=self.recv_check_delay)
            except Empty:
                return None

    def send(self, data_packet, **kwargs):
        self.queue.put(data_packet)

    def ack(self, message_key, **kwargs):
        self.queue.task_done()

    def open(self, **kwargs) -> "PersistQueueConnection":
        if self.queue_engine == "sqlite":
            queue = SQLiteQueue(self.queue_path, auto_commit=False)
        elif self.queue_engine == "file":
            queue = Queue(self.queue_path)
        else:
            raise ValueError("bad queue engine value")

        self._queue = queue

        return self

    def close(self, **kwargs) -> "PersistQueueConnection":
        self._queue = None

        return self


class PersistQueueConnector(ConnectorBase):
    def __init__(
        self, queue_dir=None, queue_engine="sqlite", recv_check_delay: float = 0.1
    ):
        self.queue_dir = queue_dir or "/tmp/tethys/persist_queues/"
        self.queue_engine = queue_engine
        self.recv_check_delay = recv_check_delay

    def connect(
        self,
        channel_id: str,
        queue_engine: str = None,
        recv_check_delay: float = None,
        **kwargs
    ) -> "PersistQueueConnection":

        queue_path = os.path.join(self.queue_dir, channel_id)
        queue_engine = queue_engine or self.queue_engine
        recv_check_delay = recv_check_delay or self.recv_check_delay

        return PersistQueueConnection(queue_path, queue_engine, recv_check_delay).open()
