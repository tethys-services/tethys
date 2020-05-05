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

from functools import reduce
from typing import Any, Union, Callable

from tethys.core.pipes.filters.filter_base import FilterBase

_ALIASES = {
    "+": sum,
    "*": lambda lst: reduce(lambda x, y: x * y, lst),
    "max": max,
    "min": min,
}


class CompositeFilter(FilterBase):
    """
    This filter aggregate scores from other filters and calculates a new score using a specific function.

    """

    def __init__(self, *filters: FilterBase, function: Union[str, Callable] = "+"):
        """

        :param filters: list of the filters
        :type filters: FilterBase
        :param function: function for calculating an aggregated score.
            Available aliases: ["+", "*", "max", "min"].
            Default value: "+".
        :type function: Union[str, Callable]
        """
        self._filters, self._function = (
            filters,
            _ALIASES[function] if isinstance(function, str) else function,
        )

        super(CompositeFilter, self).__init__(*filters, function=function)

    def execute(self, data_packet: Any, **kwargs) -> float:
        """
        Execute each filter and after execute the function with the :class:`typing.Generator` (that contains the scores) argument.

        :param data_packet: any data object
        :return: calculated score (:class:`float`)
        """
        return self._function(f.execute(data_packet, **kwargs) for f in self._filters)
