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

from unittest import mock
from unittest.mock import call

import pytest
from pytest import fixture

from tethys.core.exceptions import TethysSessionClosed, TethysInputNodesNotFound
from tethys.core.networks.network_zero import ZeroNetwork
from tethys.core.pipes.pipe_zero import ZeroPipe
from tethys.core.sessions.sess_zero import ZeroSession


class MockNetwork(ZeroNetwork):
    pass


class MockPipe(ZeroPipe):
    pass


class TestZeroSession:
    @fixture
    def stream(self):
        stream = mock.MagicMock()
        stream.closed = False

        return stream

    @fixture
    def pipe_in(self, stream):
        pipe = MockPipe("<in>", "<test>")
        pipe._stream = stream
        pipe.get_stream = mock.MagicMock(side_effect=lambda _: stream)
        pipe.push = mock.MagicMock()

        return pipe.save()

    @fixture
    def pipe_out(self, stream):
        pipe = MockPipe("<test>", "<out>")
        pipe._stream = stream
        pipe.get_stream = mock.MagicMock(side_effect=lambda _: stream)
        pipe.push = mock.MagicMock()

        return pipe.save()

    @fixture
    def pipe_out_without_stream(self):
        def raise_closed_exc(_):
            raise TethysSessionClosed

        pipe = MockPipe("<test>", "<out>")
        pipe._stream = None
        pipe.get_stream = mock.MagicMock(side_effect=raise_closed_exc)
        pipe.push = mock.MagicMock()

        return pipe.save()

    @fixture
    def network(self, pipe_in, pipe_out, pipe_out_without_stream):
        net = MockNetwork([pipe_in, pipe_out, pipe_out_without_stream])
        net.save()
        net.save = mock.MagicMock()

        return net

    @fixture
    def session(self, network):
        s1 = ZeroSession(network)
        s1.save = mock.MagicMock()

        return s1

    # init

    def test_init_child(self, network, session):
        s_child = ZeroSession(network, parent=session)

        assert s_child.parent == session
        assert session.children == [s_child.path]
        assert session.get_children_dict() == {s_child.id: s_child}

    # parent

    def test_set_parent(self, session, network):
        s_child = ZeroSession(network)
        s_child.parent = session

        assert s_child.parent == session
        assert session.children == [s_child.path]
        assert session.get_children_dict() == {s_child.id: s_child}

    def test_change_parent(self, session, network):
        parent2 = ZeroSession(network)
        s_child = ZeroSession(network)
        s_child.parent = session
        s_child.parent = parent2

        assert s_child.parent == parent2
        assert parent2.children == [s_child.path]
        assert parent2.get_children_dict() == {s_child.id: s_child}

        assert session.children == []
        assert session.get_children_dict() == {}

    # open

    def test_open(self, session):
        session.closing_mode = ZeroSession.HARD_CLOSING_MODE
        session.closed = True

        session.open(test_kw=1)

        assert session.closing_mode is None
        assert session.closed is False
        session.save.assert_called_once_with(save_dependency=False)

    # close

    def test_close(self, network, session):
        s_child = ZeroSession(network, parent=session)
        s_child.save = mock.MagicMock()

        session.close()

        assert session.closed is True
        assert session.closing_mode == session.INSTANT_CLOSING_MODE

        assert s_child.closed is True
        assert s_child.closing_mode == session.INSTANT_CLOSING_MODE

        network.save.assert_not_called()
        session.save.assert_called_once_with(save_dependency=False)
        s_child.save.assert_called_once_with(save_dependency=False)

        for pipe in network.pipes.values():
            pipe.get_stream.assert_has_calls(
                [call(s_child), call(session),]
            )
            if pipe._stream:
                pipe._stream.close.assert_has_calls(
                    [call(), call(),]
                )

    def test_close_hard(self, network, session):
        s_child = ZeroSession(network, parent=session)
        s_child.save = mock.MagicMock()

        session.close(session.HARD_CLOSING_MODE)

        assert session.closed is False
        assert session.closing_mode == session.HARD_CLOSING_MODE

        assert s_child.closed is False
        assert s_child.closing_mode == session.HARD_CLOSING_MODE

        network.save.assert_not_called()
        session.save.assert_called_once_with(save_dependency=False)
        s_child.save.assert_called_once_with(save_dependency=False)

        for pipe in network.pipes.values():
            pipe.get_stream.assert_has_calls(
                [call(s_child), call(session),]
            )
            if pipe._stream:
                pipe._stream.close.assert_has_calls(
                    [call(), call(),]
                )

    def test_close_soft(self, network, session):
        s_child = ZeroSession(network, parent=session)
        s_child.save = mock.MagicMock()

        session.close(session.SOFT_CLOSING_MODE)

        assert session.closed is False
        assert session.closing_mode == session.SOFT_CLOSING_MODE

        assert s_child.closed is False
        assert s_child.closing_mode == session.SOFT_CLOSING_MODE

        network.save.assert_not_called()
        session.save.assert_called_once_with(save_dependency=False)
        s_child.save.assert_called_once_with(save_dependency=False)

        for pipe in network.pipes.values():
            if pipe.node_b == "<out>":
                pipe.get_stream.assert_has_calls(
                    [call(s_child), call(session),]
                )
                if pipe._stream:
                    pipe._stream.close.assert_has_calls(
                        [call(), call(),]
                    )
            else:
                pipe.get_stream.assert_not_called()

    # send

    def test_send(self, session, network):
        session.send({"test": "data"}, test_kw=1)

        for pipe in network.pipes.values():
            if pipe.node_a == "<in>":
                pipe.push.assert_called_once_with(
                    {"test": "data"}, session, many=False, test_kw=1
                )
            else:
                pipe.push.assert_not_called()

    def test_send_to_empty_net(self, network):
        network.pipes_list = []

        s1 = ZeroSession(network)

        with pytest.raises(TethysInputNodesNotFound):
            s1.send({"test": "data"})

    # refresh

    def test_refresh_unsaved(self, session):
        assert session.refresh() is None

    def test_refresh_parent_check(self, session, network):
        parent = ZeroSession(network)
        parent.closed = True
        parent.closing_mode = session.HARD_CLOSING_MODE
        parent.load = lambda *_, **__: parent

        session.parent = parent
        session.load = lambda *_, **__: session

        assert session.refresh() is not None
        assert session.closed is False
        assert session.closing_mode is session.HARD_CLOSING_MODE

    def test_refresh_streams_check(self, session, network):
        session.load = lambda *_, **__: session

        assert session.refresh() is not None
        assert session.closed is False
        assert session.closing_mode is None

        for i, pipe in enumerate(network.pipes.values()):
            if not i:
                pipe.get_stream.assert_has_calls(
                    [call(session),]
                )
            else:
                pipe.get_stream.assert_not_called()

    def test_refresh_closed_streams_check(self, session):
        network = MockNetwork()
        network.pipes_list = []
        session.network = network
        session.load = lambda *_, **__: session

        assert session.refresh() is not None
        assert session.closed is True
        assert session.closing_mode is session.INSTANT_CLOSING_MODE

        for pipe in network.pipes.values():
            pipe.get_stream.assert_has_calls([call(session)])

    # context

    def test_context(self, session):
        session.open = mock.MagicMock()
        session.close = mock.MagicMock()
        with session:
            assert session.open.call_count == 1
            session.close.assert_not_called()
        session.close.assert_called_once_with(session.SOFT_CLOSING_MODE)
