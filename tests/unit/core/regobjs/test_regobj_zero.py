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
from collections import OrderedDict
from unittest import mock
from unittest.mock import call

import pytest
from pytest import fixture

from tethys.core.exceptions import TethysROFieldValidationError, TethysRONotFound
from tethys.core.regobjs.regobj_zero import (
    ZeroRegistrableObject,
    CLASS_PATH_PREFIX,
    _OBJECTS_MAP,
)


def validate(*_):
    return True


def normalized(item):
    item = OrderedDict(item)
    item.update({"_normalized": True})
    return item


class MockRegObj(ZeroRegistrableObject):
    FIELDS_SCHEMA = {
        "test": {},
        "test0": {"type": "TestObj"},
        "test1": {"type": "TestObj"},
    }
    REPOSITORY = mock.MagicMock(side_effect=lambda *_, **__: ...)

    def __init__(self, validator=None, **__):
        self.__class__.validator = validator

    @classmethod
    def _get_validator(cls):
        return cls.validator


class TestZeroRegistrableObject:
    @staticmethod
    def teardown_method():
        MockRegObj.REPOSITORY.reset_mock()
        _OBJECTS_MAP.clear()

    @fixture
    def validator(self):
        validator_mock = mock.MagicMock()
        validator_mock.validate = mock.MagicMock(side_effect=validate)
        validator_mock.normalized = mock.MagicMock(side_effect=normalized)
        return validator_mock

    # prepare

    def test_fields_prepare(self, validator):
        data = {"test": 1}

        obj = MockRegObj(validator)
        result = obj.prepare(data)

        assert result["test"] == data["test"]
        assert result != data
        validator.validate.assert_called_once_with(data, MockRegObj.FIELDS_SCHEMA)
        validator.normalized.assert_called_once_with(data)

    def test_fields_prepare_keys(self, validator):
        data = {"test": 1}

        obj = MockRegObj(validator)
        result = obj.prepare(data, ["test"])

        assert result["test"] == data["test"]
        assert result != data
        validator.validate.assert_called_once_with(data, {"test": {}})
        validator.normalized.assert_called_once_with(data)

    def test_fields_prepare_bad_keys(self, validator):
        data = {"test": 1}

        obj = MockRegObj(validator)

        with pytest.raises(KeyError):
            obj.prepare(data, ["test2"])

    def test_fields_prepare_exception(self, validator):
        data = {"test": 1}

        def sim_validate(*_):
            return False

        validator.validate = sim_validate

        obj = MockRegObj(validator)

        with pytest.raises(TethysROFieldValidationError):
            obj.prepare(data)

    # magic

    def test_getattr(self, validator):
        target_obj = MockRegObj(validator, _id="target")
        obj = MockRegObj(validator)

        def raise_404(*_, **__):
            raise TethysRONotFound("404")

        obj.load = mock.MagicMock(side_effect=raise_404)

        obj_uri = target_obj.path

        obj._attrs["abc"] = "abc"
        obj._attrs["test"] = obj_uri
        obj._attrs["test0"] = obj_uri
        obj._attrs["test1"] = CLASS_PATH_PREFIX + "404"

        assert obj.test == obj_uri
        assert obj.test0 == target_obj
        assert obj.test1 is None

        with pytest.raises(AttributeError):
            getattr(obj, "abc")

    def test_setattr_not_field(self, validator):
        obj = MockRegObj(validator)
        first_version = obj.version

        obj.abc = "abc"

        assert obj.version == first_version
        assert obj.abc == "abc"
        assert "abc" not in obj._attrs

    def test_setattr_field(self, validator):
        obj = MockRegObj(validator)
        first_version = obj.version

        obj.test = "test"

        assert obj.version != first_version
        assert obj.test == "test"
        assert obj._attrs["test"] == "test"

    def test_setattr_related_field(self, validator):
        target_obj = MockRegObj(validator, _id="target")
        obj = MockRegObj(validator)
        first_version = obj.version

        obj.test0 = target_obj
        obj.test1 = target_obj.path

        assert obj.version != first_version
        assert obj.test0 == target_obj and obj.test1 == target_obj
        assert (
            obj._attrs["test0"] == target_obj.path
            and obj._attrs["test1"] == target_obj.path
        )

    def test_new(self, validator):
        from tethys.core.regobjs.regobj_zero import _OBJECTS_MAP

        obj1 = MockRegObj(validator, _id="obj1")
        obj11 = MockRegObj(validator, _id="obj1")
        obj2 = MockRegObj(validator)

        assert id(obj1) == id(obj11)
        assert id(obj1) != id(obj2)
        assert obj1 != obj2
        assert obj1.path in _OBJECTS_MAP
        assert obj2.path in _OBJECTS_MAP

    def test_hash(self):
        obj1 = MockRegObj(_id="obj1")
        obj2 = MockRegObj()

        assert hash(obj1) == hash(obj1)
        assert hash(obj1) != hash(obj2)
        assert isinstance(hash(obj1), int) and isinstance(hash(obj2), int)

    def test_eq(self):
        obj1 = MockRegObj(_id="obj1")
        obj11 = MockRegObj(_id="obj1")
        obj2 = MockRegObj(_id="obj2")

        assert obj1 == obj11
        assert id(obj1) == id(obj11)
        assert obj1 == "obj1"
        assert obj1 != obj2
        assert "obj2" == obj2

    def test_eq1(self):
        obj1 = MockRegObj(_id="obj1")
        obj11 = MockRegObj(_id="obj_1")
        obj11._id = "obj1"
        obj2 = MockRegObj(_id="obj2")

        assert obj1 == obj11
        assert id(obj1) != id(obj11)
        assert obj1 == "obj1"
        assert obj1 != obj2
        assert "obj2" == obj2

    def test_neq_with_eq_id(self):
        obj1 = MockRegObj(_id="obj1")
        obj11 = MockRegObj(_id="obj2")
        obj11._attrs["test"] = "test"
        obj11._id = "obj1"

        assert obj1 != obj11
        assert obj1.id == obj11.id
        assert id(obj1) != id(obj11)

    # repo

    def test_load_with_cache(self):
        test_obj = MockRegObj(_id="test")
        result = MockRegObj.load("test", test_kw=1)

        assert result == test_obj
        MockRegObj.REPOSITORY.load.assert_not_called()

    def test_load_without_cache(self):
        test_obj = MockRegObj(_id="test")
        result = MockRegObj.load("test", test_kw=1, with_cache=False)

        assert result != test_obj
        MockRegObj.REPOSITORY.load.assert_called_once_with(
            MockRegObj.generate_path("test"), test_kw=1
        )

    def test_list(self):
        list_filter = {"filter": "test"}
        MockRegObj.list(list_filter, test_kw=1)
        MockRegObj.REPOSITORY.list.assert_called_once_with(
            MockRegObj.generate_path(""), list_filter=list_filter, test_kw=1
        )

    def test_refresh(self):
        obj = MockRegObj(_id="test")

        def raise_404(*_, **__):
            raise TethysRONotFound("404")

        obj.load = mock.MagicMock(side_effect=raise_404)

        result = obj.refresh(test_kw=1)

        obj.load.assert_called_once_with("test", test_kw=1, with_cache=False)
        assert result is None

    def test_save(self, validator):
        test_obj = MockRegObj(validator, _id="tst_test")
        obj = MockRegObj(validator, _id="test")

        obj.test0 = test_obj

        assert obj.save(test_kw=1) == obj

        obj.REPOSITORY.save.assert_has_calls(
            calls=[
                call(test_obj.path, test_obj, test_kw=1),
                call(obj.path, obj, test_kw=1),
            ]
        )

        validator.normalized.assert_has_calls(
            calls=[
                call({"test0": test_obj}),  # obj.test0 = test_obj
                call({"test0": obj._attrs["test0"]}),  # obj.save(test_kw=1)
                call({}),  # obj.save(test_kw=1) -> test_obj.save()
            ]
        )

    def test_save_without_deps(self, validator):
        test_obj = MockRegObj(validator, _id="tst_test")
        obj = MockRegObj(validator, _id="test")

        obj.test0 = test_obj

        assert obj.save(test_kw=1, save_dependency=False) == obj

        obj.REPOSITORY.save.assert_called_once_with(obj.path, obj, test_kw=1)

        validator.normalized.assert_has_calls(
            calls=[call({"test0": test_obj}), call({"test0": obj._attrs["test0"]})]
        )

    def test_delete(self):
        obj = MockRegObj(_id="test")

        assert obj.delete(test_kw=1) == obj

        obj.REPOSITORY.delete.assert_called_once_with(obj.path, test_kw=1)

    def test_lock(self):
        obj = MockRegObj(_id="test")

        obj.REPOSITORY.lock = mock.MagicMock(side_effect=lambda *_, **__: ...)

        assert obj.lock(test_kw=1) is ...

        obj.REPOSITORY.lock.assert_called_once_with(
            obj.path, blocking=True, lock_ttl=60, wait_timeout=float("inf"), test_kw=1
        )

    def test_unlock(self):
        obj = MockRegObj(_id="test")

        obj.REPOSITORY.unlock = mock.MagicMock(side_effect=lambda *_, **__: ...)

        assert obj.unlock(test_kw=1) is ...

        obj.REPOSITORY.unlock.assert_called_once_with(obj.path, test_kw=1)

    def test_lock_context(self):
        obj = MockRegObj(_id="test")

        with obj.lock_context(test_kw=1):
            obj.REPOSITORY.lock.assert_called_once_with(
                obj.path,
                blocking=True,
                lock_ttl=60,
                wait_timeout=float("inf"),
                test_kw=1,
            )
            obj.REPOSITORY.unlock.assert_not_called()

        obj.REPOSITORY.unlock.assert_called_once_with(obj.path)
