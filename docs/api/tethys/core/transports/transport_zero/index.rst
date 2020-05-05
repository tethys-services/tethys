 .. Copyright 2020 Konstruktor, Inc. All Rights Reserved.

 .. Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

:mod:`tethys.core.transports.transport_zero`
============================================

.. py:module:: tethys.core.transports.transport_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: ZeroTransport(connector: Union['ConnectorBase', Callable] = LocalConnector(), connections_factory: Callable = None, serializer: Callable = None, deserializer: Callable = None, **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.transports.transport_base.TransportBase`

   The Transport entity class of the Zero generation.
   The ZeroTransport is an entity that defines the connection interface.


   :param connector: Connector instance that creates a connection
       to the data exchange system (e.g. queues broker).
   :type connector: Union[ConnectorBase, Callable]
   :param connections_factory: Factory method for the connection interfaces.
   :type connections_factory: Callable
   :param serializer: Serialization function
   :type serializer: Callable
   :param deserializer: Deserialization function
   :type deserializer: Callable

   .. attribute:: CLASS_PATH
      :annotation: = /transports/

      :class:`ZeroTransport` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroTransport` fields validators


   .. attribute:: RECV_DELAY
      :annotation: = 0.1

      

   .. method:: is_connected(self, stream: ZeroStream, **kwargs)


      Is the connection established

      :param stream: Stream for the connection
      :type stream: StreamBase
      :rtype: bool


   .. method:: connect(self, stream: ZeroStream, **kwargs)


      Establish the connection

      :param stream: Stream for the connection
      :type stream: StreamBase


   .. method:: disconnect(self, stream: ZeroStream, **kwargs)


      Disconnect the stream's connection

      :param stream: Stream for the connection
      :type stream: StreamBase


   .. method:: recv(self, stream: ZeroStream, wait_timeout: float = None, **kwargs)


      Read data_packet from the stream (using connection)

      :param stream: Stream for the connection
      :type stream: StreamBase
      :param wait_timeout: waiting time (seconds)
      :type wait_timeout: float


   .. method:: send(self, stream: ZeroStream, data_packet: Any, **kwargs)


      Send data_packet to the stream (using connection)

      :param stream: Stream for the connection
      :type stream: StreamBase
      :param data_packet: any data object


   .. method:: ack(self, stream: ZeroStream, message_key: str, **kwargs)


      Acknowledge message

      :param stream: Stream for the connection
      :type stream: StreamBase
      :param message_key: message key for the acknowledgement
      :type message_key: str
