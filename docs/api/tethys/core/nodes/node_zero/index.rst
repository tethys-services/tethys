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

:mod:`tethys.core.nodes.node_zero`
==================================

.. py:module:: tethys.core.nodes.node_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: ZeroNode(operator: Union[OperatorBase, Callable] = ..., **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.nodes.node_base.NodeBase`

   The Node entity class of the Zero generation.
   The ZeroNode is a unit that process data.

   **Example:**
       .. code-block:: python

           node1 = ZeroNode(
               operator=PythonFunctionOperator(some_fn)
           )
           node1.process(stream)
           node1.send(some_data)


   :param operator: Operator instance which has a `process` method and which the Node executes.
   :type operator: OperatorBase

   .. attribute:: IN
      :annotation: = <in>

      Virtual input gate node (CONSTANT)


   .. attribute:: OUT
      :annotation: = <out>

      Virtual output gate node (CONSTANT)


   .. attribute:: CLASS_PATH
      :annotation: = /nodes/

      :class:`ZeroNode` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroNode` fields validators


   .. method:: process(self, stream: Union['ZeroStream', str], wait_timeout: Union[int, float] = None, **kwargs)


      Read the stream and execute the operator for the stream's data packet.

      The node will stop the process if the stream closed or the stream's session closed.
      If operator return value (!= None)
      then the node will send the value to the connected nodes (forward direction)

      :param stream: Stream with which the node will work.
      :type stream: Union[ZeroStream, str]
      :param wait_timeout: pass to the `stream.read()` method
      :type wait_timeout: float


   .. method:: send(self, data_packet: Any, session: ZeroSession, many: bool = False, **kwargs)


      Send data_packet to the connected nodes through streams (forward direction) in the session context.

      :param data_packet: any data object or list of the data objects (with many=True)
      :param session: ZeroSession instance
      :type session: ZeroSession
      :param many: if many=True then data_packet's elements will be sent one-by-one.
      :type many: bool
