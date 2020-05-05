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
from typing import TYPE_CHECKING, Any, Generator

from tethys.core.regobjs.regobj_base import RegistrableObjectBase

if TYPE_CHECKING:
    from tethys.core.streams.stream_base import StreamBase  # noqa: F401
    from tethys.core.sessions.sess_base import SessionBase  # noqa: F401


class PipeBase(RegistrableObjectBase):
    """
    Base abstract class for the Pipes
    """

    @abstractmethod
    def get_stream(self, session: "SessionBase") -> "StreamBase":
        """
        Get or create stream

        :param session: Session instance
        :type session: SessionBase
        :return: Stream instance
        :rtype: StreamBase
        """
        raise NotImplementedError

    @abstractmethod
    def pull(self, session: "SessionBase", **kwargs) -> Generator:
        """
        Get data_packets from the pipe's stream using python Generator

        :param session: Session instance
        :type session: SessionBase
        :return: data_packets generator
        :rtype: typing.Generator
        """
        raise NotImplementedError

    @abstractmethod
    def push(self, data_packet: Any, session: "SessionBase", **kwargs):
        """
        Push data to the pipe's stream

        :param data_packet: any data object or list of the data objects (with many=True)
        :param session: ZeroSession instance
        :type session: ZeroSession
        """
        raise NotImplementedError
