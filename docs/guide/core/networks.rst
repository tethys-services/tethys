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

Networks Manipulating
=====================

Network is the main logical element of the project.
It defines a data pipeline scheme.
Each data pipelines build with Pipe objects.
Pipe objects is a logical element that defines a data path between nodes.

Put simply, Network object is a collection of the logical connections between nodes (in the project context).

In most cases, the Network object used for creating data streams.
But it provides much responsibility for creating and reusing (with templating) the network schemas in any places.


Example to understand the concept:
    .. code-block:: python

        from tethys.core.networks import ZeroNetwork
        from tethys.core.pipes import ZeroPipe
        from tethys.core.nodes import ZeroNode

        node1 = ZeroNode()
        node2 = ZeroNode()

        pipe1 = ZeroPipe(node1, node2)
        pipe2 = ZeroPipe(node2, node1)
        pipe3 = ZeroPipe(node2, node2)

        net_template1 = ZeroNetwork(pipe1)
        net_template2 = ZeroNetwork([pipe2, pipe3])  # pipes = [pipe2, pipe3]
        net_template2.add_pipes([pipe3, pipe2])   # pipes = [pipe3, pipe2]

        network1 = net_template1 + net_template2

        assert list(network1.pipes.values()) == [pipe1, pipe3, pipe2]

        assert (network1 - net_template2).pipes == net_template1.pipes
        assert (network1 - net_template1).pipes == net_template2.pipes

        assert (net_template1 | net_template2).pipes == network1.pipes
        assert (net_template1 & net_template2).pipes == {}

        network1 &= net_template1
        assert network1.pipes == net_template1.pipes
