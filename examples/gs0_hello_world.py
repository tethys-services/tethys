# Copyright 2020 Konstruktor, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tethys.core.networks import ZeroNetwork
from tethys.core.nodes import ZeroNode
from tethys.core.pipes import ZeroPipe
from tethys.core.sessions import ZeroSession
from tethys.core.stations import ZeroStation

CACHE = []


def hello_world_op(data_packet):  # aggregate data

    CACHE.append(data_packet)

    if len(CACHE) == 2:
        return " ".join(
            CACHE
        )  # it sends CACHE data to other nodes when len(CACHE) == 2


def get_network():
    hello_world_node = ZeroNode(
        hello_world_op, _id="hello_world_node_id",  # set custom id (default: uuid4)
    )

    print_node = ZeroNode(print)

    #                                        -------->  [print_node]
    #                                       |
    #   <in>  ----> [hello_world_node] ----
    #                                       \
    #                                         -------->  <out>
    return ZeroNetwork(
        [
            ZeroPipe(ZeroNode.IN, hello_world_node),
            ZeroPipe(hello_world_node, print_node),
            ZeroPipe("hello_world_node_id", ZeroNode.OUT),
        ]
    )


if __name__ == "__main__":
    net = get_network()  # build network

    with ZeroSession(net) as session:  # start the session
        session.send(
            ["Hello", "World", "Will be ignored"], many=True
        )  # send 3 data packets to the <in> node
    # the soft closing request will be sent after the context is closed

    ZeroStation(
        sessions=[session],  # it filters the sessions the station work with
        stream_waiting_timeout=0,  # streams reading timeout
        monitor_checks_delay=0,  # streams switching interval (in this local context)
    ).start()  # start the worker for the session

    # >>> Hello World

    print("-" * 85, "\n")

    # read data from the ['hello_world_node' -> '<out>'] pipe
    out_pipe = next(net.output_pipes)

    with out_pipe.get_stream(session) as stream:
        _, out_data_packet = next(stream.read(wait_timeout=0))
        print(
            "The first data packet of the out pipe : '{}'".format(str(out_data_packet))
        )

    # >>> The first data packet of the out pipe : 'Hello World'
