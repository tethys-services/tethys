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

import json
from typing import Callable, Any

from jsonpath_ng import parse
from tethys.core.pipes.filters.filter_base import FilterBase


class SimpleJsonPathFilter(FilterBase):
    """
    This filter executes user's function for each matched value
    (with the `JSONPath <https://goessner.net/articles/JsonPath/>`_ expression) and calculate a score.

    """

    def __init__(
        self,
        path_expression: str,
        value_filter_func: Callable,
        pass_no_json: bool = False,
        calc_score: bool = False,
    ):
        """

        :param path_expression: json-path expression
        :type path_expression: str
        :param value_filter_func: Function which return True/False depends on the value
        :type value_filter_func: Callable
        :param pass_no_json: if data_packet is not json (or python object)
            then the filter return the score like 1.0 else 0.0
        :type pass_no_json: bool
        :param calc_score: if True then the filter return (success_filtered_matches / all_matches)
            else return 1 or 0
        :type calc_score: bool
        """
        self._path_expression = parse(path_expression)
        self._value_filter_func = value_filter_func
        self._pass_no_json = pass_no_json
        self._calc_score = calc_score

        super(SimpleJsonPathFilter, self).__init__(
            path_expression, value_filter_func, pass_no_json, calc_score
        )

    def execute(self, data_packet: Any, **kwargs):
        """
        Execute :func:`value_filter_func` for each matched value and
        calculate the score as a percent of the success executes.

        :param data_packet: any data object
        :return: calculated score (:class:`float`)
        """

        if isinstance(data_packet, str):
            try:
                data_packet = json.loads(data_packet)
            except json.JSONDecodeError:
                if self._pass_no_json:
                    return 1.0
                else:
                    return 0.0

        success_matches_count = 0

        matches = self._path_expression.find(data_packet)
        for match in matches:
            if not self._value_filter_func(match.value) and not self._calc_score:
                return 0.0
            elif self._calc_score:
                success_matches_count += 1

        if not self._calc_score or success_matches_count == len(matches):
            return 1.0

        return success_matches_count / len(matches)
