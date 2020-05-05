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
from contextlib import contextmanager
from typing import Iterable, Union, Callable, Any, Generator, TYPE_CHECKING, Optional

from tethys.core.exceptions import TethysSessionClosed
from tethys.core.nodes.node_zero import ZeroNode
from tethys.core.pipes.filters import FilterBase
from tethys.core.pipes.pipe_base import PipeBase
from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject
from tethys.core.streams.stream_zero import ZeroStream
from tethys.core.transports.connectors import LocalConnector
from tethys.core.transports.transport_zero import ZeroTransport

if TYPE_CHECKING:
    from tethys.core.sessions.sess_zero import ZeroSession  # noqa: F401

log = logging.getLogger(__name__)


def _default_transport_factory(_):
    return ZeroTransport(LocalConnector())


class ZeroPipe(ZeroRegistrableObject, PipeBase):
    """
    The Pipe entity class of the Zero generation.
    The ZeroPipe connects two nodes and allows adding filters and transports.

    **Example:**
        .. code-block:: python

            def transport_factory_1(pipe, **kwargs):
                return CustomTransport1()

            # setting default transport in the context
            with ZeroPipe.transport_factory_context(transport_factory_1):

                pipe1 = ZeroPipe(
                    node_a="node1",  # ZeroPipe will load "node1" from a repository
                    node_b="node2",  # ZeroPipe will load "node2" from a repository
                    filters=[
                        CustomFilter(return_value=0.5)  # filter will return 0.5 score
                    ],
                    filters_threshold=0.4999,  # pipe send data if filters_score > filters_threshold
                    # transport=transport_factory_1()  # specified by the transport_factory_context
                )

                pipe2 = ZeroPipe(
                    node_a=node2,  # ZeroPipe will use exists node2 object
                    node_b=node1,  # ZeroPipe will use exists node1 object

                    # specify custom transport instead of the transport_factory_1
                    transport=CustomTransport2()
                )


    """

    _transport_factory = _default_transport_factory

    CLASS_PATH = "/pipes/"
    ":class:`ZeroPipe` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "node_a": {"type": ["string", "ZeroNode"], "required": True},
        "node_b": {"type": ["string", "ZeroNode"], "required": True},
        "filters": {
            "type": "list",
            "schema": {"type": ["string", "FilterBase"]},
            "default": [],
        },
        "filters_threshold": {"type": "number", "default": 0, "required": False},
        "transport": {
            "type": ["string", "Callable", "ZeroTransport"],
            "required": False,
            "nullable": True,
            "default": None,
        },
    }
    ":class:`ZeroPipe` fields validators"

    @classmethod
    def _get_extra_types(cls):
        return [FilterBase]

    def __init__(
        self,
        node_a: Union[str, "ZeroNode"],
        node_b: Union[str, "ZeroNode"],
        filters: Iterable["FilterBase"] = None,
        filters_threshold: float = 0.5,
        transport: Optional[Union[str, Callable, "ZeroTransport"]] = ...,
        **kwargs
    ):
        """

        :param node_a: specify input node
        :type node_a: Union[str, ZeroNode]
        :param node_b: specify output node
        :type node_b: Union[str, ZeroNode]
        :param filters: list of the Filter instances (which inherits from abstract class `FilterBase`)
        :type filters: Iterable[FilterBase]
        :param filters_threshold: threshold for every filter's score in the filters list.
        :type filters_threshold: float
        :param transport: this is transport which will be default for every pipe's stream.
            If value == ... then transport_factory will be executed in the __init__.
            If value == None then transport_factory will be executed in the get_stream().
        :type transport: Union[str, Callable, ZeroTransport]

        """

        if isinstance(node_a, str) and not node_a.startswith("<"):
            node_a = ZeroNode.load(node_a)

        if isinstance(node_b, str) and not node_b.startswith("<"):
            node_b = ZeroNode.load(node_b)

        if transport is ...:
            transport = self.__class__._transport_factory(self)

        self.node_a = node_a
        self.node_b = node_b
        self.filters = filters
        self.filters_threshold = filters_threshold
        self.transport = transport

    @classmethod
    @contextmanager
    def transport_factory_context(
        cls, transport_factory: Union[Callable, "ZeroTransport"]
    ):
        """
        Context manager for the :func:`set_transport_factory` method
       """
        prev_transport_factory = cls._transport_factory

        cls.set_transport_factory(transport_factory)

        try:
            yield cls
        finally:
            cls._transport_factory = prev_transport_factory

    @classmethod
    def set_transport_factory(cls, transport_factory: Union[Callable, "ZeroTransport"]):
        """
        Set default transport factory. You can provide the ZeroTransport instances
        instead of Callable objects.

        :param transport_factory:
            any :class:`ZeroTransport <tethys.core.transports.transport_zero.ZeroTransport>` instance
            or any callable object that return the instance
        :type transport_factory: Union[Callable, ZeroTransport]
        """
        if isinstance(transport_factory, ZeroTransport):
            transport = transport_factory

            def transport_factory(_):
                return transport

        cls._transport_factory = transport_factory

    def filter_data_packet(
        self, data_packet: Any, session: "ZeroSession" = None
    ) -> bool:
        """
        Check all filters in the pipe. Return True
        if all filters return score that greater than filters_threshold


        :param data_packet: any data object
        :param session: optional param that extends context information
        :type session: ZeroSession
        :return: True or False, depends on the pipe's filters score.
        :rtype: bool
        """
        for _filter in self.filters or []:
            if (
                _filter.execute(data_packet, pipe=self, session=session)
                < self.filters_threshold
            ):
                return False
        return True

    def get_stream(self, session: "ZeroSession") -> "ZeroStream":
        """
        The method load or create ZeroStream instance according to pipe and session instances

        :param session: ZeroSession instance
        :type session: ZeroSession
        :return: ZeroStream instance that is attached to the pipe
        :rtype: ZeroStream
        """

        transport = self.transport or self.__class__._transport_factory(self)
        stream = ZeroStream(self, session, transport)

        if not stream.refresh():
            if session.closed:
                raise TethysSessionClosed(
                    "You cannot get the stream because "
                    "the session '{}' was closed".format(session.id)
                )

            if session.closing_mode == session.HARD_CLOSING_MODE:
                raise TethysSessionClosed(
                    "You cannot get the stream because "
                    "the session '{}' is in the hard closing state".format(session.id)
                )

            stream.save(save_dependency=False)

        return stream

    def pull(self, session: "ZeroSession", **kwargs) -> Generator:
        """
        Get data_packets from the pipe's stream using python Generator
        (execute :func:`ZeroStream.read() <tethys.core.streams.stream_zero.ZeroStream.read>` method).

        :param session: ZeroSession instance
        :type session: ZeroSession
        :return: data_packets generator
        :rtype: typing.Generator
        """
        stream = self.get_stream(session)
        closed = False

        if stream.closed:
            closed = True
            stream.open(save=False)

        for key, data_packet in stream.read(**kwargs):
            yield data_packet
            stream.ack(key)

        if closed:
            stream.close(save=False)

    def push(
        self, data_packet: Any, session: "ZeroSession", many: bool = False, **kwargs
    ) -> bool:
        """
        Send data_packet into the pipe's stream

        :param data_packet: any data object or list of the data objects (with many=True)
        :param session: ZeroSession instance
        :type session: ZeroSession
        :param many: if many=True then data_packet's elements will be sent one-by-one.
        :type many: bool
        :return: True or False, True if at least one data_packet has been sent
        :rtype: bool
        """

        if many is True:
            data_packet = list(
                filter(lambda x: self.filter_data_packet(x, session), data_packet)
            )
            if not data_packet:
                return False
        elif not self.filter_data_packet(data_packet, session):
            return False

        stream = self.get_stream(session)
        stream.write(data_packet, many=many, **kwargs)

        return True
