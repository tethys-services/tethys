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

:mod:`tethys.core.transports.connectors.connector_base`
=======================================================

.. py:module:: tethys.core.transports.connectors.connector_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: ConnectionBase

   Bases: :class:`abc.ABC`

   .. method:: recv_iter(self, **kwargs)
      :abstractmethod:



   .. method:: send(self, data_packet: Any, **kwargs)
      :abstractmethod:



   .. method:: ack(self, message_key: str, **kwargs)
      :abstractmethod:



   .. method:: open(self)
      :abstractmethod:



   .. method:: close(self)
      :abstractmethod:




.. py:class:: ConnectorBase

   Bases: :class:`serobj.utils.serobj_calls.SerobjCallsBase`

   .. method:: connect(self, channel_id: str, *args, **kwargs)
      :abstractmethod:
