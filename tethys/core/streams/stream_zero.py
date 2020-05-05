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

import logging
import time
from contextlib import contextmanager
from typing import Union, Callable, TYPE_CHECKING, Generator, List, Any, Tuple

from tethys.core.nodes.node_zero import ZeroNode
from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject
from tethys.core.sessions.sess_zero import ZeroSession
from tethys.core.streams.stream_base import StreamBase
from tethys.core.transports.transport_zero import ZeroTransport

if TYPE_CHECKING:
    from tethys.core.stations.station_zero import ZeroStation  # noqa: F401
    from tethys.core.pipes.pipe_zero import ZeroPipe  # noqa: F401

log = logging.getLogger(__name__)


class ZeroStream(ZeroRegistrableObject, StreamBase):
    """
    The Stream entity class of the Zero generation.
    The ZeroStream is an entity that defines the physical path of the data.

    """

    DEFAULT_HEARTBEAT_FAIL_DELAY = 10
    READ_DELAY = 0.1

    CLASS_PATH = "/streams/"
    ":class:`ZeroStream` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "pipe": {"type": ["string", "ZeroPipe"], "required": True},
        "transport": {"type": ["string", "ZeroTransport"], "required": True},
        "session": {"type": ["string", "ZeroSession"], "required": True},
        "station": {
            "type": ["string", "ZeroStation"],
            "nullable": True,
            "required": False,
            "default": None,
        },
        "heartbeat_ts": {"type": "number", "default": 0, "required": False},
        "closed": {"type": "boolean", "nullable": False, "default": False},
    }
    ":class:`ZeroStream` fields validators"

    def __new__(cls, *args, _id=None, **kwargs):

        if _id is None and len(args) >= 2:
            pipe, session, *_ = args
            _id = "{}_{}".format(session.id, pipe.id)

        return super().__new__(cls, *args, _id=_id, **kwargs)

    def __init__(
        self,
        pipe: "ZeroPipe",
        session: "ZeroSession",
        transport: Union["ZeroTransport", Callable],
        **kwargs
    ):
        """

        :param pipe: Pipe instance that defines the logical path between nodes.
        :type pipe: ZeroPipe
        :param session: The session allows getting the stream for the pipe.
        :type session: ZeroSession
        :param transport:
        """
        self.pipe = pipe
        self.session = session
        self.station = None
        self.closed = False
        self.heartbeat_ts = 0

        if transport and not isinstance(transport, ZeroTransport):
            transport = transport(self)
        self.transport = transport

    @contextmanager
    def connection_context(self):
        if not self.transport.is_connected(self):
            self.transport.connect(self)
            disconnect_after_read = True
        else:
            disconnect_after_read = False

        yield

        if disconnect_after_read:
            self.transport.disconnect(self)

    @property
    def heartbeat_fail_delay(self):
        station = self.station

        if station:
            heartbeat_fail_delay = getattr(station, "heartbeat_fail_delay", 0)
            if not heartbeat_fail_delay or heartbeat_fail_delay < 0:
                heartbeat_fail_delay = self.DEFAULT_HEARTBEAT_FAIL_DELAY
            return heartbeat_fail_delay

        return self.DEFAULT_HEARTBEAT_FAIL_DELAY

    @property
    def is_busy(self) -> bool:
        """
        Is some station using the stream?

        :rtype: bool
        """

        self.refresh()
        return (
            self.heartbeat_fail_delay
            and time.time() - self.heartbeat_ts < self.heartbeat_fail_delay
        )

    def open(self, save=True, **kwargs) -> "ZeroStream":
        """
        Open stream

        :param save: to save the stream
        :type save: bool
        :return: self instance
        :rtype: StreamBase
        """

        self.closed = False

        if save:
            self.save(save_dependency=False)

        log.info("Stream %s opened%s", self.id, ". State was saved" if save else "")

        return self

    def close(self, save=True, **kwargs) -> "ZeroStream":
        """
        Close stream

        :param save: to save the stream
        :type save: bool
        :return: self instance
        :rtype: StreamBase
        """

        self.closed = True

        if save:
            self.save(save_dependency=False)

        log.info("Stream %s closed%s", self.id, ". State was saved" if save else "")

        return self

    def write(self, data_packet: Union[List[Any], Any], many: bool = False, **kwargs):
        """
        Write the data_packet to the stream

        :param data_packet: any data object or list of the data objects (with many=True)
        :param many: if many=True then data_packet's elements will be sent one-by-one.
        :type many: bool
        """

        if not self.closed or self.pipe.node_b == ZeroNode.OUT:
            with self.connection_context():
                if many:
                    data_packets = data_packet
                    for data_packet in data_packets:
                        self.transport.send(self, data_packet, **kwargs)
                else:
                    self.transport.send(self, data_packet, **kwargs)

    def read(
        self, count: int = None, wait_timeout: float = None, **kwargs
    ) -> Generator[Tuple[str, Any], None, None]:
        """
        Read the data_packets from the stream. Return Generator.

        :param count: count of the data_packets
        :type count: int
        :param wait_timeout: waiting time (seconds)
        :type wait_timeout: float
        """

        counter = count or -1
        initial_station = self.station

        with self.connection_context():

            while counter and not self.closed and initial_station == self.station:
                data_packet = None
                counter -= 1

                if wait_timeout is None:
                    while (
                        data_packet is None
                        and not self.closed
                        and initial_station == self.station
                    ):
                        data_packet = self.transport.recv(
                            self, wait_timeout=wait_timeout, **kwargs
                        )

                        if data_packet is None:
                            self.refresh()

                            if self.session.closed or self.session.closing_mode:
                                return
                            time.sleep(self.READ_DELAY)

                else:
                    data_packet = self.transport.recv(
                        self, wait_timeout=wait_timeout, **kwargs
                    )

                if data_packet is None:
                    break

                yield data_packet

    def ack(self, message_key: str, **kwargs):
        """
        Acknowledge message

        :param message_key: message key for the acknowledgement
        :type message_key: str
        """

        if not self.closed:
            with self.connection_context():
                self.transport.ack(self, message_key, **kwargs)

    def redirect_to(self, station: "ZeroStation", **kwargs):
        """
        Redirect stream processing to the station

        :param station: Station where the stream can be processed in the near time
        :type station: ZeroStation
        """

        if not self.station or self.station.id != station.id:
            log.info(
                "Stream %s will redirect %sto [%s] station",
                self.id,
                "from [{}] station ".format(self.station.id) if self.station else "",
                station.id,
            )

        station.save(save_dependency=False)

        self.station = station
        self.heartbeat_ts = time.time()

        self.save(save_dependency=False)

        log.info(
            "Stream %s was redirected to [%s] station", self.id, self.station.id,
        )

    def heartbeat(self, **kwargs):
        """
        Health heartbeat

        """

        self.heartbeat_ts = time.time()
        self.save(save_dependency=False)

        log.debug("Stream [%s] heartbeat", self.id)

    def __enter__(self):
        return self.open(save=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(save=False)
