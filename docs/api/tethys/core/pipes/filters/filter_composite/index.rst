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

:mod:`tethys.core.pipes.filters.filter_composite`
=================================================

.. py:module:: tethys.core.pipes.filters.filter_composite


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: CompositeFilter(*filters: FilterBase, function: Union[str, Callable] = '+')

   Bases: :class:`tethys.core.pipes.filters.filter_base.FilterBase`

   This filter aggregate scores from other filters and calculates a new score using a specific function.


   :param filters: list of the filters
   :type filters: FilterBase
   :param function: function for calculating an aggregated score.
       Available aliases: ["+", "*", "max", "min"].
       Default value: "+".
   :type function: Union[str, Callable]

   .. method:: execute(self, data_packet: Any, **kwargs)


      Execute each filter and after execute the function with the :class:`typing.Generator` (that contains the scores) argument.

      :param data_packet: any data object
      :return: calculated score (:class:`float`)
