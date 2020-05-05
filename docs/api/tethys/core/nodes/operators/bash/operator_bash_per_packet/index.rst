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

:mod:`tethys.core.nodes.operators.bash.operator_bash_per_packet`
================================================================

.. py:module:: tethys.core.nodes.operators.bash.operator_bash_per_packet


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: log
   

   

.. py:class:: BashPerPacketOperator(cmd: Union[Callable, str], env: Optional[Dict[str, str]] = None, preload_env: bool = False, return_stdout: bool = False)

   Bases: :class:`tethys.core.nodes.operators.operator_base.OperatorBase`

   This operator executes bash command for each data_packet.

   :param cmd: command as a string or a function that generates command.
       Function should except 2 args: fn(data_packet, stream)
   :type cmd: Union[Callable, str]
   :type env: dict of the environments variables (default: None)
   :param env: Optional[Dict[str, str]]
   :param preload_env: load env variables from the os.environ (default: False)
   :type preload_env: bool
   :param return_stdout: send stdout to the next nodes (default: False)
   :type return_stdout: bool

   .. method:: env(self)
      :property:



   .. method:: cmd(self, data_packet: Any, stream: ZeroStream)



   .. method:: process(self, data_packet: Any, stream: ZeroStream, **kwargs)


      Execute bash command.

      :param data_packet: any data object
      :param stream: Any stream
      :type stream: StreamBase
      :return: None
