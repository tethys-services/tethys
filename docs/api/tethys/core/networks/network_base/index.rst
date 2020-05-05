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

:mod:`tethys.core.networks.network_base`
========================================

.. py:module:: tethys.core.networks.network_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: NetworkBase

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base abstract class for the Networks

   .. method:: input_nodes(self)
      :property:


      It returns `input nodes` [abstract property]

      Example:
          <in> ---> **Node1** ---> Node2 ---> <out>

          **Node1** - input node

      :return: list of the input nodes
      :rtype: Iterable[NodeBase]


   .. method:: output_nodes(self)
      :property:


      It returns `output nodes` [abstract property]

      Example:
          <in> ---> Node1 ---> **Node2** ---> <out>

          **Node2** - output node (because --> <out>)

      :return: list of the output nodes
      :rtype: Iterable[NodeBase]


   .. method:: input_pipes(self)
      :property:


      It returns `input pipes` [abstract property]

      Example:
          <in> **--pipe1-->** N --pipe2--> N --pipe3--> <out>

          **pipe1** - input pipe

      :return: list of the input pipes
      :rtype: Iterable[PipeBase]


   .. method:: output_pipes(self)
      :property:


      It returns `input pipes` [abstract property]

      Example:
          <in> --pipe1--> N --pipe2--> N **--pipe3-->** <out>  **<--pipe4--** N

          **pipe3** and **pipe4** - output pipes

      :return: list of the output pipes
      :rtype: Iterable[PipeBase]


   .. method:: get_pipes_map(self, reverse: bool = False, **kwargs)
      :abstractmethod:


      It returns `pipes map` like 3d array

      :param reverse: if true then 3d array -> map["node_b_id"]["node_a_id"]["pipe_id"]
      :type reverse: bool
      :return: return 3d array -> map["node_a_id"]["node_b_id"]["pipe_id"] = PipeBase()
      :rtype: Dict[str, Dict[str, Dict[str, PipeBase]]]


   .. method:: add_pipes(self, *pipes: Iterable[Union['PipeBase', str]], **kwargs)
      :abstractmethod:


      It adds pipes to the Network

      :param pipes: list of args of the pipes (str or PipeBase instances)
      :type pipes: Iterable[Union[PipeBase, str]]


   .. method:: remove_pipes(self, *pipes: Iterable[Union['PipeBase', str]], **kwargs)
      :abstractmethod:


      It removes pipes from the Network

      :param pipes: list of args of the pipes (str or PipeBase instances)
      :type pipes: Iterable[Union[PipeBase, str]]
