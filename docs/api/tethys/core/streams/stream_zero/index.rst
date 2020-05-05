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

:mod:`tethys.core.streams.stream_zero`
======================================

.. py:module:: tethys.core.streams.stream_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: log
   

   

.. py:class:: ZeroStream(pipe: ZeroPipe, session: ZeroSession, transport: Union['ZeroTransport', Callable], **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.streams.stream_base.StreamBase`

   The Stream entity class of the Zero generation.
   The ZeroStream is an entity that defines the physical path of the data.


   :param pipe: Pipe instance that defines the logical path between nodes.
   :type pipe: ZeroPipe
   :param session: The session allows getting the stream for the pipe.
   :type session: ZeroSession
   :param transport:

   .. attribute:: DEFAULT_HEARTBEAT_FAIL_DELAY
      :annotation: = 10

      

   .. attribute:: READ_DELAY
      :annotation: = 0.1

      

   .. attribute:: CLASS_PATH
      :annotation: = /streams/

      :class:`ZeroStream` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroStream` fields validators


   .. method:: connection_context(self)



   .. method:: heartbeat_fail_delay(self)
      :property:



   .. method:: is_busy(self)
      :property:


      Is some station using the stream?

      :rtype: bool


   .. method:: open(self, save=True, **kwargs)


      Open stream

      :param save: to save the stream
      :type save: bool
      :return: self instance
      :rtype: StreamBase


   .. method:: close(self, save=True, **kwargs)


      Close stream

      :param save: to save the stream
      :type save: bool
      :return: self instance
      :rtype: StreamBase


   .. method:: write(self, data_packet: Union[List[Any], Any], many: bool = False, **kwargs)


      Write the data_packet to the stream

      :param data_packet: any data object or list of the data objects (with many=True)
      :param many: if many=True then data_packet's elements will be sent one-by-one.
      :type many: bool


   .. method:: read(self, count: int = None, wait_timeout: float = None, **kwargs)


      Read the data_packets from the stream. Return Generator.

      :param count: count of the data_packets
      :type count: int
      :param wait_timeout: waiting time (seconds)
      :type wait_timeout: float


   .. method:: ack(self, message_key: str, **kwargs)


      Acknowledge message

      :param message_key: message key for the acknowledgement
      :type message_key: str


   .. method:: redirect_to(self, station: ZeroStation, **kwargs)


      Redirect stream processing to the station

      :param station: Station where the stream can be processed in the near time
      :type station: ZeroStation


   .. method:: heartbeat(self, **kwargs)


      Health heartbeat


   .. method:: __enter__(self)



   .. method:: __exit__(self, exc_type, exc_val, exc_tb)
