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

:mod:`tethys.core.stations.station_zero`
========================================

.. py:module:: tethys.core.stations.station_zero


.. toctree::
   :titlesonly:
   :maxdepth: 3


Module Contents
---------------


.. data:: log
   

   

.. py:class:: ZeroStation(sessions: List[SessionBase] = None, networks: List[NetworkBase] = None, pipes: List[PipeBase] = None, nodes_a: List[NodeBase] = None, nodes_b: List[NodeBase] = None, to_shuffle_stream: bool = False, stream_lock_ttl: float = 1, stream_lock_blocking: bool = False, stream_waiting_timeout: float = None, max_processes_count: int = 1, monitor_checks_delay: float = 1, update_min_delay: float = 1, heartbeat_fail_delay: float = 60, process_start_callback: Callable = None, process_stop_callback: Callable = None, process_error_callback: Callable = None, spawn_process_start_callback: Callable = None, spawn_process_stop_callback: Callable = None, spawn_process_error_callback: Callable = None, **kwargs)

   Bases: :class:`tethys.core.regobjs.regobj_zero.ZeroRegistrableObject`, :class:`tethys.core.stations.station_base.StationBase`

   The Station entity class of the Zero generation.
   The ZeroStation is a worker that processes streams data.


   :param sessions: Sessions that will be processed in the station
   :type sessions: Iterable[ZeroSession]
   :param networks: Networks that will be processed in the station
   :type networks: Iterable[ZeroNetwork]
   :param pipes: Pipes that will be processed in the station
   :type pipes: Iterable[ZeroPipe]
   :param nodes_a: Input nodes (bode_a) that will be processed in the station
   :type nodes_a: Iterable[ZeroNode]
   :param nodes_b: Output nodes that will be processed in the station
   :type nodes_b: Iterable[ZeroNode]

   :param to_shuffle_stream: To shuffle streams list in the waiting process
   :type to_shuffle_stream: bool
   :param stream_lock_ttl: Stream lock timeout in the try_stream function
   :type stream_lock_ttl: float
   :param stream_lock_blocking: Block lock acquire in the try_stream function (affects the streams order)
   :type stream_lock_blocking: bool
   :param stream_waiting_timeout: How long do streams instances wait for data
   :type stream_waiting_timeout: float

   :param max_processes_count: The max count multiprocessing processes
   :type max_processes_count: int
   :param monitor_checks_delay: The delay between monitoring iterations
   :type monitor_checks_delay: float
   :param update_min_delay: The delay between iterations updates
   :type update_min_delay: float
   :param heartbeat_fail_delay: The timeout of the streams processes without heartbeats
   :type heartbeat_fail_delay: float

   :param process_start_callback: The callback called when streams processes start on the station
   :type process_start_callback: Callable
   :param process_stop_callback: The callback called when streams processes stop on the station
   :type process_stop_callback: Callable
   :param process_error_callback: The callback called when streams processes stop with an error
       on the station
   :type process_error_callback: Callable
   :param spawn_process_start_callback: The callback called when start streams loading
   :type spawn_process_start_callback: Callable
   :param spawn_process_stop_callback: The callback called when a stream is found
   :type spawn_process_stop_callback: Callable
   :param spawn_process_error_callback: The callback called when streams loading error caused
   :type spawn_process_error_callback: Callable

   .. attribute:: CLASS_PATH
      :annotation: = /stations/

      :class:`ZeroStation` instances collection path in the repository


   .. attribute:: FIELDS_SCHEMA
      

      :class:`ZeroStation` fields validators


   .. method:: start(self, **kwargs)


      Start the worker process


   .. method:: stop(self, **kwargs)


      Stop the worker process
