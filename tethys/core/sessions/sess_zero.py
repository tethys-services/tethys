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
from typing import Union, Any, TYPE_CHECKING

from tethys.core.exceptions import TethysInputNodesNotFound, TethysSessionClosed
from tethys.core.nodes import ZeroNode
from tethys.core.regobjs.regobj_zero import ZeroRegistrableObject
from tethys.core.sessions.sess_base import SessionBase

if TYPE_CHECKING:
    from tethys.core.networks.network_zero import ZeroNetwork  # noqa: F401

log = logging.getLogger(__name__)


class ZeroSession(ZeroRegistrableObject, SessionBase):
    """
    The Session entity class of the Zero generation.
    The ZeroSession is a context for the streams.

    """

    SOFT_CLOSING_MODE = "<soft>"
    HARD_CLOSING_MODE = "<hard>"
    INSTANT_CLOSING_MODE = "<instant>"

    CLASS_PATH = "/sessions/"
    ":class:`ZeroSession` instances collection path in the repository"

    FIELDS_SCHEMA = {
        "network": {"type": ["string", "ZeroNetwork"], "required": True},
        "context": {"type": "dict", "default": {}, "required": False},
        "closing_mode": {
            "type": "string",
            "nullable": True,
            "default": None,
            "allowed": [SOFT_CLOSING_MODE, HARD_CLOSING_MODE, INSTANT_CLOSING_MODE],
        },
        "closed": {"type": "boolean", "nullable": False, "default": False},
        "parent": {
            "type": ["string", "ZeroSession"],
            "nullable": True,
            "default": None,
            "required": False,
        },
        "children": {
            "type": "list",
            "valuesrules": {"type": ["string", "ZeroSession"]},
        },
    }
    ":class:`ZeroSession` fields validators"

    def __init__(
        self, network: Union["ZeroNetwork", str], parent: "ZeroSession" = None, **kwargs
    ):
        """

        :param network: The network used to run streams in the session scope.
        :type network: ZeroNetwork
        :param parent: The parent session
        :type parent: ZeroSession
        """

        self.network = network

        self.closed = False
        self.closing_mode = None

        self.children = []
        self.parent = parent

    def __setattr__(self, key, value):
        old_parent = getattr(self, "parent", None)

        super().__setattr__(key, value)

        if key == "parent":
            if value and isinstance(value, ZeroSession):
                value.add_child(self)
            if old_parent:
                old_parent.remove_child(self)

    def add_child(self, child: "ZeroSession"):
        self.children.append(child.path)

    def remove_child(self, child: "ZeroSession"):
        self.children.remove(child.path)

    def get_children_dict(self):
        c_sessions = [ZeroSession.load(c_path) for c_path in self.children]
        return {child.id: child for child in c_sessions}

    def open(self, **kwargs) -> "ZeroSession":
        """
        This method changes the ZeroSession station to `closed=False`.

        :return: self object
        :rtype: ZeroSession
        """

        self.closed = False
        self.closing_mode = None

        return self.save(save_dependency=False)

    def _close_related_entities(self, mode):
        for child in self.get_children_dict().values():
            child.close(mode)

        if mode != self.SOFT_CLOSING_MODE:
            pipes = self.network.pipes.values()
        else:
            pipes = self.network.output_pipes

        for pipe in pipes:
            try:
                stream = pipe.get_stream(self)
                if not stream.closed:
                    stream.close()
            except TethysSessionClosed:
                logging.debug("Close method tried to close nonexistent stream")

    def close(self, mode: str = None) -> "ZeroSession":
        """
        This method changes the ZeroSession station to `closing_mode=mode`.
        All children also will be closed.

        :param mode: closing mode determines the mode of closing streams (default: INSTANT_CLOSING_MODE)
        :type mode: str
        :return: self object
        :rtype: ZeroSession
        """

        mode = mode or self.INSTANT_CLOSING_MODE

        if mode not in [
            self.INSTANT_CLOSING_MODE,
            self.HARD_CLOSING_MODE,
            self.SOFT_CLOSING_MODE,
        ]:
            raise ValueError("invalid closing mode")

        if mode == self.INSTANT_CLOSING_MODE:
            self.closed = True

        self.closing_mode = mode

        self._close_related_entities(mode)

        return self.save(save_dependency=False)

    def send(self, data_packet: Any, many: bool = False, **kwargs):
        """
        This method sends data_packet(s) to the input nodes.

        :param data_packet: any data object or list of the data objects (with many=True)
        :param many: if many=True then data_packet's elements will be sent one-by-one.
        :type many: bool
        """

        pipes_map = self.network.get_pipes_map()
        if ZeroNode.IN not in pipes_map:
            raise TethysInputNodesNotFound(
                "Input node not found in [{}] network".format(self.network.id)
            )

        input_pipes_nodes = pipes_map[ZeroNode.IN]

        for node_pipes in input_pipes_nodes.values():
            for pipe in node_pipes.values():
                pipe.push(data_packet, self, many=many, **kwargs)

    def _sync_closing_mode_with_parent(self):
        if (
            self.parent
            and self.parent.refresh()
            and (
                self.parent.closed or self.parent.closing_mode != self.SOFT_CLOSING_MODE
            )
        ):
            self.close(self.parent.closing_mode)

    def _sync_closing_mode_with_stream(self):
        if not self.closed:
            for pipe in self.network.pipes.values():

                try:
                    stream = pipe.get_stream(self)
                except TethysSessionClosed:
                    continue

                if not stream.closed:
                    break
            else:
                self.close()

    def refresh(self, **kwargs) -> Union["ZeroSession", None]:
        """
        Reload entity from the repository (without cache).
        Also this method updates streams and sessions states according to the closing mode.

        :return: return ZeroSession instance or None (when error like NotFound)
        :rtype: ZeroSession or None
        """

        if not super().refresh(**kwargs):
            return None

        self._sync_closing_mode_with_parent()
        self._sync_closing_mode_with_stream()

        return self

    def __enter__(self) -> "ZeroSession":
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(self.SOFT_CLOSING_MODE)
