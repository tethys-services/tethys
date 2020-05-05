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

:mod:`tethys.core.streams.stream_base`
======================================

.. py:module:: tethys.core.streams.stream_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: StreamBase

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base abstract class for the Streams

   .. method:: is_busy(self)
      :property:


      Is some station using the stream?

      :rtype: bool


   .. method:: open(self, **kwargs)
      :abstractmethod:


      Open the stream

      :return: self instance
      :rtype: StreamBase


   .. method:: close(self, **kwargs)
      :abstractmethod:


      Close the stream

      :return: self instance
      :rtype: StreamBase


   .. method:: write(self, data_packet: Any, **kwargs)
      :abstractmethod:


      Write the data_packet to the stream

      :param data_packet: any data object


   .. method:: read(self, count: int = None, wait_timeout: float = None, **kwargs)
      :abstractmethod:


      Read the data_packets from the stream. Return Generator.

      :param count: count of the data_packets
      :type count: int
      :param wait_timeout: waiting time (seconds)
      :type wait_timeout: float


   .. method:: ack(self, message_key: str, **kwargs)
      :abstractmethod:


      Acknowledge message

      :param message_key: message key for the acknowledgement
      :type message_key: str


   .. method:: redirect_to(self, station: StationBase, **kwargs)
      :abstractmethod:


      Redirect stream processing to the station

      :param station: Station where the stream can be processed in the near time
      :type station: StationBase


   .. method:: heartbeat(self, **kwargs)
      :abstractmethod:


      Health heartbeat
