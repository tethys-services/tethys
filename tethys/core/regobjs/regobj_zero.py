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

import hashlib
import logging
import multiprocessing
import uuid
from collections import OrderedDict, defaultdict
from contextlib import contextmanager
from copy import deepcopy
from typing import Callable, List, Any, TypeVar, Type, Optional

import cerberus
import serobj

from tethys.core.exceptions import (
    TethysRONotFound,
    TethysROFieldValidationError,
    TethysException,
)
from tethys.core.regobjs.regobj_base import RegistrableObjectBase
from tethys.core.regobjs.repositories.repo_base import RepositoryBase
from tethys.core.regobjs.repositories.repo_local import LocalRepository
from tethys.utils.classes import get_sub_classes
from tethys.utils.iterable import flat_iter

RegObjZT = TypeVar("RegObjZT", bound="ZeroRegistrableObject")

log = logging.getLogger(__name__)

CLASS_PATH_PREFIX = "/zero/"

_OBJECTS_MAP = {}


class ZeroRegistrableObject(RegistrableObjectBase):
    """
    Base class for all entities that used like models for a database.
    It's the Zero generation.

    A few examples:
        .. code-block:: python

            class SomeClass(ZeroRegistrableObject):
                FIELDS_SCHEMA = {
                    "some_field": {"type": "string"}
                }

                def __init__(self, some_field, another_field, **kwargs):
                    self.some_field = some_field
                    self.another_field = another_field

                # ...

            # -------------------------------------------------

            obj1 = SomeClass("str", "no:save", _id="some_id")
            obj2 = SomeClass.load("some_id")

            assert id(obj1) == id(obj2)

            # -------------------------------------------------

            obj1 = SomeClass("str", "no:save")
            obj1.save()

            obj2 = ZeroRegistrableObject.load(obj1.path)

            assert id(obj1) == id(obj2)

            # -------------------------------------------------

            ZeroRegistrableObject.REPOSITORY = JsonFileRepository(create=True)

            obj1 = SomeClass(some_field="str", another_field="no:save", _id="some_id")
            obj1.save()

            assert obj1.some_field == "str"
            assert obj1.another_field == "no:save"

            # restart script

            obj2 = SomeClass.load("some_id")
            assert obj1.some_field == "str"
            assert obj1.another_field == "no:save"  # raise AttributeError: 'SomeClass' object has no attribute 'another_field'


    """

    _id = None
    _attrs = {}
    _version = None

    _NOT_SERIALIZABLE_ATTRS = [
        "_id",
        "_attrs",
        "_version",
        "_SEROBJ__ATTRS",
        "_SEROBJ__NEW_ARGS",
        "_NOT_SERIALIZABLE_ATTRS",
        "_MULTIPROCESS_MANAGER",
        "REPOSITORY",
        "FIELDS_SCHEMA",
        "CLASS_PATH",
    ]

    _MULTIPROCESS_MANAGER = multiprocessing.Manager()

    CLASS_PATH = "/sandbox/"
    "Default collection path in the repository"

    FIELDS_SCHEMA = {}
    "Default fields validators"

    REPOSITORY = LocalRepository(_MULTIPROCESS_MANAGER.dict({"_local_repo": True}))
    "Entities repository. You can override it in your own classes"

    def __getnewargs_ex__(self):
        return (), {"_id": self.id}

    def __getstate__(self) -> dict:
        return {
            "_id": self.id,
            "_attrs": self._attrs,
            "_version": self.version,
        }

    def __setstate__(self, state: dict):
        self._id = state["_id"]
        self._attrs = state["_attrs"]

    @classmethod
    def _get_extra_types(cls) -> List[Any]:
        return []

    @classmethod
    def _get_validator(cls) -> "cerberus.Validator":
        validator = cerberus.Validator(allow_unknown=True)
        classes = get_sub_classes(ZeroRegistrableObject) + [OrderedDict, defaultdict]
        for type_cls in classes:
            validator.types_mapping[type_cls.__name__] = cerberus.TypeDefinition(
                type_cls.__name__, (type_cls,), ()
            )
            _get_extra_types_method = getattr(type_cls, "_get_extra_types", None)
            if isinstance(_get_extra_types_method, Callable):
                classes += _get_extra_types_method()

        return validator

    @classmethod
    def prepare(cls, item: dict, keys: list = None) -> dict:
        """Validate and normalize data in the attrs that define in the :attr:`FIELDS_SCHEMA`"""

        field_validator = cls._get_validator()

        if isinstance(keys, (list, tuple, set)):
            schema = {key: cls.FIELDS_SCHEMA[key] for key in keys}
        else:
            schema = cls.FIELDS_SCHEMA

        result = field_validator.validate(item, schema)

        if not result:
            raise TethysROFieldValidationError(field_validator.errors)

        return field_validator.normalized(item)

    @classmethod
    def generate_id(cls) -> str:
        """Generate random ID. Default: uuid4"""
        return str(uuid.uuid4())

    @classmethod
    def generate_path(cls, obj_id: str) -> str:
        """Generate collection path from the ID"""
        if obj_id.startswith(CLASS_PATH_PREFIX):
            return obj_id

        return "/{}/{}/{}".format(
            CLASS_PATH_PREFIX.strip("/"),
            cls.CLASS_PATH.strip("/"),
            str(obj_id).strip("/"),
        )

    @property
    def id(self) -> str:
        """Return self._id value"""
        return str(self._id)

    @property
    def path(self) -> str:
        """Return generate_path(ID) result"""
        return self.generate_path(self.id)

    @property
    def version(self) -> str:
        """Return generate_version() result"""
        if not self._version:
            self._version = self.generate_version()
        return self.generate_version()

    def generate_version(self) -> str:
        """Return hash of the fields data"""
        return hashlib.sha256(
            "{}/{}".format(self._id, serobj.dumps(self._attrs)).encode()
        ).hexdigest()

    def __getattr__(self, item: str):
        if item not in self._NOT_SERIALIZABLE_ATTRS and item in self.FIELDS_SCHEMA:
            try:
                value = self._attrs[item]

                if (
                    isinstance(value, str)
                    and self.FIELDS_SCHEMA.get(item, {}).get("type", "string")
                    != "string"
                    and value.startswith(CLASS_PATH_PREFIX)
                ):
                    if value in _OBJECTS_MAP:
                        return _OBJECTS_MAP[value]

                    try:
                        return self.load(value)
                    except TethysRONotFound:
                        return None

                return value

            except KeyError:
                pass

        return self.__getattribute__(item)

    def __setattr__(self, key: str, value: Any):
        if key not in self.FIELDS_SCHEMA:
            return super().__setattr__(key, value)

        normalized_pair = self.prepare({key: value}, keys=[key])
        key, value = next(iter(normalized_pair.items()))

        if isinstance(value, RegistrableObjectBase):
            if not isinstance(value, ZeroRegistrableObject):
                raise ValueError("You cannot add a non-ZeroRegistrableObject object")
            value = value.path

        self._attrs[key] = value
        self._version = None

    def __new__(
        cls: "ZeroRegistrableObject",
        *args,
        _id: str = None,
        _repo: "RepositoryBase" = None,
        **kwargs
    ):

        _id = _id or cls.generate_id()
        _path = cls.generate_path(_id)

        if _path in _OBJECTS_MAP:
            obj = _OBJECTS_MAP[_path]
        else:
            obj = object.__new__(cls)
            obj._id = _id
            obj._attrs = {}

            _OBJECTS_MAP[_path] = obj

        if isinstance(_repo, RepositoryBase):
            obj.REPOSITORY = _repo

        return obj

    def __str__(self):
        return "{}(_id='{}')".format(self.__class__.__name__, self.id)

    def __hash__(self):
        try:
            _hash_hex = uuid.UUID(self._id).hex
        except ValueError:
            _hash_hex = hashlib.sha256(self._id.encode()).hexdigest()
        return int(_hash_hex, 16)

    def __eq__(self, other: Any):
        if isinstance(other, str):
            return self.id == other
        elif not isinstance(other, ZeroRegistrableObject):
            return False
        return self.id == other.id and self.version == other.version

    def copy(self):
        old_id = self._id
        self._id = "copy_{}".format(id(self))

        obj = deepcopy(self)

        del _OBJECTS_MAP[self.generate_path(self._id)]
        self._id = old_id

        obj._id = obj.generate_id()

        _path = obj.generate_path(obj._id)
        _OBJECTS_MAP[_path] = obj

        return obj

    @classmethod
    def load(
        cls: Type[RegObjZT], obj_id: str, with_cache: bool = True, **kwargs
    ) -> RegObjZT:
        """
        Load the entity from the repository by ID.
        If the entity already in the memory then method will return cached version.

        :param obj_id: Entity ID or Entity path
        :type obj_id: str
        :param with_cache: load data from the cache (default: True)
        :type with_cache: bool
        :return: ZeroRegistrableObject instance
        :rtype: ZeroRegistrableObject
        """

        path = cls.generate_path(obj_id)

        if with_cache and path in _OBJECTS_MAP:
            return _OBJECTS_MAP[path]

        return cls.REPOSITORY.load(path, **kwargs)

    @classmethod
    def list(cls: Type[RegObjZT], list_filter: dict = None, **kwargs) -> List[RegObjZT]:
        """
        Load list of the entities.
        You can specify some filters, but the filter's query language is experimental.

        Filter example:
            {"some_field>=": 2}     -    list entities where some_field >= 2

            "{field_name}{operator}" - key template

        Basic filters:
            +------------+-----------------------+
            | operator   | python op.            |
            +============+=======================+
            | ->         |  field in {value}     |
            +------------+-----------------------+
            | !>         |  field not in {value} |
            +------------+-----------------------+
            | >=         |  field >= {value}     |
            +------------+-----------------------+
            | >          |  field > {value}      |
            +------------+-----------------------+
            | <=         |  field <= {value}     |
            +------------+-----------------------+
            | <          |  field < {value}      |
            +------------+-----------------------+
            | !=         |  field != {value}     |
            +------------+-----------------------+
            | ==         |  field == {value}     |
            +------------+-----------------------+

        :param list_filter: dictionary of the filters
        :type list_filter: dict
        :return: list of the ZeroRegistrableObject instances
        :rtype: List(ZeroRegistrableObject)
        """

        return cls.REPOSITORY.list(
            cls.generate_path(""), list_filter=list_filter, **kwargs
        )

    def refresh(
        self: RegObjZT, ignore_errors: bool = True, **kwargs
    ) -> Optional[RegObjZT]:
        """
        Reload entity from the repository (without cache)

        :param ignore_errors: ignore errors like TethysRONotFound (default: True)
        :type ignore_errors: bool
        :return: return ZeroRegistrableObject instance or None (when error like NotFound)
        :rtype: ZeroRegistrableObject or None
        """
        try:
            kwargs.pop("with_cache", ...)

            return self.load(self.id, with_cache=False, **kwargs)
        except TethysException:
            if ignore_errors is False:
                raise

    def save(
        self: RegObjZT,
        save_dependency: bool = True,
        save_dependency_depth: int = 6,
        save_dependency_search_depth: int = 0,
        **kwargs
    ) -> RegObjZT:
        """
        Save current state to the repository.

        :param save_dependency: save related entities
        :type save_dependency: bool
        :param save_dependency_depth: depth of related entities recursion (-1 = infinity)
        :type save_dependency_depth: int
        :param save_dependency_search_depth: depth of searching in the fields values (like dict).
        :type save_dependency_depth: int
        """

        normalized_attrs = self.prepare(self._attrs)
        setattr(self, "_attrs", normalized_attrs)

        def _converter(x):
            if isinstance(x, dict):
                return x.items()
            return x

        if save_dependency and save_dependency_depth != 0:
            for attr_name in self._attrs.keys():
                attr_items = [getattr(self, attr_name, None)]

                items = filter(
                    lambda x: isinstance(x, ZeroRegistrableObject),
                    flat_iter(
                        attr_items,
                        depth=save_dependency_search_depth,
                        converter=_converter,
                    ),
                )

                for item in items:
                    item.save(
                        save_dependency=save_dependency,
                        save_dependency_depth=save_dependency_depth - 1,
                        save_dependency_search_depth=save_dependency_search_depth,
                        **kwargs
                    )

        self.REPOSITORY.save(self.path, self, **kwargs)

        return self

    def delete(self: RegObjZT, **kwargs) -> RegObjZT:
        """
        Delete the object from the repository.

        :return: return self object
        :rtype: ZeroRegistrableObject
        """

        self.REPOSITORY.delete(self.path, **kwargs)
        return self

    def lock(
        self,
        lock_ttl: float = 60,
        wait_timeout: float = float("inf"),
        blocking: bool = True,
        **kwargs
    ) -> bool:
        """
        Lock the object in the repository.

        :param lock_ttl: time to live for the lock (next lock will wait for the time or wait_timeout)
        :type lock_ttl: float
        :param wait_timeout: how much time to wait until lock is unlocked
            (after this time the function will have ignored the lock)
        :type wait_timeout: float
        :param blocking: wait for the lock (if false then the function return False)
        :type blocking: bool
        :return: is locked by the current process?
        """

        return self.REPOSITORY.lock(
            self.path,
            lock_ttl=lock_ttl,
            wait_timeout=wait_timeout,
            blocking=blocking,
            **kwargs
        )

    def unlock(self, **kwargs) -> bool:
        """
        Unlock the object in the repository.

        """

        return self.REPOSITORY.unlock(self.path, **kwargs)

    @contextmanager
    def lock_context(
        self,
        lock_ttl: float = 60,
        wait_timeout: float = float("inf"),
        blocking: bool = True,
        **kwargs
    ):
        """
        Contextmanager for the Locking/Unlocking the object in the repository.
        It allows nested context

        Example:
            .. code-block:: python

                start = time.time()

                def lock():
                    obj.lock()
                    print(time.time() - start)  # ~ 2s

                with obj.lock_context(lock_ttl=1):
                    with obj.lock_context(lock_ttl=2):
                        print(time.time() - start)  # ~ 0s

                        Thread(target=lock).start()
                        time.sleep(5)  # todo_something

        """

        locks_counter = getattr(self, "_lock_context_counter", 0)

        try:
            if locks_counter > 0:
                wait_timeout = 0

            setattr(self, "_lock_context_counter", locks_counter + 1)

            yield self.lock(
                lock_ttl=lock_ttl,
                wait_timeout=wait_timeout,
                blocking=blocking,
                **kwargs
            )
        finally:
            if locks_counter > 1:
                setattr(self, "_lock_context_counter", locks_counter - 1)
            else:
                self.unlock()
