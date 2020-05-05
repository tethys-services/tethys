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

import time
from typing import Callable, Union, Any, TYPE_CHECKING, Tuple

from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject
from tethys.core.transports.connectors import (
    LocalConnector,
    ConnectorBase,
    ConnectionBase,
)
from tethys.core.transports.transport_base import TransportBase

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401


def _pass(x):
    return x


class ZeroTransport(ZeroRegistrableObject, TransportBase):
    """
    The Transport entity class of the Zero generation.
    The ZeroTransport is an entity that defines the connection interface.

    """

    CLASS_PATH = "/transports/"
    ":class:`ZeroTransport` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "connector": {"type": ["ConnectorBase", "Callable"], "required": True},
        "connections_factory": {
            "type": "Callable",
            "required": False,
            "nullable": True,
            "default": None,
        },
        "serializer": {"type": "Callable", "required": True},
        "deserializer": {"type": "Callable", "required": True},
    }
    ":class:`ZeroTransport` fields validators"

    RECV_DELAY = 0.1

    _connections = {}

    @classmethod
    def _get_extra_types(cls):
        Callable.__name__ = "Callable"
        return [ConnectorBase, Callable]

    def __init__(
        self,
        connector: Union["ConnectorBase", Callable] = LocalConnector(),
        connections_factory: Callable = None,
        serializer: Callable = None,
        deserializer: Callable = None,
        **kwargs
    ):
        """

        :param connector: Connector instance that creates a connection
            to the data exchange system (e.g. queues broker).
        :type connector: Union[ConnectorBase, Callable]
        :param connections_factory: Factory method for the connection interfaces.
        :type connections_factory: Callable
        :param serializer: Serialization function
        :type serializer: Callable
        :param deserializer: Deserialization function
        :type deserializer: Callable
        """

        self.connector = connector
        self.connections_factory = connections_factory

        self.serializer = serializer or _pass
        self.deserializer = deserializer or _pass

    def is_connected(self, stream: "ZeroStream", **kwargs) -> bool:
        """
        Is the connection established

        :param stream: Stream for the connection
        :type stream: StreamBase
        :rtype: bool
        """

        return stream.id in self._connections

    def connect(self, stream: "ZeroStream", **kwargs) -> ConnectionBase:
        """
        Establish the connection

        :param stream: Stream for the connection
        :type stream: StreamBase
        """

        if stream.id in self._connections:
            return self._connections[stream.id]

        if isinstance(self.connector, ConnectorBase):
            connector = self.connector
        else:
            connector = self.connector(self, stream=stream)

        if self.connections_factory:
            connection = self.connections_factory(connector, stream=stream)
        else:
            connection = connector.connect(stream.id, **kwargs)

        self._connections[stream.id] = connection

        return connection

    def disconnect(self, stream: "ZeroStream", **kwargs):
        """
        Disconnect the stream's connection

        :param stream: Stream for the connection
        :type stream: StreamBase
        """

        self._connections[stream.id].close()
        del self._connections[stream.id]

    def recv(
        self, stream: "ZeroStream", wait_timeout: float = None, **kwargs
    ) -> Union[Tuple[str, Any], None]:
        """
        Read data_packet from the stream (using connection)

        :param stream: Stream for the connection
        :type stream: StreamBase
        :param wait_timeout: waiting time (seconds)
        :type wait_timeout: float
        """

        connection = self._connections[stream.id]

        if wait_timeout is None:
            next_timeout = float("inf")
        elif wait_timeout <= 0:
            next_timeout = 0
        else:
            next_timeout = time.time() + wait_timeout

        iterator = connection.recv_iter()

        while not next_timeout or time.time() < next_timeout:
            if stream and stream.closed:
                break

            try:
                next_message = next(iterator)

                if not next_message:
                    break

                key, message = next_message

                return key, self.deserializer(message)

            except StopIteration:
                if not next_timeout:
                    break

                iterator = connection.recv_iter()

                time.sleep(self.RECV_DELAY)

        return None

    def send(self, stream: "ZeroStream", data_packet: Any, **kwargs):
        """
        Send data_packet to the stream (using connection)

        :param stream: Stream for the connection
        :type stream: StreamBase
        :param data_packet: any data object
        """

        connection = self._connections[stream.id]
        connection.send(self.serializer(data_packet), **kwargs)

    def ack(self, stream: "ZeroStream", message_key: str, **kwargs):
        """
        Acknowledge message

        :param stream: Stream for the connection
        :type stream: StreamBase
        :param message_key: message key for the acknowledgement
        :type message_key: str
        """

        connection = self._connections[stream.id]
        connection.ack(message_key, **kwargs)
