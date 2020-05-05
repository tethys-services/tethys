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

from typing import Callable, Any

from tethys.core.pipes.filters.filter_base import FilterBase


class FNFilter(FilterBase):
    """
    This filter executes user's function for calculating a score.

    """

    def __init__(self, value_filter_func: Callable):
        """

        :param value_filter_func: proxy function for calculating a score
        :type value_filter_func: Callable
        """
        self._value_filter_func = value_filter_func
        super().__init__(value_filter_func)

    def execute(self, data_packet: Any, **kwargs) -> float:
        """
        Execute :func:`value_filter_func` with the same args.

        :param data_packet: any data object
        :return: calculated score (:class:`float`)
        """
        return self._value_filter_func(data_packet, **kwargs)
