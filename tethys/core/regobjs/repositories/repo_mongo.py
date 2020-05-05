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

import time
import uuid
from multiprocessing import current_process

import pymongo

from tethys.core.exceptions import TethysRONotFound
from tethys.core.regobjs.repositories.repo_base import RepositoryBase
from tethys.utils.filters import get_pair_filter

LOCK_CHECK_DELAY = 0.1

FILTER_MONGO_MAP = {
    "->": "$in",
    "!>": "$nin",
    ">=": "$gte",
    ">": "$gt",
    "<=": "$lte",
    "<": "$lt",
    "!=": "$ne",
    "==": "$eq",
}


class MongodbRepository(RepositoryBase):
    def __init__(
        self, uri: str, collection_prefix: str = "repo", object_key_field: str = "key"
    ):
        self.uri = uri
        self.collection_prefix = collection_prefix or "repo"
        self.object_key_field = object_key_field

        self._databases_by_process = {}

    @property
    def database(self):
        databases_by_process = getattr(self, "_databases_by_process", None)
        if not databases_by_process:
            self._databases_by_process = {}

        database = self._databases_by_process.get(current_process())
        if not database:
            client = pymongo.MongoClient(self.uri)
            database = client.get_database()
            self._databases_by_process[current_process()] = database

        return database

    @staticmethod
    def _get_object_path_pair(path: str):
        path_parts_array = path.strip("/").split("/")
        collection_name, object_name = (
            ".".join(path_parts_array[:-1]),
            path_parts_array[-1],
        )
        return collection_name, object_name

    def _get_collection(self, path: str):
        collection_name = "{}.{}".format(
            self.collection_prefix, path.strip("/").replace("/", ".")
        )
        return self.database[collection_name]

    @classmethod
    def __find_expression(cls, query: dict):
        attrs_path = "payload.representation.attrs._attrs.representation"

        if not query:
            return {}

        if len(query) <= 1:
            for field, value in query.items():
                return {"{}.{}".format(attrs_path, field): value}

        raw_query = {"$and": []}

        for field, value in query.items():
            raw_query["$and"].append({"{}.{}".format(attrs_path, field): value})

        return raw_query

    def _list(
        self, path: str, list_filter: dict = None, raw_query: bool = False, **kwargs
    ):
        list_filter = list_filter or {}
        collection = self._get_collection(path)

        if raw_query:
            query = list_filter
            return list(collection.find(query, {"_id": 0, self.object_key_field: 0}))

        else:
            query = {}
            for key, value in list_filter.items():
                field, _filter = get_pair_filter(FILTER_MONGO_MAP, key)

                if field in query:
                    query[field].update({_filter: value})
                else:
                    query[field] = {_filter: value}

            return list(
                collection.find(
                    self.__find_expression(query), {"_id": 0, self.object_key_field: 0}
                )
            )

    def _load(self, path: str, **kwargs):
        try:
            collection_name, object_name = self._get_object_path_pair(path)
            collection = self._get_collection(collection_name)

            obj_repo = collection.find_one(
                {self.object_key_field: object_name},
                {"_id": 0, self.object_key_field: 0},
            )

            if not obj_repo:
                raise KeyError

            return obj_repo
        except KeyError:
            raise TethysRONotFound("Object `{}` not found in Repository".format(path))

    def _save(self, path: str, obj_repr: dict, **kwargs):
        collection_name, object_name = self._get_object_path_pair(path)
        collection = self._get_collection(collection_name)
        kv_pair_dict = {self.object_key_field: object_name}

        obj_repr.update(kv_pair_dict)
        collection.update(kv_pair_dict, obj_repr, upsert=True)

    def _delete(self, path: str, **kwargs):
        self._unlock(path)

        collection_name, object_name = self._get_object_path_pair(path)
        collection = self._get_collection(collection_name)
        kv_pair_dict = {self.object_key_field: object_name}

        result = collection.delete_one(kv_pair_dict)

        if not result["deletedCount"]:
            raise TethysRONotFound(
                "{} collection has not {} object".format(collection_name, object_name)
            )

    def _get_locks_collection(self, path: str):
        new_collection_path = "{}.locks".format(path)
        return self._get_collection(new_collection_path)

    def _lock(
        self,
        path: str,
        lock_ttl: float = 60,
        blocking: bool = True,
        wait_timeout: float = float("inf"),
        **kwargs
    ):
        collection_name, lock_key = self._get_object_path_pair(path)
        collection = self._get_locks_collection(collection_name)
        kv_pair_dict = {self.object_key_field: lock_key}

        lock_dict = collection.find_one(kv_pair_dict)
        if lock_dict and isinstance(lock_dict, dict):
            expires_ts = lock_dict.get("expires_ts", 0)
            delta = expires_ts - time.time()

            if delta > 0:
                if not blocking:
                    return False
                else:
                    time.sleep(max(delta, wait_timeout))

        expires_ts = time.time() + lock_ttl
        self_token = str(uuid.uuid4())
        obj_repr = {**kv_pair_dict, "expires_ts": expires_ts, "self_token": self_token}

        collection.update(kv_pair_dict, obj_repr, upsert=True)

        time.sleep(LOCK_CHECK_DELAY)

        lock_dict = collection.find_one(kv_pair_dict)
        if lock_dict and isinstance(lock_dict, dict):
            token = lock_dict.get("self_token")

            if token == self_token:
                return True

        return False

    def _unlock(self, path: str, **kwargs):
        collection_name, lock_key = self._get_object_path_pair(path)
        collection = self._get_locks_collection(collection_name)

        collection.find_one_and_delete({self.object_key_field: lock_key})
