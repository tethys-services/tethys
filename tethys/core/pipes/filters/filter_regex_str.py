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

import re

from tethys.core.pipes.filters.filter_base import FilterBase


class RegexMatchFilter(FilterBase):
    """
    This filter use user's regular expressions with str(data_packet)

    """

    def __init__(self, expression: str, flags: int = 0):
        """

        :param expression: regex expression
        :type expression: str
        :param flags: flags from the 're' package (like re.IGNORECASE, re.MULTILINE)
        :type flags: int
        """

        self._expression = re.compile(expression, flags)
        self._flags = flags
        super(RegexMatchFilter, self).__init__(expression, flags=flags)

    def execute(self, data_packet, **kwargs):
        """
        Execute :func:`re.match` for the str(data_packet).

        :param data_packet: any data object
        :return: 1.0 or 0.0  (:class:`float`)

        """

        match_obj = self._expression.match(str(data_packet), self._flags)
        if not match_obj:
            return 0.0
        return 1.0
