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

import json
import logging.config
import os
import shutil

from tethys.apps.worker.settings import LOG_CONFIG
from tethys.core.networks import ZeroNetwork
from tethys.core.nodes import ZeroNode
from tethys.core.nodes.operators import (
    BashPerPacketOperator,
    PythonFunctionOperator,
    RoundRobinBalancerOperator,
)
from tethys.core.pipes import ZeroPipe
from tethys.core.sessions import ZeroSession
from tethys.core.stations import ZeroStation
from tethys.core.transports import ZeroTransport
from tethys.core.transports.connectors import PersistQueueConnector

TMP_FOLDER = "tmp"


def get_file_data(data_packet, node):
    if isinstance(data_packet, dict):
        name = data_packet["data"]
    else:
        name = str(data_packet)

    json_file_name = "{}.{}.json".format(node.id, name)
    return json_file_name, json.dumps(data_packet)


def cmd_generator(p, _):
    return "echo '{1}' > ./tmp/{0}".format(*p)


class OwnZeroNode(ZeroNode):
    CLASS_PATH = "/nodes/own/"


def get_network():
    b = ZeroNode(RoundRobinBalancerOperator(), _id="balancer").save()
    n1 = ZeroNode(PythonFunctionOperator(get_file_data), _id="node1").save()
    n2 = ZeroNode(PythonFunctionOperator(get_file_data), _id="node2").save()
    n3 = OwnZeroNode(PythonFunctionOperator(get_file_data), _id="node3").save()
    bash_save = ZeroNode(BashPerPacketOperator(cmd_generator), _id="bash_save")

    return ZeroNetwork(
        [
            ZeroPipe(ZeroNode.IN, b, _id="in-balancer"),
            ZeroPipe("balancer", "/zero/nodes/node1", _id="balancer-node1"),
            ZeroPipe("balancer", "/zero/nodes/node2", _id="balancer-node2"),
            ZeroPipe("balancer", "/zero/nodes/own/node3", _id="balancer-node3"),
            ZeroPipe("node1", bash_save, _id="node1-bash_save"),
            ZeroPipe("node2", bash_save, _id="node2-bash_save"),
            ZeroPipe("/zero/nodes/own/node3", bash_save, _id="node3-bash_save"),
            ZeroPipe(n1, ZeroNode.OUT, _id="node1-out"),
            ZeroPipe(n2, ZeroNode.OUT, _id="node2-out"),
            ZeroPipe(n3, ZeroNode.OUT, _id="node3-out"),
        ]
    )


def prepare_env():
    shutil.rmtree(TMP_FOLDER, ignore_errors=True)
    os.makedirs(TMP_FOLDER)


def config_logger():
    LOG_CONFIG["loggers"]["tethys"]["level"] = logging.DEBUG
    logging.config.dictConfig(LOG_CONFIG)


def config_transport():
    def connections_factory(connector, stream):
        return connector.connect("{}/{}".format(stream.session.id, stream.id))

    def transport_factory(pipe):
        connector = PersistQueueConnector("/tmp/tethys/queues/{}/".format(pipe.id))
        return ZeroTransport(connector, connections_factory)

    ZeroPipe.set_transport_factory(transport_factory)


if __name__ == "__main__":
    prepare_env()
    config_logger()
    config_transport()

    net = get_network()

    with ZeroSession(net) as sess:
        sess.send("json_string")
        sess.send([{"data": i} for i in range(100)], many=True)

    def process_start_handler(stream=None, station=None):
        print("Start {} stream [{} station]".format(stream.id, station))

    def process_stop_handler(stream=None, station=None):
        print("Stop {} stream [{} station]".format(stream.id, station))

    def process_error_handler(e, stream=None, station=None):
        print("Error in {} stream [{} station]: {}".format(stream.id, station, e))

    ZeroStation(
        [sess],
        stream_waiting_timeout=0,
        monitor_checks_delay=0.5,
        process_start_callback=process_start_handler,
        process_stop_callback=process_stop_handler,
        process_error_callback=process_error_handler,
    ).start()

    for out_pipe in net.output_pipes:
        with out_pipe.get_stream(sess) as out_stream:
            print("{} -> <{}>:".format(*out_pipe.id.split("-")))

            for _, out_data_packet in out_stream.read(wait_timeout=0):
                print("   ", out_data_packet)
