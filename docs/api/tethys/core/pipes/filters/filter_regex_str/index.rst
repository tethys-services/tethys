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

:mod:`tethys.core.pipes.filters.filter_regex_str`
=================================================

.. py:module:: tethys.core.pipes.filters.filter_regex_str


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: RegexMatchFilter(expression: str, flags: int = 0)

   Bases: :class:`tethys.core.pipes.filters.filter_base.FilterBase`

   This filter use user's regular expressions with str(data_packet)


   :param expression: regex expression
   :type expression: str
   :param flags: flags from the 're' package (like re.IGNORECASE, re.MULTILINE)
   :type flags: int

   .. method:: execute(self, data_packet, **kwargs)


      Execute :func:`re.match` for the str(data_packet).

      :param data_packet: any data object
      :return: 1.0 or 0.0  (:class:`float`)
