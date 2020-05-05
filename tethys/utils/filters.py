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

FILTER_FUNCS = {
    "->": lambda x, y: x in y,
    "!>": lambda x, y: x not in y,
    ">=": lambda x, y: x >= y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    "<": lambda x, y: x < y,
    "!=": lambda x, y: x != y,
    "==": lambda x, y: x == y,
}


def get_pair_filter(filters_map, key):
    field, operator = key[:-2], key[-2:]

    _filter = filters_map.get(operator)
    if not _filter:
        field = key[:-1]
        _filter = filters_map.get(operator[1])
    if not _filter:
        field = key
        _filter = filters_map.get("==")

    return field, _filter


def value_filter(value, dict_filter: dict):
    if not dict_filter:
        return True

    for key, filter_value in dict_filter.items():
        if getattr(value, key, None) == filter_value:
            continue

        field, _f_lambda = get_pair_filter(FILTER_FUNCS, key)

        if not _f_lambda or not _f_lambda(getattr(value, field, None), filter_value):
            return False

    return True
