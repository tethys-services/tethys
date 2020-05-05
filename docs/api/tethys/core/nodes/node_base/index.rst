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

:mod:`tethys.core.nodes.node_base`
==================================

.. py:module:: tethys.core.nodes.node_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: NodeBase

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base abstract class for the Node

   .. method:: process(self, stream: StreamBase, **kwargs)
      :abstractmethod:


      Read the stream and execute an operator for the stream's data packet.

      :param stream: Stream that node will process
      :type stream: StreamBase
