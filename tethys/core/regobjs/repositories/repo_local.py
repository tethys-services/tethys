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

import multiprocessing
import time

from tethys.core.exceptions import TethysRONotFound
from tethys.core.regobjs.repositories.repo_base import RepositoryBase
from tethys.utils.filters import value_filter

THREADS_LOCK = multiprocessing.RLock()


class LocalRepository(RepositoryBase):
    def __init__(self, storage: dict = None):
        self._storage = storage or {}

    def __reduce__(self):
        return self.__class__, (self._storage,), {}

    def _list(self, path: str, list_filter: dict = None):
        list_filter = list_filter or {}

        storage = self._storage
        lists_keys_and_values = list(
            zip(
                *filter(
                    lambda dict_pair: dict_pair[0].startswith(path)
                    and (
                        not list_filter
                        or value_filter(self._deserialize(dict_pair[1]), list_filter)
                    ),
                    list(storage.items()),
                )
            )
        )
        return lists_keys_and_values[1] if len(lists_keys_and_values) > 1 else []

    def _load(self, path, **kwargs):
        try:
            return self._storage[path]
        except KeyError:
            raise TethysRONotFound("Object `{}` not found in Repository".format(path))

    def _save(self, path, obj_repr, **kwargs):
        self._storage[path] = obj_repr

    def _delete(self, path: str, **kwargs):
        try:
            lock_key = self._get_lock_key(path)
            del self._storage[lock_key]
        except KeyError:
            pass

        try:
            del self._storage[path]
        except KeyError:
            raise TethysRONotFound("Object `{}` not found in Repository".format(path))

    @staticmethod
    def _get_lock_key(path: str):
        return "lock__{}".format(path)

    def _lock(
        self,
        path: str,
        lock_ttl: float = 5,
        blocking: bool = True,
        wait_timeout: float = float("inf"),
        **kwargs
    ):
        lock_key = self._get_lock_key(path)

        if THREADS_LOCK.acquire(block=False):
            expires_ts = self._storage.get(lock_key, 0)

            if expires_ts:
                delta = expires_ts - time.time()

                if delta > 0:
                    if not blocking:
                        return False
                    else:
                        time.sleep(min(delta, wait_timeout))

            self._storage[lock_key] = time.time() + lock_ttl

            THREADS_LOCK.release()

        return True

    def _unlock(self, path: str, **kwargs):
        lock_key = self._get_lock_key(path)

        if THREADS_LOCK.acquire(block=False):
            try:
                del self._storage[lock_key]
                THREADS_LOCK.release()
                return True
            except KeyError:
                THREADS_LOCK.release()
                return False
