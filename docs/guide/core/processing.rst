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

Data processing
===============

There are some constraints regarding processing big data.
One of them is that the system can't calculate big data like other data streaming frameworks.
It is created for another purpose. It helps manage any data stream.
In most cases, you can use the system to combine several streaming
frameworks using one interface to do complex data processing tasks.


Tethys can process your data in Nodes using Operators.
Operators can use python to process and route the data, but it is simple usage.
If you need speed or cluster processing, you can use any integrations.

How to use nodes and operator you can learn below:
    .. code-block:: python

        from tethys.core.networks import ZeroNetwork
        from tethys.core.nodes import ZeroNode
        from tethys.core.nodes.operators import PythonFunctionOperator
        from tethys.core.pipes import ZeroPipe
        from tethys.core.sessions import ZeroSession
        from tethys.core.stations import ZeroStation


        class MyZeroSession(ZeroSession):
            FIELDS_SCHEMA = dict(
                **ZeroSession.FIELDS_SCHEMA,
                counter={
                    "type": "integer",
                    "default": 0
                }
            )


        def operator(data_packet, session):
            if isinstance(data_packet, str):
                with session.lock_context():
                    session.counter += 1
                    session.save()


        node = ZeroNode(
            PythonFunctionOperator(operator)
        )
        pipe = ZeroPipe(ZeroNode.IN, node)
        network = ZeroNetwork([pipe])

        # the session will be opened and closed (<safe> mode)
        with MyZeroSession(network) as session:
            session.send(["1", "2", None, {"some": "data"}, "3"], many=True)


        ZeroStation(
            sessions=[session],
            monitor_checks_delay=0.1,
            update_min_delay=0.1,
            stream_waiting_timeout=0,
        ).start()

        assert session.counter == 3  # isinstance(data_packet, str)

List of the :py:mod:`operators <tethys.core.nodes.operators>` you can find in the :ref:`API Reference`.
