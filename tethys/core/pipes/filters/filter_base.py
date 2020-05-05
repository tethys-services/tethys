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
from typing import Any

from serobj.utils.serobj_calls import SerobjCallsBase


class FilterBase(SerobjCallsBase):
    """
        Base class for all pipe filters. Each filter should provide
        an `execute` method that returns the score.
    """

    _SEROBJ__ATTRS = []

    @abstractmethod
    def execute(self, data_packet: Any, **kwargs) -> float:
        """
        The method that pipe executes before data sending.

        :param data_packet: any data object
        :return: score (:class:`float`) that contains any user's value.
            For many cases you can use [1, 0] values.

        """
        raise NotImplementedError
