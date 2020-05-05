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

from typing import Callable, TYPE_CHECKING, Any

from tethys.core.nodes.operators.operator_base import OperatorBase

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401


class ReadFileOperator(OperatorBase):
    """
    This operator reads a file (whole or part by part according to pack_size)
    """

    def __init__(self, path_generator: Callable = str, pack_size: int = None):
        """

        :param path_generator: a function that generate the path to the file from the data_packet (default: str)
        :type path_generator: Callable
        :param pack_size: argument for the file.read(n) method (default: None)
        :type pack_size: int
        """
        self._path_generator = path_generator
        self._pack_size = pack_size

    def process(self, data_packet: Any, stream: "ZeroStream", **kwargs):
        """
        Read the file and send data to the next nodes.

        :param data_packet: any data object
        :param stream: Any stream
        :type stream: StreamBase
        :return: None
        """

        node = stream.pipe.node_b

        with open(self._path_generator(data_packet)) as f:
            if self._pack_size is None:
                return f.read()
            else:
                data = f.read(self._pack_size)
                while data:
                    node.send(data, stream.session)
                    data = f.read(self._pack_size)


class ReadFileLinesOperator(OperatorBase):
    """
    This operator reads a file line by line
    """

    def __init__(self, path_generator: Callable = str):
        """

        :param path_generator: a function that generate the path to the file from the data_packet (default: str)
        :type path_generator: Callable
        """

        self._path_generator = path_generator

    def process(self, data_packet: Any, stream: "ZeroStream", **kwargs):
        """
        Read the file line by line and send each line to the next nodes.

        :param data_packet: any data object
        :param stream: Any stream
        :type stream: StreamBase
        :return: None
        """

        node = stream.pipe.node_b

        with open(self._path_generator(data_packet)) as f:
            data = f.readline()
            while data:
                node.send(data, stream.session)
                data = f.readline()
