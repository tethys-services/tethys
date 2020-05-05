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

import logging
from abc import abstractmethod
from typing import Any

from tethys.core.regobjs.regobj_base import RegistrableObjectBase

log = logging.getLogger(__name__)


class SessionBase(RegistrableObjectBase):
    """
    Base abstract class for the Sessions

    """

    @abstractmethod
    def open(self) -> "RegistrableObjectBase":
        """Open the session"""
        raise NotImplementedError

    @abstractmethod
    def close(self, mode: str = None) -> "RegistrableObjectBase":
        """Close the session"""
        raise NotImplementedError

    @abstractmethod
    def send(self, data_packet: Any):
        """Send the data_packet to the input nodes"""
        raise NotImplementedError
