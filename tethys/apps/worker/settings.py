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

import os

LOG_FORMAT = os.environ.get(
    "LOG_FORMAT",
    "[%(asctime)s] %(levelname)-5s - %(message)s | {%(pathname)s:%(lineno)d}",
)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")
LOG_ROOT_LEVEL = os.environ.get("LOG_ROOT_LEVEL", "ERROR")

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"tethys_main": {"format": LOG_FORMAT}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "tethys_main"}
    },
    "loggers": {
        "tethys": {"handler": ["console"], "level": LOG_LEVEL, "propagate": True}
    },
    "root": {"handlers": ["console"], "level": LOG_ROOT_LEVEL},
}
