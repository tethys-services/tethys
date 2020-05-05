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

:mod:`tethys.core.nodes.operators.files.operator_read_file`
===========================================================

.. py:module:: tethys.core.nodes.operators.files.operator_read_file


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: ReadFileOperator(path_generator: Callable = str, pack_size: int = None)

   Bases: :class:`tethys.core.nodes.operators.operator_base.OperatorBase`

   This operator reads a file (whole or part by part according to pack_size)

   :param path_generator: a function that generate the path to the file from the data_packet (default: str)
   :type path_generator: Callable
   :param pack_size: argument for the file.read(n) method (default: None)
   :type pack_size: int

   .. method:: process(self, data_packet: Any, stream: ZeroStream, **kwargs)


      Read the file and send data to the next nodes.

      :param data_packet: any data object
      :param stream: Any stream
      :type stream: StreamBase
      :return: None



.. py:class:: ReadFileLinesOperator(path_generator: Callable = str)

   Bases: :class:`tethys.core.nodes.operators.operator_base.OperatorBase`

   This operator reads a file line by line

   :param path_generator: a function that generate the path to the file from the data_packet (default: str)
   :type path_generator: Callable

   .. method:: process(self, data_packet: Any, stream: ZeroStream, **kwargs)


      Read the file line by line and send each line to the next nodes.

      :param data_packet: any data object
      :param stream: Any stream
      :type stream: StreamBase
      :return: None
