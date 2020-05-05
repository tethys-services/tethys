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

:mod:`tethys.core.regobjs.regobj_base`
======================================

.. py:module:: tethys.core.regobjs.regobj_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: RegistrableObjectBase

   Bases: :class:`abc.ABC`

   Base abstract class for all entities that used like models for a database.

   .. method:: id(self)
      :property:



   .. method:: version(self)
      :property:



   .. method:: load(cls, expression: str, **kwargs)
      :classmethod:
      :abstractmethod:



   .. method:: list(cls, **kwargs)
      :classmethod:
      :abstractmethod:



   .. method:: save(self, **kwargs)
      :abstractmethod:



   .. method:: refresh(self, **kwargs)
      :abstractmethod:



   .. method:: delete(self, **kwargs)
      :abstractmethod:



   .. method:: lock(self, **kwargs)
      :abstractmethod:



   .. method:: unlock(self, **kwargs)
      :abstractmethod:
