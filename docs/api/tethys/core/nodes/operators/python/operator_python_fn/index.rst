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

:mod:`tethys.core.nodes.operators.python.operator_python_fn`
============================================================

.. py:module:: tethys.core.nodes.operators.python.operator_python_fn


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: PythonFunctionOperator(callable_obj: Callable)

   Bases: :class:`tethys.core.nodes.operators.operator_base.OperatorBase`

   This operator just calls the python function.
   You can specify some reserved args in the function and args would be filled (like in the pytest fixtures).

   **Example:**
       .. code-block:: python

           def f1(data_packet, stream):
               print(stream)

           def f2(data_packet, station, stream):
               print(station, stream)

           def f3(data_packet, stream, station, operator):
               print(station, stream, operator)

           def f4():
               pass

           def f5(a, b, c):
               pass

           PythonFunctionOperator(f1)
           PythonFunctionOperator(f2)
           PythonFunctionOperator(f3)
           PythonFunctionOperator(f4)  # raise TypeError
           PythonFunctionOperator(f5)  # raise TypeError


   :param callable_obj: some callable object (function or instance with the __call__ magic method)
   :type callable_obj: Callable

   .. method:: args(self)
      :property:



   .. method:: process(self, data_packet: Any, stream: ZeroStream, **kwargs)


      Execute callable_obj with dynamic args.

      :param data_packet: any data object
      :param stream: Any stream
      :type stream: StreamBase
      :return: Result of the callable_obj execution
      :rtype: Any
