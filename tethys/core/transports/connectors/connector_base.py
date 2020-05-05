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

from abc import abstractmethod, ABC
from typing import Any, Generator, Tuple

from serobj.utils.serobj_calls import SerobjCallsBase


class ConnectionBase(ABC):
    @abstractmethod
    def recv_iter(self, **kwargs) -> Generator[Tuple[str, Any], None, None]:
        raise NotImplementedError

    @abstractmethod
    def send(self, data_packet: Any, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def ack(self, message_key: str, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def open(self) -> "ConnectionBase":
        raise NotImplementedError

    @abstractmethod
    def close(self) -> "ConnectionBase":
        raise NotImplementedError


class ConnectorBase(SerobjCallsBase):
    @abstractmethod
    def connect(self, channel_id: str, *args, **kwargs) -> "ConnectionBase":
        raise NotImplementedError
