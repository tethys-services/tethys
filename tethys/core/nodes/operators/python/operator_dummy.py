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

from typing import Any, TYPE_CHECKING

from tethys.core.nodes.operators.operator_base import OperatorBase

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401


class DummyOperator(OperatorBase):
    """
    This operator just return data_packet (resend)

    **Example:**
        .. code-block:: python

            assert DummyOperator().process("some_data", ...) == "some_data"

    """

    def __init__(self, echo=True):
        self._echo = echo

    def process(self, data_packet: Any, stream: "ZeroStream", **kwargs):
        """
        Execute callable_obj with dynamic args.

        :param data_packet: any data object
        :param stream: Any stream
        :type stream: StreamBase
        :return: data_packet
        """
        if self._echo:
            return data_packet
