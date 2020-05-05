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

import inspect
from abc import ABC
from typing import List, Type

from tethys.utils.classes import get_sub_classes


class AppBase(ABC):
    @classmethod
    def get_apps(cls) -> List[Type]:
        sub_classes = filter(lambda x: not inspect.isabstract(x), get_sub_classes(cls))
        classes = [c for c in sub_classes if not getattr(c, "DISABLED", None)]
        return classes
