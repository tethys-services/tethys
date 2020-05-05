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

:mod:`tethys.core.networks.network_zero`
========================================

.. py:module:: tethys.core.networks.network_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: ZeroNetwork(*pipes: Union[Iterable[Union['ZeroPipe', str]], Union['ZeroPipe', str]], **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.networks.network_base.NetworkBase`

   The Network entity class of the Zero generation.
   The ZeroNetwork is a container of the Pipes.

   **Example:**
       .. code-block:: python

           pipe1 = ZeroPipe(
               node_a=node1,
               node_b=node2
           )

           pipe2 = ZeroPipe(
               node_a=node2,
               node_b=node1
           )

           pipe3 = ZeroPipe(
               node_a=node3,
               node_b=node1
           )

           pipe4 = ZeroPipe(
               node_a=node3,
               node_b=node2
           )

           network_template = ZeroNetwork([pipe1, pipe2])

           network = ZeroNetwork()
           network.add_pipes(pipe3, pipe4)

           result_network = network_template + network


   :param pipes: list of args of the pipes (str or PipeZero instances) - can be empty
   :type pipes: Iterable[Union[ZeroPipe, str]

   .. attribute:: CLASS_PATH
      :annotation: = /networks/

      :class:`ZeroNetwork` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroNetwork` fields validators


   .. method:: pipes(self)
      :property:



   .. method:: input_nodes(self)
      :property:


      It returns `input nodes`

      Example:
          <in> ---> **Node1** ---> Node2 ---> <out>

          **Node1** - input node

      :return: list of the input nodes
      :rtype: Iterable[ZeroNode]


   .. method:: output_nodes(self)
      :property:


      It returns `output nodes`

      Example:
          <in> ---> Node1 ---> **Node2** ---> <out>

          **Node2** - output node (because --> <out>)

      :return: list of the output nodes
      :rtype: Iterable[ZeroNode]


   .. method:: input_pipes(self)
      :property:


      It returns `input pipes`

      Example:
          <in> **--pipe1-->** N --pipe2--> N --pipe3--> <out>

          **pipe1** - input pipe

      :return: list of the input pipes
      :rtype: Iterable[ZeroPipe]


   .. method:: output_pipes(self)
      :property:


      It returns `input pipes`

      Example:
          <in> --pipe1--> N --pipe2--> N **--pipe3-->** <out>  **<--pipe4--** N

          **pipe3** and **pipe4** - output pipes

      :return: list of the output pipes
      :rtype: Iterable[ZeroPipe]


   .. method:: get_forward_pipes(self, pipe_or_node: Union[ZeroNode, ZeroPipe])


      Get all pipes that go after the `pipe_or_node` instance.

      Example:
          <in> --p1--> N1 --p2--> N2 --p3--> <out>

          If p1 or N1 - target instance (`pipe_or_node`) then p2- forward pipe

      :param pipe_or_node: specify target pipe or node
      :type pipe_or_node: Union[ZeroNode, ZeroPipe]
      :return: all pipes after the `pipe_or_node`
      :rtype: Iterator[ZeroPipe]


   .. method:: get_backward_pipes(self, pipe_or_node: Union[ZeroNode, ZeroPipe])


      Get all pipes that go after the `pipe_or_node` instance.

      Example:
          <in> --p1--> N1 --p2--> N2 --p4--> <out>

          If N1 or p2 - target instance (`pipe_or_node`) then p1 - backward pipe

      :param pipe_or_node: specify target pipe or node
      :type pipe_or_node: Union[ZeroNode, ZeroPipe]
      :return: all pipes before the `pipe_or_node`
      :rtype: Iterator[ZeroPipe]


   .. method:: get_pipes_map(self, reverse: bool = False, **kwargs)


      It returns `pipes map` like 3d array

      :param reverse: if true then 3d array -> map["node_b_id"]["node_a_id"]["pipe_id"]
      :type reverse: bool
      :return: return 3d array -> map["node_a_id"]["node_b_id"]["pipe_id"] = ZeroPipe()
      :rtype: Dict[str, Dict[str, Dict[str, ZeroPipe]]]


   .. method:: add_pipes(self, *pipes: Union[Iterable[Union[ZeroPipe, str]], Union[ZeroPipe, str]])


      It adds pipes to the ZeroNetwork instance

      :param pipes: list of args of the pipes (str or ZeroPipe instances)
      :type pipes: Iterable[Union[ZeroPipe, str]


   .. method:: remove_pipes(self, *pipes: Union[Iterable[Union['ZeroPipe', str]], Union['ZeroPipe', str]])


      It removes pipes from the Network

      :param pipes: list of args of the pipes (str or ZeroPipe instances)
      :type pipes: Iterable[Union[ZeroPipe, str]]


   .. method:: save(self, save_dependency: bool = True, **kwargs)



   .. method:: __eq__(self, other: Any)



   .. method:: __ne__(self, other: Any)



   .. method:: __add__(self, other: ZeroNetwork)



   .. method:: __iadd__(self, other: ZeroNetwork)



   .. method:: __sub__(self, other: ZeroNetwork)



   .. method:: __isub__(self, other: ZeroNetwork)



   .. method:: __and__(self, other: ZeroNetwork)



   .. method:: __iand__(self, other: ZeroNetwork)



   .. method:: __or__(self, other: ZeroNetwork)



   .. method:: __ior__(self, other: ZeroNetwork)
