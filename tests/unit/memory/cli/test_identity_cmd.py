"""Tests for the identity CLI commands."""

import pytest

from memory.client import MemoryClient
from memory.config import default_db_path_for_home


def _client(mirror_home):
    return MemoryClient(db_path=default_db_path_for_home(mirror_home))


# ---------------------------------------------------------------------------
# identity list
# ---------------------------------------------------------------------------


def test_list_shows_all_entries(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Be direct.")
    mem.set_identity("self", "soul", "Deep purpose.")

    from memory.cli.identity_cmd import main

    main(["list", "--mirror-home", str(home)])

    out = capsys.readouterr().out
    assert "[ego]" in out
    assert "behavior" in out
    assert "[self]" in out
    assert "soul" in out


def test_list_filters_by_layer(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Be direct.")
    mem.set_identity("self", "soul", "Deep purpose.")

    from memory.cli.identity_cmd import main

    main(["list", "--layer", "ego", "--mirror-home", str(home)])

    out = capsys.readouterr().out
    assert "behavior" in out
    assert "soul" not in out


def test_list_empty_db(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    _client(home)  # initialise DB

    from memory.cli.identity_cmd import main

    main(["list", "--mirror-home", str(home)])

    assert "No identity entries found." in capsys.readouterr().out


# ---------------------------------------------------------------------------
# identity get
# ---------------------------------------------------------------------------


def test_get_prints_content(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Be direct and honest.")

    from memory.cli.identity_cmd import main

    main(["get", "ego", "behavior", "--mirror-home", str(home)])

    assert "Be direct and honest." in capsys.readouterr().out


def test_get_exits_1_when_not_found(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    _client(home)

    from memory.cli.identity_cmd import main

    with pytest.raises(SystemExit) as exc:
        main(["get", "ego", "behavior", "--mirror-home", str(home)])

    assert exc.value.code == 1
    assert "No identity entry found" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# identity set
# ---------------------------------------------------------------------------


def test_set_creates_new_entry(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)

    from memory.cli.identity_cmd import main

    main(["set", "ego", "behavior", "--content", "New behavior.", "--mirror-home", str(home)])

    assert "created" in capsys.readouterr().out
    assert mem.get_identity("ego", "behavior") == "New behavior."


def test_set_updates_existing_entry(tmp_path, capsys):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Old behavior.")

    from memory.cli.identity_cmd import main

    main(["set", "ego", "behavior", "--content", "New behavior.", "--mirror-home", str(home)])

    assert "updated" in capsys.readouterr().out
    assert mem.get_identity("ego", "behavior") == "New behavior."


def test_set_reads_from_stdin(tmp_path, capsys, monkeypatch):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)

    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("Content from stdin."))

    from memory.cli.identity_cmd import main

    main(["set", "ego", "behavior", "--mirror-home", str(home)])

    assert mem.get_identity("ego", "behavior") == "Content from stdin."


def test_set_exits_1_on_empty_content(tmp_path, capsys, monkeypatch):
    home = tmp_path / ".mirror" / "testuser"
    _client(home)

    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("   "))

    from memory.cli.identity_cmd import main

    with pytest.raises(SystemExit) as exc:
        main(["set", "ego", "behavior", "--mirror-home", str(home)])

    assert exc.value.code == 1
    assert "empty" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# identity edit
# ---------------------------------------------------------------------------


def test_edit_saves_changed_content(tmp_path, capsys, mocker):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Original content.")

    def fake_editor(cmd):
        # cmd is [editor, tmp_path] — write new content to the file
        Path(cmd[1]).write_text("Edited content.", encoding="utf-8")

        class R:
            returncode = 0

        return R()

    from pathlib import Path

    mocker.patch("subprocess.run", side_effect=fake_editor)
    mocker.patch.dict("os.environ", {"EDITOR": "fakeeditor"}, clear=False)

    from memory.cli.identity_cmd import main

    main(["edit", "ego", "behavior", "--mirror-home", str(home)])

    out = capsys.readouterr().out
    assert "updated" in out
    assert mem.get_identity("ego", "behavior") == "Edited content."


def test_edit_no_changes_detected(tmp_path, capsys, mocker):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Same content.")

    def fake_editor(cmd):
        # Write back the same content — no changes
        from pathlib import Path

        Path(cmd[1]).write_text("Same content.", encoding="utf-8")

        class R:
            returncode = 0

        return R()

    mocker.patch("subprocess.run", side_effect=fake_editor)
    mocker.patch.dict("os.environ", {"EDITOR": "fakeeditor"}, clear=False)

    from memory.cli.identity_cmd import main

    main(["edit", "ego", "behavior", "--mirror-home", str(home)])

    assert "No changes" in capsys.readouterr().out
    assert mem.get_identity("ego", "behavior") == "Same content."


def test_edit_aborts_on_empty_content(tmp_path, capsys, mocker):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Original content.")

    def fake_editor(cmd):
        from pathlib import Path

        Path(cmd[1]).write_text("   ", encoding="utf-8")

        class R:
            returncode = 0

        return R()

    mocker.patch("subprocess.run", side_effect=fake_editor)
    mocker.patch.dict("os.environ", {"EDITOR": "fakeeditor"}, clear=False)

    from memory.cli.identity_cmd import main

    with pytest.raises(SystemExit) as exc:
        main(["edit", "ego", "behavior", "--mirror-home", str(home)])

    assert exc.value.code == 1
    assert mem.get_identity("ego", "behavior") == "Original content."


def test_edit_aborts_on_nonzero_editor_exit(tmp_path, capsys, mocker):
    home = tmp_path / ".mirror" / "testuser"
    mem = _client(home)
    mem.set_identity("ego", "behavior", "Original content.")

    def fake_editor(cmd):
        class R:
            returncode = 1

        return R()

    mocker.patch("subprocess.run", side_effect=fake_editor)
    mocker.patch.dict("os.environ", {"EDITOR": "fakeeditor"}, clear=False)

    from memory.cli.identity_cmd import main

    with pytest.raises(SystemExit) as exc:
        main(["edit", "ego", "behavior", "--mirror-home", str(home)])

    assert exc.value.code == 1
    assert mem.get_identity("ego", "behavior") == "Original content."


# ---------------------------------------------------------------------------
# seed bootstrap-only behaviour
# ---------------------------------------------------------------------------


def test_seed_skips_existing_entries_by_default(tmp_path, capsys):
    """seed without --force should not overwrite entries already in the DB."""
    import yaml

    from memory.client import MemoryClient

    # Use a DB at a known path; seed will also write to this path via db_path.
    db_path = tmp_path / "memory_test.db"
    mem = MemoryClient(db_path=db_path)
    mem.set_identity("ego", "behavior", "DB version — should not be overwritten.")

    identity_root = tmp_path / "identity"
    ego_dir = identity_root / "ego"
    ego_dir.mkdir(parents=True)
    (ego_dir / "behavior.yaml").write_text(
        yaml.dump({"behavior": "YAML version — should be ignored."}), encoding="utf-8"
    )

    from memory.cli.seed import seed

    # Pass db_path directly so seed writes to the same DB.
    results = seed(
        env="test",
        identity_root=identity_root,
        force=False,
        _db_path=db_path,
    )

    assert results["skipped"] >= 1
    assert mem.get_identity("ego", "behavior") == "DB version — should not be overwritten."


def test_seed_force_overwrites_existing_entries(tmp_path, capsys):
    """seed --force should overwrite entries already in the DB."""
    import yaml

    from memory.client import MemoryClient

    db_path = tmp_path / "memory_test.db"
    mem = MemoryClient(db_path=db_path)
    mem.set_identity("ego", "behavior", "DB version — will be overwritten.")

    identity_root = tmp_path / "identity"
    ego_dir = identity_root / "ego"
    ego_dir.mkdir(parents=True)
    (ego_dir / "behavior.yaml").write_text(
        yaml.dump({"behavior": "YAML version — should win with --force."}), encoding="utf-8"
    )

    from memory.cli.seed import seed

    results = seed(
        env="test",
        identity_root=identity_root,
        force=True,
        _db_path=db_path,
    )

    assert results["updated"] >= 1
    assert mem.get_identity("ego", "behavior") == "YAML version — should win with --force."
