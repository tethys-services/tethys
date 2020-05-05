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

import errno
import fcntl
import os
import time
from typing import Union


class FLock:
    def __init__(
        self,
        path: str,
        timeout: Union[int, float] = None,
        delay: Union[int, float] = 0.5,
    ):
        self._f = None  # type: int

        self._path = path + ".lock"
        self._timeout = timeout
        self._delay = delay

    def __enter__(self) -> "FLock":
        self._f = os.open(self._path, os.O_CREAT)
        lock_ts = time.time()

        while True:
            try:
                fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, IOError) as ex:
                if ex.errno != errno.EAGAIN:
                    raise
                if self._timeout is not None and time.time() > (
                    lock_ts + self._timeout
                ):
                    raise

            time.sleep(self._delay)

        return self

    def __exit__(self, *args) -> None:
        fcntl.flock(self._f, fcntl.LOCK_UN)
        os.close(self._f)
        self._f = None
