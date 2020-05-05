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

Concept
=======

Tethys is a system that helps you manage data streams.
You can build your network of pipes and nodes. After this you can push your data.
This data will be processed according to the network schema.

You need additional components to control all processes for the system to work properly.
System functionality and its components are described below.


Zero Objects
------------

Every component state will be stored in particular database (repository).
You can read more about database interfaces in the :ref:`User Guide` page.

There are 7 basic components:

:mod:`Networks <tethys.core.networks>`,
:mod:`Pipes <tethys.core.pipes>`, and
:mod:`Nodes <tethys.core.nodes>` are abstract representations of the system processes.
They help to describe a logical data path.

:mod:`Sessions <tethys.core.sessions>`,
:mod:`Streams <tethys.core.streams>`, and
:mod:`Transports <tethys.core.transports>` provide the information about physical processes.

:mod:`Stations <tethys.core.stations>` coordinate and execute every process.


Together they ensure the correct work of the system.
The description of components work is provided below on the diagrams.

Life Cycle
----------

.. thumbnail:: assets/images/concept/1.png
  :alt: Basic network
  :group: concept

This example shows a network that describes a simple HTTP content downloader.
There are nodes which are connected with the help of pipes,
the operators that execute special functions with the data and
some components (like transport factories and a filter).

Pipes use local transports (RAM) by default.
The system will work correctly if the nodes (connected by the local pipe) are executed in one process.
Custom transports and transports factories allow to set external technologies (like RabbitMQ).
All the examples show Apache Kafka is used as the default transport.

Nodes can pull the data from the pipes and execute operator for each data packet.
Each node executes a dummy operator (which broadcasts data packets to the next pipes) by default.

Each Pipe filters data packets before being sent to the next Nodes (using Filter components).

All processes can be distributed across your cluster machines.
Each machine can launch station that will spawn and control stream processes.
Station is a simple worker program. And there are some additional programs that help to launch
the Station worker from shell with your custom settings.
Also you can define the functions to each of the specific station.

In most cases, you will start the worker like this:

.. code-block:: bash

    tethys apps Worker start --config worker.conf.yaml

Each data stream process represent by Stream object.
Stream objects is the entity that describe physical data streams.
Streams can be open and close.
Also there are Sessions that isolate processes.
Each Stream attached to a some Session and to the Pipe.
Put simply, Stream is the representation of the data stream in the pipe in the session context.


.. thumbnail:: assets/images/concept/2.png
  :alt: Basic network with stations
  :group: concept

The schema shows 2 stations. The first station works and wait open stream.
The second station do nothing. Information about stations is stored in a meta registry.
Meta registry is the database with information about all system components (their states).

You can create a session and send some data to the flow. After that the system will create an instance of the Stream object.

.. code-block:: python

    # pseudo example
    sess = ZeroSession(network).save()
    sess.send("some_data_packet")


.. thumbnail:: assets/images/concept/3.png
  :alt: Basic network with session
  :group: concept

The data packet will be sent to the first pipe (<IN>).
This pipe will create a Stream object and send the data_packet to it.
Station will find the Stream and start a process that will listen to the stream (data packets),
execute operators for each new data_packet and send the results to the next pipes.


.. thumbnail:: assets/images/concept/4.png
  :alt: Basic network with session
  :group: concept


After a while, the pipes will be filled with data streams.
<OUT> Pipe is not full, because Node 2 sends data only to the first channel.


.. thumbnail:: assets/images/concept/5.png
  :alt: Data flow
  :group: concept


In the example, Node 1 processes each URL, downloads the content,
saves the content on disk and sends content URI (path on disk) to the next node (Node 2).

The next node reads content from the disk, parses the content, and each new URL (from the content) is sent to the next node (Node 3).

Node 3 checks the history to prevent duplication and sends the URL (if it's a new URL) to the first node (Node 1).
Pipe's filter also checks the URL protocol.


You can stop the data flow. All streams will be closed when you close the session.
There are several closing modes. Next examples show <soft> mode.

.. thumbnail:: assets/images/concept/6.png
  :alt: Session closing
  :group: concept

When you close the session (soft mode), streams will be close when they are empty.
The example (above) shows that Stream 1 is going to be close.



Over time all streams will be closed.

.. thumbnail:: assets/images/concept/7.png
  :alt: Session closing
  :group: concept


Session will be closed (completely) when there are no open streams.

.. thumbnail:: assets/images/concept/8.png
  :alt: Session closing
  :group: concept

In some cases, the closing process can be endless as some node processes can be endless (or may be zombie).
To stop the process you need to close the session completely (<instant> mode).
