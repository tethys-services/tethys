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

from typing import Iterable

from tethys.core.transports.connectors.connector_base import (
    ConnectorBase,
    ConnectionBase,
)


class DummyConnection(ConnectionBase):
    def __init__(self, recv_iter_data_packet: Iterable):
        self.recv_iter_data_packet = recv_iter_data_packet

    def recv_iter(self, **kwargs):
        yield from self.recv_iter_data_packet

    def send(self, data_obj, **kwargs):
        pass

    def ack(self, message_key, **kwargs):
        pass

    def open(self, **kwargs):
        return self

    def close(self, **kwargs):
        return self


class DummyConnector(ConnectorBase):
    def __init__(self, recv_iter_data_packet: Iterable = None):
        self.recv_iter_data_packet = recv_iter_data_packet or iter(lambda: None, None)

    def connect(self, _, **kwargs) -> "DummyConnection":
        return DummyConnection(self.recv_iter_data_packet)
