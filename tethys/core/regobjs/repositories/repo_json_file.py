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

from tethys.core.regobjs.repositories.repo_local import LocalRepository
from tethys.utils.files import FLock


class JsonFileRepository(LocalRepository):
    def __init__(
        self,
        f_path: str = None,
        create: bool = False,
        storage: dict = None,
        buff_2: bool = True,
    ):
        self._f_path = f_path or "./tethys_repo.json"
        self._f_2buf_path = f_path or "./tethys_repo.2buf.json" if buff_2 else None

        try:
            open(self._f_path, "r").close()
        except FileNotFoundError:
            if create:
                with open(self._f_path, "w") as f:
                    f.write("{}")
            else:
                raise

        if storage is not None:
            super().__init__(storage)

    class ProxyStorage(dict):
        def __init__(self, self_obj: "JsonFileRepository"):
            self._self_obj = self_obj

            try:
                _storage_data = self_obj._load_json()
            except Exception:
                if self_obj._f_2buf_path:
                    _storage_data = self_obj._load_json(self_obj._f_2buf_path)
                else:
                    raise

            super().__init__(_storage_data)

        def __setitem__(self, key, value):
            super().__setitem__(key, value)
            self._self_obj._storage = self

        def __delitem__(self, key):
            super().__delitem__(key)
            self._self_obj._storage = self

    @property
    def _storage(self) -> dict:
        return self.ProxyStorage(self)

    @_storage.setter
    def _storage(self, storage: dict):
        if isinstance(storage, dict):
            if self._f_2buf_path:
                self._save_json(storage, self._f_2buf_path)
            self._save_json(storage)

    def _load_json(self, f_path: str = None) -> dict:
        f_path = f_path or self._f_path
        with FLock(f_path):
            with open(f_path) as f:
                return json.load(f) or {}

    def _save_json(self, data: dict, f_path: str = None):
        f_path = f_path or self._f_path
        with FLock(f_path):
            with open(f_path, "w") as f:
                json.dump(data, f)
