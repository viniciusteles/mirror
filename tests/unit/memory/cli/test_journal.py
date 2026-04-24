"""Tests for journal CLI behavior."""

from memory import MemoryClient
from memory.config import default_db_path_for_home


def _mock_journal_classification(mocker) -> None:
    mocker.patch(
        "memory.intelligence.extraction.classify_journal_entry",
        return_value={"title": "Scoped journal", "layer": "ego", "tags": ["note"]},
    )
    mocker.patch("memory.services.memory.generate_embedding", return_value=[0.1, 0.2, 0.3])
    mocker.patch("memory.services.memory.embedding_to_bytes", return_value=b"embedding")


def test_journal_writes_to_explicit_mirror_home(mocker, tmp_path, capsys):
    _mock_journal_classification(mocker)
    mirror_home = tmp_path / ".mirror" / "pati"

    from memory.cli.journal import main

    main(["--mirror-home", str(mirror_home), "entry for explicit home"])

    captured = capsys.readouterr()
    assert "Journal entry recorded" in captured.out

    mem = MemoryClient(env="test", db_path=default_db_path_for_home(mirror_home))
    memories = mem.get_by_type("journal")
    assert len(memories) == 1
    assert memories[0].content == "entry for explicit home"


def test_journal_explicit_mirror_home_overrides_environment_selection(mocker, tmp_path, capsys):
    _mock_journal_classification(mocker)
    env_home = tmp_path / ".mirror" / "testuser"
    explicit_home = tmp_path / ".mirror" / "pati"

    mocker.patch.dict("os.environ", {"MIRROR_HOME": str(env_home)}, clear=False)

    from memory.cli.journal import main

    main(["--mirror-home", str(explicit_home), "scoped entry"])

    captured = capsys.readouterr()
    assert "Journal entry recorded" in captured.out

    env_mem = MemoryClient(env="test", db_path=default_db_path_for_home(env_home))
    explicit_mem = MemoryClient(env="test", db_path=default_db_path_for_home(explicit_home))
    assert env_mem.get_by_type("journal") == []
    explicit_entries = explicit_mem.get_by_type("journal")
    assert len(explicit_entries) == 1
    assert explicit_entries[0].content == "scoped entry"
