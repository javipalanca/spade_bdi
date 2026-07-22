from collections import deque
from unittest.mock import MagicMock, patch, mock_open

import pytest

from spade_bdi.bdi import BDIAgent
from spade_bdi.bdi_behaviour import BDIBehaviour


@pytest.fixture
def bdi_agent():
    jid = "test@localhost"
    pwd = "1234"
    asl_file_path = MagicMock()

    yield BDIAgent(jid, pwd, asl_file_path)


def test_init():
    jid = "test@localhost"
    pwd = "1234"
    asl_file_path = MagicMock()
    with (
        patch("spade_bdi.bdi.BDIAgent._load_asl", autospec=True) as mock_load_ask,
        patch("spade_bdi.bdi.BDIAgent.add_behaviour", autospec=True) as mock_add_beh,
        patch("spade_bdi.bdi.BDIAgent.add_custom_actions") as mock_add_custom_act,
        patch("spade_bdi.bdi.asp") as mock_asp,
        patch("spade_bdi.bdi.asp_runtime") as mock_asp_runtime,
        patch("spade_bdi.bdi.asp_stdlib") as mock_asp_stdlib,
    ):
        mock_bdi_instance = MagicMock()

        def set_bdi(*args, **kwargs):
            instance = args[0]
            instance.bdi = mock_bdi_instance

        def start_bdi(*args, **kwargs):
            instance = args[0]
            instance.bdi_enabled = True

        mock_add_beh.side_effect = set_bdi
        mock_load_ask.side_effect = start_bdi

        bdi_agent = BDIAgent(jid, pwd, asl_file_path)

        assert bdi_agent.bdi_env == mock_asp_runtime.Environment.return_value
        assert bdi_agent.bdi_actions == mock_asp.Actions.return_value
        assert bdi_agent.asl_file == asl_file_path
        assert bdi_agent.bdi_enabled is True
        assert isinstance(bdi_agent.bdi_intention_buffer, deque)
        assert bdi_agent.bdi == mock_bdi_instance
        assert bdi_agent.bdi_agent is None

        mock_asp.Actions.assert_called_once_with(mock_asp_stdlib.actions)
        bdi_agent.bdi.add_actions.assert_called_once()
        mock_add_custom_act.assert_called_once_with(bdi_agent.bdi_actions)
        mock_load_ask.assert_called_once()
        mock_add_beh.assert_called_once()
        beh_args = mock_add_beh.call_args[0]
        assert beh_args[0] == bdi_agent
        assert isinstance(beh_args[1], BDIBehaviour)
        assert beh_args[2].get_metadata("performative") == "BDI"


def test_pause_bdi(bdi_agent):
    bdi_agent.bdi_enabled = True

    bdi_agent.pause_bdi()

    assert bdi_agent.bdi_enabled is False


def test_resume_bdi(bdi_agent):
    bdi_agent.bdi_enabled = False

    bdi_agent.resume_bdi()

    assert bdi_agent.bdi_enabled is True


def test_add_behaviour(bdi_agent):
    bdi_agent.bdi = None
    beh = MagicMock(spec=BDIBehaviour)

    bdi_agent.add_behaviour(beh)

    assert bdi_agent.bdi is not None
    assert isinstance(bdi_agent.bdi, BDIBehaviour)
    assert beh in bdi_agent.behaviours


def test_set_asl(bdi_agent):
    asl_mock = "fake/asl"
    bdi_agent.asl_file = "bad/ask"
    bdi_agent._load_asl = MagicMock()

    bdi_agent.set_asl(asl_mock)

    assert bdi_agent.asl_file == asl_mock
    bdi_agent._load_asl.assert_called_once()


def test_load_asl(bdi_agent):
    asl_payload = "!start. +!start : true <- .print('hola')."
    mock_file = mock_open(read_data=asl_payload)
    bdi_agent.bdi_env = MagicMock()

    with patch("spade_bdi.bdi.open", mock_file):
        bdi_agent._load_asl()

    mock_file.assert_called_once_with(bdi_agent.asl_file)
    bdi_agent.bdi_env.build_agent.assert_called_once_with(
        mock_file(), bdi_agent.bdi_actions
    )
    assert bdi_agent.bdi_agent.name == "test@localhost"
    assert bdi_agent.bdi_enabled is True


def test_load_asl_not_found(bdi_agent):
    with (
        patch("spade_bdi.bdi.open", side_effect=FileNotFoundError),
        patch("spade_bdi.bdi.logger") as mock_logger,
        patch("spade_bdi.bdi.BDIAgent.pause_bdi"),
        patch("spade_bdi.bdi.BDIAgent.resume_bdi"),
    ):
        bdi_agent._load_asl()

        assert bdi_agent.asl_file is None
        assert bdi_agent.pause_bdi.call_count == 2
        assert bdi_agent.resume_bdi.call_count == 0

        mock_logger.info.assert_called_once_with(
            "Warning: ASL specified for test@localhost does not exist. Disabling BDI."
        )
