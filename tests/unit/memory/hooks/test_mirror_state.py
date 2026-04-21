from memory.client import MemoryClient
from memory.hooks import mirror_state


def _client(tmp_path):
    return MemoryClient(db_path=tmp_path / "memory.db")


def test_needs_inject_false_when_session_state_is_missing(tmp_path, mocker):
    client = _client(tmp_path)
    mocker.patch("memory.hooks.mirror_state._memory_client", return_value=client)

    assert mirror_state.needs_inject("sess-1") is False


def test_write_state_makes_one_session_active_and_needing_injection(tmp_path, mocker):
    client = _client(tmp_path)
    mocker.patch("memory.hooks.mirror_state._memory_client", return_value=client)

    mirror_state.write_state(True, persona="engineer", journey="mirror-poc", session_id="sess-1")

    assert mirror_state.needs_inject("sess-1") is True
    assert mirror_state.get_value("persona", "sess-1") == "engineer"
    assert mirror_state.get_value("journey", "sess-1") == "mirror-poc"


def test_mark_injected_is_isolated_per_session(tmp_path, mocker):
    client = _client(tmp_path)
    mocker.patch("memory.hooks.mirror_state._memory_client", return_value=client)

    mirror_state.write_state(True, persona="engineer", journey="mirror-poc", session_id="sess-a")
    mirror_state.write_state(True, persona="writer", journey="content", session_id="sess-b")

    mirror_state.mark_injected("sess-a")

    assert mirror_state.needs_inject("sess-a") is False
    assert mirror_state.needs_inject("sess-b") is True
    assert mirror_state.get_value("persona", "sess-b") == "writer"


def test_inactive_state_does_not_need_injection(tmp_path, mocker):
    client = _client(tmp_path)
    mocker.patch("memory.hooks.mirror_state._memory_client", return_value=client)

    mirror_state.write_state(False, session_id="sess-1")

    assert mirror_state.needs_inject("sess-1") is False


def test_missing_or_non_text_values_return_empty_string(tmp_path, mocker):
    client = _client(tmp_path)
    mocker.patch("memory.hooks.mirror_state._memory_client", return_value=client)

    client.store.upsert_runtime_session("sess-1")

    assert mirror_state.get_value("persona", "sess-1") == ""
    assert mirror_state.get_value("missing", "sess-1") == ""


def test_cli_warns_on_stderr_when_session_id_is_missing(capsys, mocker):
    mocker.patch("sys.argv", ["mirror_state", "needs-inject"])

    mirror_state.main()

    err = capsys.readouterr().err
    assert "--session-id" in err.lower() or "session-id" in err.lower()
