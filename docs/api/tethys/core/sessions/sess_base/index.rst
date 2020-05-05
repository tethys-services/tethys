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

:mod:`tethys.core.sessions.sess_base`
=====================================

.. py:module:: tethys.core.sessions.sess_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: log
   

   

.. py:class:: SessionBase

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base abstract class for the Sessions

   .. method:: open(self)
      :abstractmethod:


      Open the session


   .. method:: close(self, mode: str = None)
      :abstractmethod:


      Close the session


   .. method:: send(self, data_packet: Any)
      :abstractmethod:


      Send the data_packet to the input nodes
