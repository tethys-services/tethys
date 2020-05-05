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
from abc import ABC, abstractmethod
from typing import List, Any

import serobj

from tethys.core.exceptions import TethysBadRepositoryObjectValue

log = logging.getLogger(__name__)


class RepositoryBase(ABC):
    @abstractmethod
    def _list(self, path: str, **kwargs) -> List:
        raise NotImplementedError

    @abstractmethod
    def _load(self, path: str, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def _save(self, path: str, obj_repr: object, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _delete(self, path: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def _lock(
        self,
        path: str,
        lock_ttl: float = 60,
        wait_timeout: float = float("inf"),
        blocking: bool = True,
        **kwargs
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _unlock(self, path: str, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    def _serialize(cls, obj):
        return serobj.dumps(obj)

    @classmethod
    def _deserialize(cls, obj_repr):
        return serobj.loads(obj_repr)

    def list(self, path: str, ignore_errors: bool = True, **kwargs) -> List:
        objs_list = self._list(path, **kwargs)
        deserialized_objects = []

        for obj in objs_list:
            try:
                deserialized_objects.append(self._deserialize(obj))
            except ValueError as e:
                if not ignore_errors:
                    raise TethysBadRepositoryObjectValue(e)

        return deserialized_objects

    def load(self, path: str, ignore_errors: bool = False, **kwargs) -> Any:
        obj = self._load(path, **kwargs)

        try:
            return self._deserialize(obj)
        except Exception as e:
            if ignore_errors:
                return None

            raise TethysBadRepositoryObjectValue(
                "repository cannot deserialize data: {}".format(e)
            )

    def save(self, path: str, obj_repr: object, **kwargs):
        self._save(path, self._serialize(obj_repr), **kwargs)

    def delete(self, path: str, **kwargs) -> None:
        self._delete(path, **kwargs)

    def lock(
        self,
        path: str,
        lock_ttl: float = 60,
        wait_timeout: float = float("inf"),
        blocking: bool = True,
        **kwargs
    ) -> bool:

        return self._lock(
            path,
            lock_ttl=lock_ttl,
            wait_timeout=wait_timeout,
            blocking=blocking,
            **kwargs
        )

    def unlock(self, path: str, **kwargs) -> bool:
        return self._unlock(path, **kwargs)
