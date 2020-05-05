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
import os
import time
from contextlib import closing
from urllib.request import urlopen

import requests

from tethys.core.exceptions import TethysRONotFound
from tethys.core.networks import ZeroNetwork
from tethys.core.nodes import ZeroNode
from tethys.core.nodes.operators import PythonFunctionOperator
from tethys.core.pipes import ZeroPipe
from tethys.core.pipes.filters import RegexMatchFilter
from tethys.core.transports import ZeroTransport
from tethys.core.transports.connectors.connector_rabbitmq import RabbitMQConnector

TMP_FOLDER = "tmp"


class ReqOperator(PythonFunctionOperator):
    """
    It wraps the output data packet
    """

    def process(self, data_packet, stream, **kwargs):
        result = super().process(data_packet, stream, **kwargs)

        if (
            isinstance(data_packet, dict)
            and data_packet.get("_message_type") == "req_op"
        ):
            data_packet_value = data_packet["output"]
        else:
            data_packet_value = data_packet

        return {
            "input": data_packet_value,
            "output": result,
            "stream": stream.id,
            "timestamp": time.time(),
            "_message_type": "req_op",
        }


def req_http_op(data_packet):
    if isinstance(data_packet, bytes):
        data_packet = data_packet.decode()

    if isinstance(data_packet, str):
        data_packet = {"method": "GET", "url": data_packet}

    if not isinstance(data_packet, dict):
        raise ValueError("bad data_packet value: {}".format(data_packet))

    response = requests.request(**data_packet)

    if response.status_code >= 400:
        raise ValueError({"status": response.status_code, "message": response.text})

    return response.text


def req_ftp_op(data_packet):
    if isinstance(data_packet, bytes):
        data_packet = data_packet.decode()

    if not isinstance(data_packet, str):
        raise ValueError("bad data_packet value: {}".format(data_packet))

    with closing(urlopen(data_packet)) as response:
        return response.read().decode()


def save_op(data_packet):
    if not os.path.exists(TMP_FOLDER):
        os.makedirs(TMP_FOLDER)

    file_name = "{}.log".format(str(data_packet["timestamp"]))

    with open(os.path.join(TMP_FOLDER, file_name), "w") as f:
        f.write(
            "INPUT: {}\n\nOUTPUT: \n{}".format(
                data_packet["input"], data_packet["output"]
            )
        )


def transport_connectors_factory(*_, **__):
    return RabbitMQConnector(os.environ.get("TRANSPORT_URI", "amqp://127.0.0.1/"))


def serializer(x):
    return json.dumps(x).encode("utf-8")


def deserializer(x):
    return json.loads(x.decode("utf-8"))


def generate_network(name):
    transport = ZeroTransport(
        transport_connectors_factory, serializer=serializer, deserializer=deserializer
    )

    with ZeroPipe.transport_factory_context(transport):
        req_http = ZeroNode(ReqOperator(req_http_op))
        req_ftp = ZeroNode(ReqOperator(req_ftp_op))
        save = ZeroNode(PythonFunctionOperator(save_op))

        http_filter = RegexMatchFilter("^https?://.*")
        ftp_filter = RegexMatchFilter("^ftp://.*")

        return ZeroNetwork(
            [
                ZeroPipe(ZeroNode.IN, req_http, filters=[http_filter]),
                ZeroPipe(ZeroNode.IN, req_ftp, filters=[ftp_filter]),
                ZeroPipe(req_http, save),
                ZeroPipe(req_ftp, save),
            ],
            _id=name,
        )


def get_network(name="l2_network"):
    try:
        return ZeroNetwork.load(name)
    except TethysRONotFound:
        return generate_network(name).save()
