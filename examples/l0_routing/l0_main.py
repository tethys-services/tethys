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

import logging.config
import os
import shutil

from tethys.apps.worker.settings import LOG_CONFIG
from tethys.core.networks import ZeroNetwork
from tethys.core.nodes import ZeroNode
from tethys.core.nodes.operators import PythonFunctionOperator
from tethys.core.pipes import ZeroPipe
from tethys.core.pipes.filters import SimpleJsonPathFilter
from tethys.core.sessions import ZeroSession
from tethys.core.stations import ZeroStation
from tethys.core.transports import ZeroTransport
from tethys.core.transports.connectors import PersistQueueConnector

TMP_FOLDER = "tmp"


def generate_data(data_packet, node, session):
    number = int(data_packet)

    node.send([{"data": {"number": i}} for i in range(number)], session, many=True)

    node.send("some str", session)

    return "some str"


def get_network():
    node1 = ZeroNode(PythonFunctionOperator(generate_data), _id="node1").save()

    def f_odd(value):
        return value % 2 == 1

    def f_even(value):
        return value % 2 == 0

    odd_filter = SimpleJsonPathFilter("data.number", f_odd)
    even_filter = SimpleJsonPathFilter("data.number", f_even)

    custom_transport = ZeroTransport(
        PersistQueueConnector(TMP_FOLDER, queue_engine="file")
    )

    return ZeroNetwork(
        [
            ZeroPipe(ZeroNode.IN, node1, _id="in-node1",),
            ZeroPipe(
                "/zero/nodes/node1",
                ZeroNode.OUT,
                filters=[even_filter],
                transport=custom_transport,
                _id="even-out",
            ),
            ZeroPipe(
                node1,
                ZeroNode.OUT,
                filters=[odd_filter],
                transport=custom_transport,
                _id="odd-out",
            ),
        ]
    )


def prepare_env():
    shutil.rmtree(TMP_FOLDER, ignore_errors=True)
    os.makedirs(TMP_FOLDER)


def config_logger():
    LOG_CONFIG["loggers"]["tethys"]["level"] = logging.DEBUG
    logging.config.dictConfig(LOG_CONFIG)


if __name__ == "__main__":
    prepare_env()
    config_logger()

    net = get_network()

    with ZeroSession(net) as sess:
        sess.send(10)

    ZeroStation(
        [sess],
        stream_waiting_timeout=0,
        monitor_checks_delay=0,
        update_min_delay=0,
        stream_lock_blocking=True,
        stream_lock_ttl=10,
    ).start()

    for out_pipe in net.output_pipes:
        with out_pipe.get_stream(sess) as stream:
            print("{} -> <{}>:".format(*out_pipe.id.split("-")))

            for _, out_data_packet in stream.read(wait_timeout=0):
                print("   ", out_data_packet)
