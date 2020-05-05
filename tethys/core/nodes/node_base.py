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
from typing import TYPE_CHECKING

from tethys.core.regobjs.regobj_base import RegistrableObjectBase

if TYPE_CHECKING:
    from tethys.core.streams.stream_base import StreamBase  # noqa: F401


class NodeBase(RegistrableObjectBase):
    """
    Base abstract class for the Node
    """

    @abstractmethod
    def process(self, stream: "StreamBase", **kwargs):
        """
        Read the stream and execute an operator for the stream's data packet.

        :param stream: Stream that node will process
        :type stream: StreamBase
        """
        raise NotImplementedError
