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

:mod:`tethys.core.transports.connectors.connector_dummy`
========================================================

.. py:module:: tethys.core.transports.connectors.connector_dummy


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: DummyConnection(recv_iter_data_packet: Iterable)

   Bases: :class:`tethys.core.transports.connectors.connector_base.ConnectionBase`

   .. method:: recv_iter(self, **kwargs)



   .. method:: send(self, data_obj, **kwargs)



   .. method:: ack(self, message_key, **kwargs)



   .. method:: open(self, **kwargs)



   .. method:: close(self, **kwargs)




.. py:class:: DummyConnector(recv_iter_data_packet: Iterable = None)

   Bases: :class:`tethys.core.transports.connectors.connector_base.ConnectorBase`

   .. method:: connect(self, _, **kwargs)
