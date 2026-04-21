"""Tests for conversation-logger mirror-home targeting."""

from memory import MemoryClient
from memory.config import default_db_path_for_home


def test_status_uses_explicit_mirror_home_for_mute_state(mocker, tmp_path, capsys):
    env_home = tmp_path / ".mirror" / "vinicius"
    explicit_home = tmp_path / ".mirror" / "pati"
    (explicit_home / "mute").parent.mkdir(parents=True, exist_ok=True)
    (explicit_home / "mute").write_text("")

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.conversation_logger import main

    main(["--mirror-home", str(explicit_home), "status"])

    captured = capsys.readouterr()
    assert captured.out.strip() == "MUTED"


def test_log_user_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path):
    env_home = tmp_path / ".mirror" / "vinicius"
    explicit_home = tmp_path / ".mirror" / "pati"
    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.conversation_logger import main

    main(["--mirror-home", str(explicit_home), "log-user", "sess-1", "hello"])

    env_mem = MemoryClient(env="test", db_path=default_db_path_for_home(env_home))
    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))

    assert env_mem.store.conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0] == 0
    assert explicit_mem.store.conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0] == 1


def test_session_end_pi_explicit_mirror_home_uses_explicit_runtime_session(mocker, tmp_path):
    env_home = tmp_path / ".mirror" / "vinicius"
    explicit_home = tmp_path / ".mirror" / "pati"
    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))
    conv = explicit_mem.start_conversation(interface="pi")
    explicit_mem.store.upsert_runtime_session(
        "pi-session-id",
        conversation_id=conv.id,
        interface="pi",
    )

    mock_end = mocker.patch.object(explicit_mem, "end_conversation")
    mocker.patch("memory.cli.conversation_logger._memory_client", return_value=explicit_mem)

    from memory.cli.conversation_logger import main

    main(["--mirror-home", str(explicit_home), "session-end-pi", "pi-session-id"])

    mock_end.assert_called_once_with(conv.id, extract=False)
