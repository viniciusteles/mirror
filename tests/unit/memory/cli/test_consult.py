"""Tests for consult CLI behavior."""

from memory import MemoryClient
from memory.config import default_db_path_for_home


def test_consult_uses_context_from_explicit_mirror_home(mocker, tmp_path, capsys):
    mirror_home = tmp_path / ".mirror" / "pati"
    db_path = default_db_path_for_home(mirror_home)
    mem = MemoryClient(env="test", db_path=db_path)
    mem.set_identity("self", "soul", "Scoped soul")
    mem.set_identity("ego", "behavior", "Scoped behavior")
    mem.set_identity("ego", "identity", "Scoped ego")
    mem.set_identity("user", "identity", "Scoped user")

    sent = {}

    def _fake_send(model_id, messages):
        sent["model_id"] = model_id
        sent["messages"] = messages
        return mocker.Mock(
            model=model_id,
            content="ok",
            prompt_tokens=None,
            completion_tokens=None,
            generation_id=None,
        )

    mocker.patch("memory.cli.consult.send_to_model", side_effect=_fake_send)
    mocker.patch("memory.cli.consult.resolve_model", return_value="openai/gpt-test")
    mocker.patch("memory.cli.consult.cmd_credits")

    from memory.cli.consult import main

    main(["openai", "What now?", "--mirror-home", str(mirror_home)])

    assert sent["model_id"] == "openai/gpt-test"
    assert "Scoped soul" in sent["messages"][0]["content"]
    captured = capsys.readouterr()
    assert "Consulting openai/gpt-test" in captured.out
    assert "ok" in captured.out


def test_consult_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path):
    env_home = tmp_path / ".mirror" / "vinicius"
    explicit_home = tmp_path / ".mirror" / "pati"

    env_mem = MemoryClient(env="test", db_path=default_db_path_for_home(env_home))
    env_mem.set_identity("self", "soul", "Env soul")
    env_mem.set_identity("ego", "behavior", "Env behavior")
    env_mem.set_identity("ego", "identity", "Env ego")
    env_mem.set_identity("user", "identity", "Env user")

    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))
    explicit_mem.set_identity("self", "soul", "Explicit soul")
    explicit_mem.set_identity("ego", "behavior", "Explicit behavior")
    explicit_mem.set_identity("ego", "identity", "Explicit ego")
    explicit_mem.set_identity("user", "identity", "Explicit user")

    sent = {}

    def _fake_send(model_id, messages):
        sent["messages"] = messages
        return mocker.Mock(
            model=model_id,
            content="ok",
            prompt_tokens=None,
            completion_tokens=None,
            generation_id=None,
        )

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)
    mocker.patch("memory.cli.consult.send_to_model", side_effect=_fake_send)
    mocker.patch("memory.cli.consult.resolve_model", return_value="openai/gpt-test")
    mocker.patch("memory.cli.consult.cmd_credits")

    from memory.cli.consult import main

    main(["openai", "What now?", "--mirror-home", str(explicit_home)])

    system_prompt = sent["messages"][0]["content"]
    assert "Explicit soul" in system_prompt
    assert "Env soul" not in system_prompt
