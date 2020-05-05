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

:mod:`tethys.core.regobjs.repositories.repo_mongo`
==================================================

.. py:module:: tethys.core.regobjs.repositories.repo_mongo


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: LOCK_CHECK_DELAY
   :annotation: = 0.1

   

.. data:: FILTER_MONGO_MAP
   

   

.. py:class:: MongodbRepository(uri: str, collection_prefix: str = 'repo', object_key_field: str = 'key')

   Bases: :class:`tethys.core.regobjs.repositories.repo_base.RepositoryBase`

   .. method:: database(self)
      :property:
