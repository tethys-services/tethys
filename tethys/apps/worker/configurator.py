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
import yaml

from tethys.utils.imports import import_module


def _load_attrs_settings(obj):
    return {
        setting_key: getattr(obj, setting_key)
        for setting_key in dir(obj)
        if setting_key.isupper() and not setting_key.startswith("_")
    }


class Config(dict):
    def __getattr__(self, item):
        if str(item).isupper():
            try:
                return self[item]
            except KeyError:
                pass
        return self.__getattribute__(item)

    @classmethod
    def make_with(cls, custom_configs: dict = None):
        import tethys.apps.worker.settings as default_settings

        conf_dict = {}
        conf_dict.update(_load_attrs_settings(default_settings))
        if custom_configs:
            conf_dict.update({key.upper(): val for key, val in custom_configs.items()})

        return Config(conf_dict)


class ConfigsLoader:
    @classmethod
    def load(cls, fn):
        default_loaders = [JsonConfigsLoader, YamlConfigsLoader, PyConfigsLoader]

        swap_pos = 0
        if fn.endswith(".json"):
            swap_pos = default_loaders.index(JsonConfigsLoader)
        elif fn.endswith(".yaml") or fn.endswith(".yml"):
            swap_pos = default_loaders.index(YamlConfigsLoader)
        elif fn.endswith(".py"):
            swap_pos = default_loaders.index(PyConfigsLoader)

        if swap_pos:
            default_loaders[0], default_loaders[swap_pos] = (
                default_loaders[swap_pos],
                default_loaders[0],
            )

        for loader in default_loaders:
            try:
                return loader.load(fn)
            except ValueError:
                pass
        else:
            raise ValueError("{} file not supported".format(fn))


class JsonConfigsLoader(ConfigsLoader):
    @classmethod
    def load(cls, fn):
        with open(fn) as f:
            conf_dict = json.load(f)
            if not isinstance(conf_dict, dict):
                raise ValueError("Bad configs in {}. [is not dict]".format(fn))
            return Config.make_with(conf_dict)


class YamlConfigsLoader(ConfigsLoader):
    @classmethod
    def load(cls, fn):
        with open(fn) as f:
            conf_dict = yaml.full_load(f)
            if not isinstance(conf_dict, dict):
                raise ValueError("Bad configs in {}. [is not dict]".format(fn))
            return Config.make_with(conf_dict)


class PyConfigsLoader(ConfigsLoader):
    @classmethod
    def load(cls, fn):
        module = import_module(fn)
        if not module:
            raise ValueError("python module with configs not found")

        conf_dict = _load_attrs_settings(module)

        return Config.make_with(conf_dict)
