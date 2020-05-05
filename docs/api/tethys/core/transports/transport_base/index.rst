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

:mod:`tethys.core.transports.transport_base`
============================================

.. py:module:: tethys.core.transports.transport_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: TransportBase

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base abstract class for the Transport

   .. method:: is_connected(self, stream: StreamBase, **kwargs)
      :abstractmethod:


      Is the connection established

      :param stream: Stream for the connection
      :type stream: StreamBase
      :rtype: bool


   .. method:: connect(self, stream: StreamBase, **kwargs)
      :abstractmethod:


      Establish the connection

      :param stream: Stream for the connection
      :type stream: StreamBase


   .. method:: disconnect(self, stream: StreamBase, **kwargs)
      :abstractmethod:


      Disconnect the stream's connection

      :param stream: Stream for the connection
      :type stream: StreamBase


   .. method:: recv(self, stream: StreamBase, **kwargs)
      :abstractmethod:


      Read data_packet from the stream (using the current connection)

      :param stream: Stream for the connection
      :type stream: StreamBase


   .. method:: send(self, stream: StreamBase, data_packet: Any, **kwargs)
      :abstractmethod:


      Send data_packet to the stream (using connection)

      :param stream: Stream for the connection
      :type stream: StreamBase
      :param data_packet: any data object


   .. method:: ack(self, stream: StreamBase, message_key: str, **kwargs)
      :abstractmethod:


      Acknowledge message

      :param stream: Stream for the connection
      :type stream: StreamBase
      :param message_key: message key for the acknowledgement
      :type message_key: str
