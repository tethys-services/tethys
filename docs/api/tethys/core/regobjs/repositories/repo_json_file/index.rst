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

:mod:`tethys.core.regobjs.repositories.repo_json_file`
======================================================

.. py:module:: tethys.core.regobjs.repositories.repo_json_file


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: JsonFileRepository(f_path: str = None, create: bool = False, storage: dict = None, buff_2: bool = True)

   Bases: :class:`tethys.core.regobjs.repositories.repo_local.LocalRepository`

   .. py:class:: ProxyStorage(self_obj: JsonFileRepository)

      Bases: :class:`dict`

      .. method:: __setitem__(self, key, value)



      .. method:: __delitem__(self, key)
