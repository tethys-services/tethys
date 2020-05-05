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

from multiprocessing import Manager
from typing import TYPE_CHECKING, Any

from tethys.core.nodes.operators.operator_base import OperatorBase
from tethys.utils.iterable import flat_iter

_node_pipes = {}
_cursors = Manager().dict()

if TYPE_CHECKING:
    from tethys.core.streams.stream_zero import ZeroStream  # noqa: F401
    from tethys.core.sessions.sess_zero import ZeroSession  # noqa: F401


class RoundRobinBalancerOperator(OperatorBase):
    """
    This operator distributes data_packets between forward nodes (with round-robin algorithm)

    """

    @classmethod
    def _get_next(cls, node_id: str, session: "ZeroSession"):
        network = session.network

        if network.version not in _node_pipes:
            pipes_nodes = network.get_pipes_map()[node_id]

            _node_pipes[network.version] = list(
                flat_iter(
                    [b_node_pipes.values() for b_node_pipes in pipes_nodes.values()]
                )
            )

        if session.version not in _cursors:
            _cursors[session.version] = 0

        next_pipe_index = _cursors[session.version]
        next_pipe = _node_pipes[network.version][next_pipe_index]
        _cursors[session.version] = (_cursors[session.version] + 1) % len(
            _node_pipes[network.version]
        )

        return next_pipe

    def process(self, data_packet: Any, stream: "ZeroStream", **kwargs):
        """
        Resend data_packet to one of the forward nodes.

        :param data_packet: any data object
        :param stream: Any stream
        :type stream: StreamBase
        :return: None
        """

        session = stream.session
        cur_node = stream.pipe.node_b

        next_pipe = self._get_next(cur_node.id, session)
        next_pipe.push(data_packet, session)
