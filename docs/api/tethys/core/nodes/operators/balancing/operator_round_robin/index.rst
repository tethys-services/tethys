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

:mod:`tethys.core.nodes.operators.balancing.operator_round_robin`
=================================================================

.. py:module:: tethys.core.nodes.operators.balancing.operator_round_robin


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: RoundRobinBalancerOperator

   Bases: :class:`tethys.core.nodes.operators.operator_base.OperatorBase`

   This operator distributes data_packets between forward nodes (with round-robin algorithm)

   .. method:: process(self, data_packet: Any, stream: ZeroStream, **kwargs)


      Resend data_packet to one of the forward nodes.

      :param data_packet: any data object
      :param stream: Any stream
      :type stream: StreamBase
      :return: None
