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

import sys
from typing import Iterable, Mapping, Generator, Callable


def flat_iter(
    iter_obj: Iterable, depth: int = None, converter: Callable = None
) -> Generator:
    if depth is None:
        depth = sys.getrecursionlimit()

    for item in iter_obj:
        if converter:
            item = converter(item)

        if (
            depth > 0
            and isinstance(item, Iterable)
            and not isinstance(item, Mapping)
            and not isinstance(item, (str, bytes, bytearray))
        ):
            yield from flat_iter(item, depth - 1)
        else:
            yield item
