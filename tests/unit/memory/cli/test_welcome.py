"""Tests for the `python -m memory welcome` command."""

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from memory import MemoryClient
from memory.config import default_db_path_for_home

JOURNEY_ACTIVE = """# Sample journey
**Status:** active

## Description
A scoped journey.
"""

JOURNEY_PAUSED = """# Paused journey
**Status:** paused

## Description
A paused journey.
"""

PERSONA_BODY = """# Persona
A test persona.
"""


def _mem(tmp_path, user: str = "tester") -> tuple[MemoryClient, str]:
    home = tmp_path / ".mirror" / user
    mem = MemoryClient(env="test", db_path=default_db_path_for_home(home))
    return mem, str(home)


def _iso(offset: timedelta) -> str:
    return (datetime.now(timezone.utc) + offset).isoformat()


# ---------- silent states -----------------------------------------------


def test_welcome_empty_when_no_mirror_home_resolvable(monkeypatch, capsys):
    monkeypatch.delenv("MIRROR_HOME", raising=False)
    monkeypatch.delenv("MIRROR_USER", raising=False)

    from memory.cli.welcome import main

    main([])

    captured = capsys.readouterr()
    assert captured.out == ""


def test_welcome_empty_when_mirror_welcome_off(monkeypatch, tmp_path, capsys):
    _mem(tmp_path)

    monkeypatch.setenv("MIRROR_WELCOME", "off")

    from memory.cli.welcome import main

    main(["--mirror-home", str(tmp_path / ".mirror" / "tester")])

    captured = capsys.readouterr()
    assert captured.out == ""


# ---------- structure ---------------------------------------------------


def test_welcome_has_three_visible_lines_and_blank_before_invitation(tmp_path, capsys):
    _mem(tmp_path, user="alisson-vale")

    from memory.cli.welcome import main

    main(["--mirror-home", str(tmp_path / ".mirror" / "alisson-vale")])

    out = capsys.readouterr().out
    lines = out.splitlines()
    assert lines[0] == "◇ Mirror · alisson-vale"
    # Stats line is always present, even for an empty database.
    assert "journeys" in lines[1]
    assert lines[2] == ""
    assert lines[3] == "→ Where shall we begin?"


def test_welcome_ends_with_invitation(tmp_path, capsys):
    _mem(tmp_path, user="alisson-vale")

    from memory.cli.welcome import main

    main(["--mirror-home", str(tmp_path / ".mirror" / "alisson-vale")])

    out = capsys.readouterr().out
    assert out.rstrip().endswith("→ Where shall we begin?")


# ---------- stats content -----------------------------------------------


def test_welcome_renders_zeroes_on_fresh_database(tmp_path, capsys):
    _mem(tmp_path, user="alisson-vale")

    from memory.cli.welcome import main

    main(["--mirror-home", str(tmp_path / ".mirror" / "alisson-vale")])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "journeys" in line)
    assert "0 journeys" in stats
    assert "0 personas" in stats
    assert "0 memories" in stats
    assert "0 conversations" in stats
    assert "since today" in stats


def test_welcome_counts_active_journeys_and_skips_paused(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "alpha", JOURNEY_ACTIVE)
    mem.set_identity("journey", "beta", JOURNEY_ACTIVE)
    mem.set_identity("journey", "gamma", JOURNEY_PAUSED)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "journeys" in line)
    assert "2 journeys" in stats


def test_welcome_counts_personas(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("persona", "therapist", PERSONA_BODY)
    mem.set_identity("persona", "strategist", PERSONA_BODY)
    mem.set_identity("persona", "researcher", PERSONA_BODY)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "personas" in line)
    assert "3 personas" in stats


def test_welcome_counts_memories(mocker, tmp_path, capsys):
    mocker.patch(
        "memory.services.memory.generate_embedding",
        return_value=np.zeros(1536, dtype=np.float32),
    )
    mem, home = _mem(tmp_path, user="alisson-vale")
    for i in range(4):
        mem.add_memory(
            title=f"m{i}",
            content="...",
            memory_type="insight",
            layer="self",
            journey="alpha",
        )

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "memories" in line)
    assert "4 memories" in stats


def test_welcome_counts_conversations_and_renders_since_month(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    first = mem.conversations.start_conversation(interface="pi", journey="alpha")
    mem.store.update_conversation(first.id, started_at="2024-12-15T10:00:00+00:00")
    mem.conversations.start_conversation(interface="pi", journey="alpha")
    mem.conversations.start_conversation(interface="pi", journey="alpha")

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "conversations" in line)
    assert "3 conversations" in stats
    assert "since Dec 2024" in stats


def test_welcome_uses_thousands_separator_above_a_thousand(mocker, tmp_path, capsys):
    mocker.patch(
        "memory.services.memory.generate_embedding",
        return_value=np.zeros(1536, dtype=np.float32),
    )
    mem, home = _mem(tmp_path, user="alisson-vale")

    # Bulk-insert via the store to keep the test fast.
    from memory.models import Memory

    for i in range(1247):
        m = Memory(
            title=f"m{i}",
            content="x",
            memory_type="insight",
            layer="self",
        )
        mem.store.create_memory(m)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "memories" in line)
    assert "1,247 memories" in stats


# ---------- order and shape --------------------------------------------


def test_welcome_stats_line_order_is_stable(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "alpha", JOURNEY_ACTIVE)
    mem.set_identity("persona", "p1", PERSONA_BODY)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "journeys" in line)
    # Order: journeys · personas · memories · conversations · since ...
    idx_j = stats.index("journeys")
    idx_p = stats.index("personas")
    idx_m = stats.index("memories")
    idx_c = stats.index("conversations")
    idx_s = stats.index("since")
    assert idx_j < idx_p < idx_m < idx_c < idx_s


def test_welcome_uses_middot_separator(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "alpha", JOURNEY_ACTIVE)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "journeys" in line)
    assert " · " in stats


@pytest.mark.parametrize(
    "month_iso, expected",
    [
        ("2024-01-01T00:00:00+00:00", "since Jan 2024"),
        ("2025-05-15T12:00:00+00:00", "since May 2025"),
        ("2026-11-30T23:59:59+00:00", "since Nov 2026"),
    ],
)
def test_welcome_since_label_formats_month_year(tmp_path, capsys, month_iso, expected):
    mem, home = _mem(tmp_path, user="alisson-vale")
    conv = mem.conversations.start_conversation(interface="pi", journey="x")
    mem.store.update_conversation(conv.id, started_at=month_iso)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    stats = next(line for line in out.splitlines() if "journeys" in line)
    assert expected in stats
