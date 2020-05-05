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

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from tethys.core.regobjs.regobj_base import RegistrableObjectBase

if TYPE_CHECKING:
    from tethys.core.streams import StreamBase  # noqa: F401


class TransportBase(RegistrableObjectBase):
    """
    Base abstract class for the Transport

    """

    @abstractmethod
    def is_connected(self, stream: "StreamBase", **kwargs) -> bool:
        """
        Is the connection established

        :param stream: Stream for the connection
        :type stream: StreamBase
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def connect(self, stream: "StreamBase", **kwargs):
        """
        Establish the connection

        :param stream: Stream for the connection
        :type stream: StreamBase
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, stream: "StreamBase", **kwargs):
        """
        Disconnect the stream's connection

        :param stream: Stream for the connection
        :type stream: StreamBase
        """
        raise NotImplementedError

    @abstractmethod
    def recv(self, stream: "StreamBase", **kwargs):
        """
        Read data_packet from the stream (using the current connection)

        :param stream: Stream for the connection
        :type stream: StreamBase
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, stream: "StreamBase", data_packet: Any, **kwargs):
        """
        Send data_packet to the stream (using connection)

        :param stream: Stream for the connection
        :type stream: StreamBase
        :param data_packet: any data object
        """
        raise NotImplementedError

    @abstractmethod
    def ack(self, stream: "StreamBase", message_key: str, **kwargs):
        """
        Acknowledge message

        :param stream: Stream for the connection
        :type stream: StreamBase
        :param message_key: message key for the acknowledgement
        :type message_key: str
        """
        raise NotImplementedError
