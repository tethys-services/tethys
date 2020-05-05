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

:mod:`tethys.core.pipes.pipe_base`
==================================

.. py:module:: tethys.core.pipes.pipe_base


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. py:class:: PipeBase

   Bases: :class:`tethys.core.regobjs.regobj_base.RegistrableObjectBase`

   Base abstract class for the Pipes

   .. method:: get_stream(self, session: SessionBase)
      :abstractmethod:


      Get or create stream

      :param session: Session instance
      :type session: SessionBase
      :return: Stream instance
      :rtype: StreamBase


   .. method:: pull(self, session: SessionBase, **kwargs)
      :abstractmethod:


      Get data_packets from the pipe's stream using python Generator

      :param session: Session instance
      :type session: SessionBase
      :return: data_packets generator
      :rtype: typing.Generator


   .. method:: push(self, data_packet: Any, session: SessionBase, **kwargs)
      :abstractmethod:


      Push data to the pipe's stream

      :param data_packet: any data object or list of the data objects (with many=True)
      :param session: ZeroSession instance
      :type session: ZeroSession
