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

:mod:`tethys.core.pipes.pipe_zero`
==================================

.. py:module:: tethys.core.pipes.pipe_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: log
   

   

.. py:class:: ZeroPipe(node_a: Union[str, 'ZeroNode'], node_b: Union[str, 'ZeroNode'], filters: Iterable['FilterBase'] = None, filters_threshold: float = 0.5, transport: Optional[Union[str, Callable, 'ZeroTransport']] = ..., **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.pipes.pipe_base.PipeBase`

   The Pipe entity class of the Zero generation.
   The ZeroPipe connects two nodes and allows adding filters and transports.

   **Example:**
       .. code-block:: python

           def transport_factory_1(pipe, **kwargs):
               return CustomTransport1()

           # setting default transport in the context
           with ZeroPipe.transport_factory_context(transport_factory_1):

               pipe1 = ZeroPipe(
                   node_a="node1",  # ZeroPipe will load "node1" from a repository
                   node_b="node2",  # ZeroPipe will load "node2" from a repository
                   filters=[
                       CustomFilter(return_value=0.5)  # filter will return 0.5 score
                   ],
                   filters_threshold=0.4999,  # pipe send data if filters_score > filters_threshold
                   # transport=transport_factory_1()  # specified by the transport_factory_context
               )

               pipe2 = ZeroPipe(
                   node_a=node2,  # ZeroPipe will use exists node2 object
                   node_b=node1,  # ZeroPipe will use exists node1 object

                   # specify custom transport instead of the transport_factory_1
                   transport=CustomTransport2()
               )



   :param node_a: specify input node
   :type node_a: Union[str, ZeroNode]
   :param node_b: specify output node
   :type node_b: Union[str, ZeroNode]
   :param filters: list of the Filter instances (which inherits from abstract class `FilterBase`)
   :type filters: Iterable[FilterBase]
   :param filters_threshold: threshold for every filter's score in the filters list.
   :type filters_threshold: float
   :param transport: this is transport which will be default for every pipe's stream.
       If value == ... then transport_factory will be executed in the __init__.
       If value == None then transport_factory will be executed in the get_stream().
   :type transport: Union[str, Callable, ZeroTransport]

   .. attribute:: CLASS_PATH
      :annotation: = /pipes/

      :class:`ZeroPipe` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroPipe` fields validators


   .. method:: transport_factory_context(cls, transport_factory: Union[Callable, 'ZeroTransport'])
      :classmethod:


      Context manager for the :func:`set_transport_factory` method


   .. method:: set_transport_factory(cls, transport_factory: Union[Callable, 'ZeroTransport'])
      :classmethod:


      Set default transport factory. You can provide the ZeroTransport instances
      instead of Callable objects.

      :param transport_factory:
          any :class:`ZeroTransport <tethys.core.transports.transport_zero.ZeroTransport>` instance
          or any callable object that return the instance
      :type transport_factory: Union[Callable, ZeroTransport]


   .. method:: filter_data_packet(self, data_packet: Any, session: ZeroSession = None)


      Check all filters in the pipe. Return True
      if all filters return score that greater than filters_threshold


      :param data_packet: any data object
      :param session: optional param that extends context information
      :type session: ZeroSession
      :return: True or False, depends on the pipe's filters score.
      :rtype: bool


   .. method:: get_stream(self, session: ZeroSession)


      The method load or create ZeroStream instance according to pipe and session instances

      :param session: ZeroSession instance
      :type session: ZeroSession
      :return: ZeroStream instance that is attached to the pipe
      :rtype: ZeroStream


   .. method:: pull(self, session: ZeroSession, **kwargs)


      Get data_packets from the pipe's stream using python Generator
      (execute :func:`ZeroStream.read() <tethys.core.streams.stream_zero.ZeroStream.read>` method).

      :param session: ZeroSession instance
      :type session: ZeroSession
      :return: data_packets generator
      :rtype: typing.Generator


   .. method:: push(self, data_packet: Any, session: ZeroSession, many: bool = False, **kwargs)


      Send data_packet into the pipe's stream

      :param data_packet: any data object or list of the data objects (with many=True)
      :param session: ZeroSession instance
      :type session: ZeroSession
      :param many: if many=True then data_packet's elements will be sent one-by-one.
      :type many: bool
      :return: True or False, True if at least one data_packet has been sent
      :rtype: bool
