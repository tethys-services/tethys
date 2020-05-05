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

from typing import Union, TYPE_CHECKING, Any, Callable

from tethys.core.nodes.node_base import NodeBase
from tethys.core.nodes.operators.operator_base import OperatorBase
from tethys.core.nodes.operators.python.operator_dummy import DummyOperator
from tethys.core.nodes.operators.python.operator_python_fn import PythonFunctionOperator
from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401
    from tethys.core.sessions.sess_zero import ZeroSession  # noqa: F401


class ZeroNode(ZeroRegistrableObject, NodeBase):
    """
    The Node entity class of the Zero generation.
    The ZeroNode is a unit that process data.

    **Example:**
        .. code-block:: python

            node1 = ZeroNode(
                operator=PythonFunctionOperator(some_fn)
            )
            node1.process(stream)
            node1.send(some_data)

    """

    IN = "<in>"
    "Virtual input gate node (CONSTANT)"

    OUT = "<out>"
    "Virtual output gate node (CONSTANT)"

    CLASS_PATH = "/nodes/"
    ":class:`ZeroNode` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "operator": {"type": "OperatorBase", "required": True},
    }
    ":class:`ZeroNode` fields validators"

    @classmethod
    def _get_extra_types(cls):
        # specify FIELDS_SCHEMA types
        return [OperatorBase]

    def __init__(self, operator: Union[OperatorBase, Callable] = ..., **kwargs):
        """

        :param operator: Operator instance which has a `process` method and which the Node executes.
        :type operator: OperatorBase
        """
        if isinstance(operator, Callable):
            operator = PythonFunctionOperator(operator)
        elif not operator or operator is ...:
            operator = DummyOperator()

        self.operator = operator

    def process(
        self,
        stream: Union["ZeroStream", str],
        wait_timeout: Union[int, float] = None,
        **kwargs
    ):
        """
        Read the stream and execute the operator for the stream's data packet.

        The node will stop the process if the stream closed or the stream's session closed.
        If operator return value (!= None)
        then the node will send the value to the connected nodes (forward direction)

        :param stream: Stream with which the node will work.
        :type stream: Union[ZeroStream, str]
        :param wait_timeout: pass to the `stream.read()` method
        :type wait_timeout: float
        """

        if isinstance(stream, str):
            from tethys.core.streams.stream_zero import ZeroStream  # noqa: F811

            stream = ZeroStream.load(stream)

        stream_iter = stream.read(wait_timeout=wait_timeout)
        for message_key, data_packet in stream_iter:
            if stream.closed or stream.session.closing_mode not in [
                None,
                stream.session.SOFT_CLOSING_MODE,
            ]:
                return

            result = self.operator.process(
                data_packet, stream, message_key=message_key, **kwargs
            )

            if result is not None:
                self.send(result, stream.session)

            stream.ack(message_key)

    def send(
        self, data_packet: Any, session: "ZeroSession", many: bool = False, **kwargs
    ):
        """
        Send data_packet to the connected nodes through streams (forward direction) in the session context.

        :param data_packet: any data object or list of the data objects (with many=True)
        :param session: ZeroSession instance
        :type session: ZeroSession
        :param many: if many=True then data_packet's elements will be sent one-by-one.
        :type many: bool
        """

        network = session.network
        pipes_nodes = network.get_pipes_map()[self.id]

        for b_node_pipes in pipes_nodes.values():
            for pipe in b_node_pipes.values():
                pipe.push(data_packet, session, many=many, **kwargs)
