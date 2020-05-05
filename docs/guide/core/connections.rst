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

Data Streams and Connections
============================


There are several objects that realize the main idea of the project.
And some of them implement data transfer interfaces: Pipe, Stream, Transport.

Pipe objects describe logical data paths. Also, these objects responsible for streams getting.
Stream objects store information about Transport objects and a state of the data flows.
Transport objects responsible for managing connections.


Example to understand the concept of the pipes and streams creating:

    .. code-block:: python

        from tethys.core.exceptions import TethysROFieldValidationError
        from tethys.core.pipes import ZeroPipe
        from tethys.core.streams import ZeroStream
        from tethys.core.transports import ZeroTransport
        from tethys.core.transports.connectors import DummyConnector

        from tethys.core.networks import ZeroNetwork
        from tethys.core.sessions import ZeroSession
        from tethys.core.nodes import ZeroNode

        node1 = ZeroNode()
        node2 = ZeroNode()
        network = ZeroNetwork()
        session = ZeroSession(network)

        connector = DummyConnector()
        custom_transport = ZeroTransport(connector)

        # will execute in ZeroStream.__init__
        def transport_func(stream): return custom_transport

        pipe1 = ZeroPipe(node1, node2)
        pipe2 = ZeroPipe(node2, node1, transport=transport_func)
        pipe3 = ZeroPipe(node2, node1, transport=custom_transport)

        assert pipe1.transport != pipe2.transport != pipe3.transport

        # transport factories

        # set the transport for all pipes in the context
        with ZeroPipe.transport_factory_context(custom_transport):
            pipe4 = ZeroPipe(node2, node1)

        # set the result of the function for all pipes in the context
        # lambda will execute in ZeroPipe.__init__ method
        with ZeroPipe.transport_factory_context(lambda pipe: custom_transport):
            pipe5 = ZeroPipe(node2, node1)

        assert pipe3.transport == pipe4.transport == pipe5.transport

        with ZeroPipe.transport_factory_context(lambda pipe: custom_transport):
            # lambda will execute in ZeroPipe.get_stream() method
            pipe6 = ZeroPipe(node2, node1, transport=None)

        ZeroPipe.set_transport_factory(custom_transport)

        pipe7 = ZeroPipe(node2, node1, transport=None)

        assert pipe5.transport != pipe6.transport
        assert pipe6.transport is None and pipe7.transport is None

        # streams

        stream1 = pipe1.get_stream(session)  # this get_stream will create the stream
        stream2 = pipe2.get_stream(session)
        stream3 = pipe3.get_stream(session)
        stream4 = pipe4.get_stream(session)
        stream5 = pipe5.get_stream(session)
        stream6 = pipe6.get_stream(session)
        stream7 = pipe7.get_stream(session)

        assert stream7 == pipe7.get_stream(session)  # and this get_stream will load the stream

        # first pipe and first stream using default transport
        assert stream1.transport != stream2.transport

        # other streams have identical transport objects
        assert all(
            stream.transport == custom_transport
            for stream in [stream2, stream3, stream4, stream5, stream6, stream7]
        )

        custom_stream = ZeroStream(pipe1, session, custom_transport)

        try:
            custom_stream2 = ZeroStream(pipe1, session, None)
        except TethysROFieldValidationError:
            custom_stream2 = None

        assert not custom_stream2


Each object described above uses special methods to transfer data.
The following examples show how these methods work.

In most cases, you will not use the pipe's interface to send data,
but the next example will help you to understand how data are transferred and filtered.

    .. code-block:: python

        from tethys.core.pipes import ZeroPipe
        from tethys.core.pipes.filters import RegexMatchFilter, FNFilter

        from tethys.core.networks import ZeroNetwork
        from tethys.core.sessions import ZeroSession
        from tethys.core.nodes import ZeroNode

        from difflib import SequenceMatcher

        node1 = ZeroNode()
        node2 = ZeroNode()
        network = ZeroNetwork()
        session = ZeroSession(network)

        # simple pipe
        pipe1 = ZeroPipe(node1, node2)

        # push method will get/create stream by self.get_stream(session)
        # and execute 'write' method of the stream.
        pipe1.push("some_data_packet", session)

        # pull method will receive data from the stream.
        data_packets_generator = pipe1.pull(session)

        assert next(data_packets_generator) == "some_data_packet"

        # a distinctive feature of the pipe's methods is filtering.
        # you can filter the data before sending using special filters.

        def similarity(data_packet, **kwargs):
            if not isinstance(data_packet, str):
                return 0.0
            return SequenceMatcher(None, data_packet, "some_data_packet").ratio()

        pipe2 = ZeroPipe(
            node1, node2,
            filters=[
                RegexMatchFilter("^some_.*"),  # return 1 or 0
                FNFilter(similarity)  # return similarity result
            ],
            filters_threshold=0.5  # filters score > 0.5
        )

        # also you can send a list of data packets by adding many=True
        pipe2.push(["some_data_packet", "data_packet", "some_", None, {}], session, many=True)
        data_packets_generator = pipe2.pull(session, wait_timeout=0)

        assert list(data_packets_generator) == ["some_data_packet"]


Pipes methods are proxies for the streams methods with some sugar,
as well as streams methods are proxies for the transport methods.

Next example shows how the methods work together:

    .. code-block:: python

        import json

        from tethys.core.pipes import ZeroPipe

        from tethys.core.networks import ZeroNetwork
        from tethys.core.sessions import ZeroSession
        from tethys.core.nodes import ZeroNode
        from tethys.core.transports import ZeroTransport

        node1 = ZeroNode()
        node2 = ZeroNode()
        network = ZeroNetwork()
        session = ZeroSession(network)

        def serializer(x):
            return json.dumps(x)

        def deserializer(x):
            return json.loads(x)

        transport1 = ZeroTransport(serializer=serializer, deserializer=deserializer)
        pipe1 = ZeroPipe(node1, node2, transport=transport1)
        stream1 = pipe1.get_stream(session)
        connection1 = transport1.connect(stream1)

        pipe1.push("data1", session)

        data_packet_key1, data_packet1 = next(stream1.read(wait_timeout=0))
        stream1.write(["data2", {"v": "data3"}], many=True)
        stream1.ack(data_packet_key1)

        assert (data_packet_key1, data_packet1) == ("", "data1")


        data_packet_key2, data_packet2 = transport1.recv(stream1, wait_timeout=0)
        transport1.send(stream1, None)
        transport1.ack(stream1, data_packet_key2)

        assert (data_packet_key2, data_packet2) == ("", "data2")


        connection1.send("data")
        assert list(connection1.recv_iter()) == [
            ("", '{"v": "data3"}'),
            ("", "null"),
            ("", "data")
        ]  # not deserialized

        for i in range(3):
            connection1.ack("")  # "" because LocalConnection doesn't generate message_key

        transport1.disconnect(stream1)

As a user, you will not use most of the features.
They are part of the system and helps to process your data according to your declarative instructions.

Also, there are methods for data sending in Nodes and Sessions.
In most cases, you will use them to send data.

High-level example:

    .. code-block:: python

        import json

        from tethys.core.pipes import ZeroPipe
        from tethys.core.networks import ZeroNetwork
        from tethys.core.sessions import ZeroSession
        from tethys.core.nodes import ZeroNode
        from tethys.core.nodes.operators import PythonFunctionOperator
        from tethys.core.transports import ZeroTransport
        from tethys.core.stations import ZeroStation


        def serializer(x):
            return json.dumps(x)


        def deserializer(x):
            return json.loads(x)


        transport1 = ZeroTransport(serializer=serializer, deserializer=deserializer)


        # the first argument is the data_packet and other arguments will be recognized (by name)
        # you can pass arguments in any order
        # list of the available arguments you can find in the PythonFunctionOperator description
        # in the Api Reference section

        def op1_fn(data_packet, node, network, session):
            if isinstance(data_packet, str):
                # send data to the forward pipes (Pipe2 and Pipe3)
                node.send(data_packet, session)
            else:
                first_forward_pipe = next(network.get_forward_pipes(node))  # Pipe2
                first_forward_pipe.push(data_packet, session)

        def op2_fn(data_packet, pipe, node, session):
            if isinstance(data_packet, str):
                pipe.push({"data": data_packet}, session)  # recursion
            else:
                node.send(data_packet, session)  # send data to the forward pipes

        # data processing will detailed in the next docs section.
        node1 = ZeroNode(
            PythonFunctionOperator(op1_fn)
        )
        node2 = ZeroNode(
            op2_fn  # the function will be wrapped by PythonFunctionOperator
        )
        # default: dummy operator that just returns data_packet
        node3 = ZeroNode()


        with ZeroPipe.transport_factory_context(transport1):
            pipe1 = ZeroPipe(ZeroNode.IN, node1, _id="pipe1")
            pipe2 = ZeroPipe(node1, node2, _id="pipe2")
            pipe3 = ZeroPipe(node1, node3, _id="pipe3")
            pipe4 = ZeroPipe(node2, ZeroNode.OUT, _id="pipe4")
            pipe5 = ZeroPipe(node3, ZeroNode.OUT, _id="pipe5")

        network = ZeroNetwork([pipe1, pipe2, pipe3, pipe4, pipe5])

        #                                     -----Pipe 2------>  Node 2 -----Pipe 4------> OUT
        #    IN   --Pipe1-->   Node 1   --->
        #                                     -----Pipe 3------>  Node 3 -----Pipe 5------> OUT

        session = ZeroSession(network).open()

        # will send data to the input pipe (Pipe1)
        session.send(["data1", "data2", {"data": "data3"}], many=True)

        session.close(ZeroSession.SOFT_CLOSING_MODE)

        # start processing
        ZeroStation(
            sessions=[session],
            monitor_checks_delay=0.1,
            update_min_delay=0.1,
            stream_waiting_timeout=0
        ).start()

        assert list(pipe4.pull(session, wait_timeout=0)) == [
            {"data": "data3"},
            {"data": "data1"},
            {"data": "data2"}
        ]

        assert list(pipe5.pull(session, wait_timeout=0)) == [
            "data1",
            "data2"
        ]

How to work the "data processing" will detailed in next sections of the docs.
Also, list of the filters, operators and connectors you can find in the :ref:`API Reference`.
