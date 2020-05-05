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

from queue import Empty
from multiprocessing import Queue
from multiprocessing.managers import BaseManager

from tethys.core.transports.connectors.connector_base import (
    ConnectorBase,
    ConnectionBase,
)


class QueuesManager(BaseManager):
    _queues = {}
    _instance = None

    @classmethod
    def get_queue(cls, name):
        if name not in cls._queues:
            cls._queues[name] = Queue()
        return cls._queues[name]

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
            cls._instance.start()
        return cls._instance


QueuesManager.register("get_queue", QueuesManager.get_queue)


class LocalConnection(ConnectionBase):
    def __init__(self, channel_id, recv_check_delay: float):
        self.channel_id = channel_id
        self.recv_check_delay = recv_check_delay

    @property
    def queue(self):
        return QueuesManager.instance().get_queue(self.channel_id)

    def recv_iter(self, **kwargs):
        while True:
            try:
                yield "", self.queue.get(timeout=self.recv_check_delay)
            except Empty:
                return None

    def send(self, data_packet, **kwargs):
        self.queue.put(data_packet)

    def ack(self, message_key, **kwargs):
        pass

    def open(self, **kwargs) -> "LocalConnection":
        QueuesManager.instance()

        return self

    def close(self, **kwargs) -> "LocalConnection":
        return self


class LocalConnector(ConnectorBase):
    def __init__(self, recv_check_delay: float = 0.1):
        self.recv_check_delay = recv_check_delay

    def connect(
        self, channel_id: str, recv_check_delay: float = None, **kwargs
    ) -> "LocalConnection":

        recv_check_delay = recv_check_delay or self.recv_check_delay
        return LocalConnection(channel_id, recv_check_delay).open()
