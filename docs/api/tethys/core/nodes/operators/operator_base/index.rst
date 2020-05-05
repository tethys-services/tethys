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

:mod:`tethys.core.nodes.operators.operator_base`
================================================

.. py:module:: tethys.core.nodes.operators.operator_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: OperatorBase

   Bases: :class:`serobj.utils.serobj_calls.SerobjCallsBase`

   Base abstract class for the Operator.

   .. method:: __getstate__(self)


      Serialize public attrs only


   .. method:: process(self, data_packet: Any, stream: StreamBase, message_key: str = None, **kwargs)
      :abstractmethod:


      Process one `data_packet`.

      :param data_packet: any data object
      :type data_packet: Any
      :param stream: any Stream instance
      :type stream: StreamBase
      :param message_key:
      :type message_key: str
      :return: next data_packet or None
      :rtype: Any
