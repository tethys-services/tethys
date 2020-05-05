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

Quick Start
===========

This tutorial assumes you are starting fresh.
You are to read the :ref:`User Guide` to learn how to do more complicated and useful things.

Tethys is created to manage the data flow among your systems.
How to start your first data stream is provided below.

*Let's start with "Hello World"!*

1. Install Tethys

.. code-block:: python

   # installing from PyPI
   pip install tethys


2. Create network

.. code-block:: python

    # network.py

    from tethys.core.networks import ZeroNetwork
    from tethys.core.nodes import ZeroNode
    from tethys.core.pipes import ZeroPipe

    CACHE = []


    def hello_world_op(data_packet):

        CACHE.append(data_packet)

        if len(CACHE) == 2:
            return ' '.join(CACHE)


    def get_network():

        hello_world_node = ZeroNode(
            hello_world_op,
            _id="hello_world_id"
        )

        print_node = ZeroNode(print)

        return ZeroNetwork(
            [
                ZeroPipe(
                    ZeroNode.IN, hello_world_node
                ),
                ZeroPipe(
                    hello_world_node, print_node
                ),
                ZeroPipe(
                    "hello_world_id", ZeroNode.OUT
                ),
            ]
        )


3. Process data



.. code-block:: bash

    # run in python terminal
    python3


.. code-block:: python

    from network import get_network
    from tethys.core.stations import ZeroStation
    from tethys.core.sessions import ZeroSession

    net = get_network()

    with ZeroSession(net) as session:
        session.send(["Hello", "World", "Something else"], many=True)

    ZeroStation(
        sessions=[session],
        stream_waiting_timeout=0,
        monitor_checks_delay=0.5,
    ).start()


4. Check results


.. code-block:: python

    out_pipe = next(net.output_pipes)
    out_stream = out_pipe.get_stream(session)

    with out_stream:
        out_stream_gen = out_stream.read()
        key, message = next(out_stream_gen)
        print(message)

Full example is here: `gs0_hello_world.py <https://github.com/tethys-platform/tethys/blob/master/examples/gs0_hello_world.py>`_.

You can visit `Github <https://github.com/tethys-platform/tethys/tree/master/examples>`_ for further examples.
