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

:mod:`tethys.apps.worker.configurator`
======================================

.. py:module:: tethys.apps.worker.configurator


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: Config

   Bases: :class:`dict`

   .. method:: __getattr__(self, item)



   .. method:: make_with(cls, custom_configs: dict = None)
      :classmethod:




.. py:class:: ConfigsLoader

   .. method:: load(cls, fn)
      :classmethod:




.. py:class:: JsonConfigsLoader

   Bases: :class:`tethys.apps.worker.configurator.ConfigsLoader`

   .. method:: load(cls, fn)
      :classmethod:




.. py:class:: YamlConfigsLoader

   Bases: :class:`tethys.apps.worker.configurator.ConfigsLoader`

   .. method:: load(cls, fn)
      :classmethod:




.. py:class:: PyConfigsLoader

   Bases: :class:`tethys.apps.worker.configurator.ConfigsLoader`

   .. method:: load(cls, fn)
      :classmethod:
