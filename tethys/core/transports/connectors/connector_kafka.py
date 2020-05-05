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

from kafka import KafkaConsumer, KafkaProducer
from kafka.structs import TopicPartition

from tethys.core.transports.connectors.connector_base import (
    ConnectorBase,
    ConnectionBase,
)


class KafkaConnection(ConnectionBase):
    def __init__(
        self,
        channel_id: str,
        group_id: str,
        partition: int,
        bootstrap_servers: list,
        producer_params: dict,
        consumer_params: dict,
    ):

        self.topic = channel_id
        self.group_id = group_id or channel_id
        self.partition = partition or 0
        self.bootstrap_servers = bootstrap_servers or []

        self.producer_params = producer_params or {}
        self.consumer_params = consumer_params or {}

        self._consumer = None
        self._producer = None

    def _get_consumer(self):
        enable_auto_commit = self.consumer_params.pop("enable_auto_commit", False)
        auto_offset_reset = self.consumer_params.pop("auto_offset_reset", "earliest")
        consumer_timeout_ms = self.consumer_params.pop("consumer_timeout_ms", 10 * 1000)
        max_poll_records = self.consumer_params.pop("max_poll_records", 1)
        value_deserializer = self.consumer_params.pop(
            "value_deserializer", lambda x: json.loads(x.decode("utf-8"))
        )

        consumer = KafkaConsumer(
            group_id=self.group_id,
            bootstrap_servers=self.bootstrap_servers,
            consumer_timeout_ms=consumer_timeout_ms,
            enable_auto_commit=enable_auto_commit,
            auto_offset_reset=auto_offset_reset,
            max_poll_records=max_poll_records,
            value_deserializer=value_deserializer,
            **self.consumer_params
        )
        consumer.assign([TopicPartition(self.topic, self.partition)])

        return consumer

    def _get_producer(self):
        value_serializer = self.producer_params.pop(
            "value_serializer", lambda x: json.dumps(x).encode()
        )
        producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=value_serializer,
            **self.producer_params
        )
        return producer

    def recv_iter(self, **kwargs):
        for message in self._consumer:
            yield "", message

    def send(self, data_packet, **kwargs):
        self._producer.send(self.topic, value=data_packet, **kwargs).get()

    def ack(self, message_key, **kwargs):
        self._consumer.commit()

    def open(self, **kwargs) -> "KafkaConnection":
        self._consumer = self._get_consumer()
        self._producer = self._get_producer()

        return self

    def close(self, **kwargs) -> "KafkaConnection":
        self._consumer = None
        self._producer = None

        return self


class KafkaConnector(ConnectorBase):
    def __init__(
        self,
        partition: int = 0,
        bootstrap_servers: list = None,
        producer_params: dict = None,
        consumer_params: dict = None,
    ):
        self.partition = partition
        self.bootstrap_servers = bootstrap_servers or []

        self.producer_params = producer_params or {}
        self.consumer_params = consumer_params or {}

    def connect(
        self,
        channel_id: str,
        group_id: str = None,
        partition: int = 0,
        bootstrap_servers: list = None,
        producer_params: dict = None,
        consumer_params: dict = None,
        **kwargs
    ) -> "KafkaConnection":
        topic = channel_id
        group_id = group_id or channel_id
        partition = partition or 0
        bootstrap_servers = bootstrap_servers or []

        producer_params = producer_params or {}
        consumer_params = consumer_params or {}

        return KafkaConnection(
            topic,
            group_id,
            partition,
            bootstrap_servers,
            producer_params,
            consumer_params,
        ).open()
