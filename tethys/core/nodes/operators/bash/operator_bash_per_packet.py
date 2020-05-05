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
import os
from subprocess import PIPE, STDOUT, Popen
from tempfile import NamedTemporaryFile
from typing import Callable, Dict, Optional, Union, TYPE_CHECKING, Any

from tethys.core.exceptions import TethysRuntimeError
from tethys.core.nodes.operators.operator_base import OperatorBase

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401


class BashPerPacketOperator(OperatorBase):
    """
    This operator executes bash command for each data_packet.
    """

    def __init__(
        self,
        cmd: Union[Callable, str],
        env: Optional[Dict[str, str]] = None,
        preload_env: bool = False,
        return_stdout: bool = False,
    ):
        """

        :param cmd: command as a string or a function that generates command.
            Function should except 2 args: fn(data_packet, stream)
        :type cmd: Union[Callable, str]
        :type env: dict of the environments variables (default: None)
        :param env: Optional[Dict[str, str]]
        :param preload_env: load env variables from the os.environ (default: False)
        :type preload_env: bool
        :param return_stdout: send stdout to the next nodes (default: False)
        :type return_stdout: bool
        """
        self._cmd = cmd
        self._env = env
        self._preload_env = preload_env
        self._return_stdout = return_stdout

    @property
    def env(self) -> dict:
        env = {}
        if self._preload_env:
            env.update(os.environ.copy())
        if self._env:
            env.update(self._env)
        return env

    def cmd(self, data_packet: Any, stream: "ZeroStream"):
        if isinstance(self._cmd, str):
            return self._cmd
        if callable(self._cmd):
            return self._cmd(data_packet, stream)

    def process(self, data_packet: Any, stream: "ZeroStream", **kwargs):
        """
        Execute bash command.

        :param data_packet: any data object
        :param stream: Any stream
        :type stream: StreamBase
        :return: None
        """
        cmd = self.cmd(data_packet, stream)

        with NamedTemporaryFile(prefix=stream.id) as tmp_file:
            tmp_file.write(bytes(cmd.encode("utf-8")))
            tmp_file.flush()

            log.debug("Bash node will execute: %s", cmd)

            process = Popen(
                ["bash", tmp_file.name], env=self.env, stdout=PIPE, stderr=STDOUT
            )

            process.wait()

            output = "\n".join(
                line.decode().rstrip() for line in iter(process.stdout.readline, b"")
            )

            log.info(
                "Bash node output for the `%s` command: [return code: %s]%s",
                cmd,
                process.returncode,
                output and "\n" + output,
            )

            if process.returncode:
                raise TethysRuntimeError("Bash command failed")

            if self._return_stdout:
                return output
