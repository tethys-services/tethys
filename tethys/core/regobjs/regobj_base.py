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

from abc import ABC, abstractmethod
from typing import List, Union


class RegistrableObjectBase(ABC):
    """
    Base abstract class for all entities that used like models for a database.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def load(cls, expression: str, **kwargs) -> "RegistrableObjectBase":
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def list(cls, **kwargs) -> List["RegistrableObjectBase"]:
        raise NotImplementedError

    @abstractmethod
    def save(self, **kwargs) -> "RegistrableObjectBase":
        raise NotImplementedError

    @abstractmethod
    def refresh(self, **kwargs) -> Union["RegistrableObjectBase", None]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs) -> "RegistrableObjectBase":
        raise NotImplementedError

    @abstractmethod
    def lock(self, **kwargs) -> bool:
        raise NotImplementedError

    @abstractmethod
    def unlock(self, **kwargs) -> bool:
        raise NotImplementedError
