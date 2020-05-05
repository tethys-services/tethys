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

from inspect import Signature
from typing import Callable, Any, TYPE_CHECKING

from tethys.core.nodes.operators.operator_base import OperatorBase

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401


def _get_args_by_sig(callable_obj):
    args = []
    try:
        sig = Signature.from_callable(callable_obj)
    except Exception:
        return args

    for p in sig.parameters.values():
        if p.kind in [p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY, p.VAR_KEYWORD]:
            args.append(p.name)

    return args


class PythonFunctionOperator(OperatorBase):
    """
    This operator just calls the python function.
    You can specify some reserved args in the function and args would be filled (like in the pytest fixtures).

    **Example:**
        .. code-block:: python

            def f1(data_packet, stream):
                print(stream)

            def f2(data_packet, station, stream):
                print(station, stream)

            def f3(data_packet, stream, station, operator):
                print(station, stream, operator)

            def f4():
                pass

            def f5(a, b, c):
                pass

            PythonFunctionOperator(f1)
            PythonFunctionOperator(f2)
            PythonFunctionOperator(f3)
            PythonFunctionOperator(f4)  # raise TypeError
            PythonFunctionOperator(f5)  # raise TypeError

    """

    def __init__(self, callable_obj: Callable):
        """

        :param callable_obj: some callable object (function or instance with the __call__ magic method)
        :type callable_obj: Callable
        """
        self._callable = callable_obj
        self._args = None

    @property
    def args(self):
        if getattr(self, "_args", None) is None:
            self._args = _get_args_by_sig(self._callable)
        return self._args

    def process(self, data_packet: Any, stream: "ZeroStream", **kwargs):
        """
        Execute callable_obj with dynamic args.

        :param data_packet: any data object
        :param stream: Any stream
        :type stream: StreamBase
        :return: Result of the callable_obj execution
        :rtype: Any
        """
        args = {}

        for p in self.args:
            if p == "station":
                args[p] = stream.station
            if p == "stream":
                args[p] = stream
            if p == "session":
                args[p] = stream.session
            if p == "network":
                args[p] = stream.session.network
            if p == "pipe":
                args[p] = stream.pipe
            if p == "node_a":
                args[p] = stream.pipe.node_a
            if p == "node" or p == "node_b":
                args[p] = stream.pipe.node_b
            if p == "operator":
                args[p] = self
            if p in kwargs:
                args[p] = kwargs[p]

        return self._callable(data_packet, **args)
