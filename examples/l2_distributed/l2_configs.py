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

REPO_CONFIG = {
    "repo_params": ["mongodb://root:root@mongo:27017/l2_repo?authSource=admin"]
}

STATION_CONFIG = {
    "heartbeat_fail_delay": 10,
    "max_processes_count": int(os.environ.get("MAX_PROCESSES_COUNT", 1)),
}
