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

from typing import Union

import pika

from tethys.core.transports.connectors.connector_base import (
    ConnectorBase,
    ConnectionBase,
)


class RabbitMQConnection(ConnectionBase):
    def __init__(self, queue: str, connection_params: Union[dict, str]):

        if isinstance(connection_params, dict):
            params = pika.ConnectionParameters(**connection_params)
        elif isinstance(connection_params, str):
            params = pika.URLParameters(connection_params)
        else:
            raise TypeError("Unsupported 'connection_params' type")

        self.queue = queue
        self.params = params

        self._connection = None
        self._channel = None

    def recv_iter(self, **kwargs):
        for method_frame, properties, body in self._channel.consume(self.queue):
            yield method_frame.delivery_tag, body

    def send(self, data_packet, **kwargs):
        self._channel.basic_publish(
            exchange="", routing_key=self.queue, body=data_packet, **kwargs
        )

    def ack(self, message_key, **kwargs):
        self._channel.basic_ack(message_key)

    def open(self, **kwargs) -> "RabbitMQConnection":
        self._connection = pika.BlockingConnection(self.params)

        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self.queue)

        return self

    def close(self, **kwargs) -> "RabbitMQConnection":
        if self._channel:
            self._channel.close()

        if self._connection:
            self._connection.close()

        self._connection = None
        self._channel = None

        return self


class RabbitMQConnector(ConnectorBase):
    def __init__(self, connection_params: Union[dict, str]):
        self.connection_params = connection_params

    def connect(self, queue: str, **kwargs) -> "RabbitMQConnection":
        return RabbitMQConnection(queue, self.connection_params).open()
