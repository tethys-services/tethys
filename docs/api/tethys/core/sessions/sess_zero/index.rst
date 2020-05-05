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

:mod:`tethys.core.sessions.sess_zero`
=====================================

.. py:module:: tethys.core.sessions.sess_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: log
   

   

.. py:class:: ZeroSession(network: Union['ZeroNetwork', str], parent: ZeroSession = None, **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.sessions.sess_base.SessionBase`

   The Session entity class of the Zero generation.
   The ZeroSession is a context for the streams.


   :param network: The network used to run streams in the session scope.
   :type network: ZeroNetwork
   :param parent: The parent session
   :type parent: ZeroSession

   .. attribute:: SOFT_CLOSING_MODE
      :annotation: = <soft>

      

   .. attribute:: HARD_CLOSING_MODE
      :annotation: = <hard>

      

   .. attribute:: INSTANT_CLOSING_MODE
      :annotation: = <instant>

      

   .. attribute:: CLASS_PATH
      :annotation: = /sessions/

      :class:`ZeroSession` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroSession` fields validators


   .. method:: __setattr__(self, key, value)



   .. method:: add_child(self, child: ZeroSession)



   .. method:: remove_child(self, child: ZeroSession)



   .. method:: get_children_dict(self)



   .. method:: open(self, **kwargs)


      This method changes the ZeroSession station to `closed=False`.

      :return: self object
      :rtype: ZeroSession


   .. method:: close(self, mode: str = None)


      This method changes the ZeroSession station to `closing_mode=mode`.
      All children also will be closed.

      :param mode: closing mode determines the mode of closing streams (default: INSTANT_CLOSING_MODE)
      :type mode: str
      :return: self object
      :rtype: ZeroSession


   .. method:: send(self, data_packet: Any, many: bool = False, **kwargs)


      This method sends data_packet(s) to the input nodes.

      :param data_packet: any data object or list of the data objects (with many=True)
      :param many: if many=True then data_packet's elements will be sent one-by-one.
      :type many: bool


   .. method:: refresh(self, **kwargs)


      Reload entity from the repository (without cache).
      Also this method updates streams and sessions states according to the closing mode.

      :return: return ZeroSession instance or None (when error like NotFound)
      :rtype: ZeroSession or None


   .. method:: __enter__(self)



   .. method:: __exit__(self, exc_type, exc_val, exc_tb)
