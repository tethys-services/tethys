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
from typing import Any, TYPE_CHECKING, Generator

from tethys.core.regobjs.regobj_base import RegistrableObjectBase

if TYPE_CHECKING:
    from tethys.core.stations.station_base import StationBase  # noqa: F401


class StreamBase(RegistrableObjectBase):
    """
    Base abstract class for the Streams

    """

    @property
    @abstractmethod
    def is_busy(self) -> bool:
        """
        Is some station using the stream?

        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def open(self, **kwargs) -> "StreamBase":
        """
        Open the stream

        :return: self instance
        :rtype: StreamBase
        """
        raise NotImplementedError

    @abstractmethod
    def close(self, **kwargs) -> "StreamBase":
        """
        Close the stream

        :return: self instance
        :rtype: StreamBase
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, data_packet: Any, **kwargs):
        """
        Write the data_packet to the stream

        :param data_packet: any data object
        """
        raise NotImplementedError

    @abstractmethod
    def read(
        self, count: int = None, wait_timeout: float = None, **kwargs
    ) -> Generator:
        """
        Read the data_packets from the stream. Return Generator.

        :param count: count of the data_packets
        :type count: int
        :param wait_timeout: waiting time (seconds)
        :type wait_timeout: float
        """
        raise NotImplementedError

    @abstractmethod
    def ack(self, message_key: str, **kwargs):
        """
        Acknowledge message

        :param message_key: message key for the acknowledgement
        :type message_key: str
        """
        raise NotImplementedError

    @abstractmethod
    def redirect_to(self, station: "StationBase", **kwargs):
        """
        Redirect stream processing to the station

        :param station: Station where the stream can be processed in the near time
        :type station: StationBase
        """
        raise NotImplementedError

    @abstractmethod
    def heartbeat(self, **kwargs):
        """
        Health heartbeat

        """
        raise NotImplementedError
