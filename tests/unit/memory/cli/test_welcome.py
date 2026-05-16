"""Tests for the `python -m memory welcome` command."""

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from memory import MemoryClient
from memory.config import default_db_path_for_home

# ---------- helpers -------------------------------------------------------


JOURNEY_LAUNCH = """# Launch Mirror Mind
**Status:** active

## Description
Get the product launched.
"""

JOURNEY_PATH_LAUNCH = """# Launch path

**Current stage:** pre-launch
**Next:** write announcement

Rest of path...
"""


def _mem(tmp_path, user: str = "tester") -> tuple[MemoryClient, str]:
    home = tmp_path / ".mirror" / user
    mem = MemoryClient(env="test", db_path=default_db_path_for_home(home))
    return mem, str(home)


def _iso(offset: timedelta) -> str:
    return (datetime.now(timezone.utc) + offset).isoformat()


# ---------- empty / silent states ----------------------------------------


def test_welcome_empty_when_no_mirror_home_resolvable(monkeypatch, capsys):
    monkeypatch.delenv("MIRROR_HOME", raising=False)
    monkeypatch.delenv("MIRROR_USER", raising=False)

    from memory.cli.welcome import main

    main([])

    captured = capsys.readouterr()
    assert captured.out == ""


def test_welcome_empty_when_mirror_welcome_off(monkeypatch, tmp_path, capsys):
    mem, home = _mem(tmp_path)
    mem.set_identity("journey", "launch-mirror-mind", JOURNEY_LAUNCH)

    monkeypatch.setenv("MIRROR_WELCOME", "off")

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    captured = capsys.readouterr()
    assert captured.out == ""


def test_welcome_minimal_when_no_journey(tmp_path, capsys):
    _mem(tmp_path, user="alisson-vale")

    from memory.cli.welcome import main

    main(["--mirror-home", str(tmp_path / ".mirror" / "alisson-vale")])

    captured = capsys.readouterr().out
    assert "◇ Mirror · alisson-vale" in captured
    assert "Active journey" not in captured
    assert "Where shall we begin?" in captured


# ---------- with state ---------------------------------------------------


def test_welcome_with_active_journey_and_no_signal_shows_two_lines(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "launch-mirror-mind", JOURNEY_LAUNCH)
    mem.set_journey_path(journey="launch-mirror-mind", content=JOURNEY_PATH_LAUNCH)

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    assert "◇ Mirror · alisson-vale" in out
    assert "Active journey: launch-mirror-mind" in out
    assert "pre-launch" in out
    assert "write announcement" in out
    assert "Last insight" not in out
    assert "Last conversation" not in out
    assert "Where shall we begin?" in out


def test_welcome_renders_last_insight_when_recent_memory_exists(mocker, tmp_path, capsys):
    mocker.patch(
        "memory.services.memory.generate_embedding",
        return_value=np.zeros(1536, dtype=np.float32),
    )

    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "launch-mirror-mind", JOURNEY_LAUNCH)
    mem.set_journey_path(journey="launch-mirror-mind", content=JOURNEY_PATH_LAUNCH)
    mem.add_memory(
        title="courage matters more than readiness for the launch",
        content="...",
        memory_type="insight",
        layer="self",
        journey="launch-mirror-mind",
    )

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    assert 'Last insight: "courage matters more than readiness for the launch"' in out
    assert "Last conversation" not in out


def test_welcome_falls_back_to_recent_conversation_when_no_insight(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "launch-mirror-mind", JOURNEY_LAUNCH)
    mem.set_journey_path(journey="launch-mirror-mind", content=JOURNEY_PATH_LAUNCH)

    conv = mem.conversations.start_conversation(
        interface="pi",
        journey="launch-mirror-mind",
        title="refining the launch announcement",
    )
    # End it within the 48h window.
    mem.store.update_conversation(conv.id, ended_at=_iso(timedelta(hours=-14)))

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    assert "Last insight" not in out
    assert "Last conversation" in out
    assert "refining the launch announcement" in out


def test_welcome_picks_journey_of_most_recent_conversation(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "old-journey", JOURNEY_LAUNCH.replace("Launch", "Old"))
    mem.set_identity("journey", "current-focus", JOURNEY_LAUNCH.replace("Launch", "Current"))
    mem.set_journey_path(
        journey="current-focus",
        content="# Current path\n\n**Current stage:** building\n",
    )

    # Older conversation on the wrong journey.
    old = mem.conversations.start_conversation(interface="pi", journey="old-journey")
    mem.store.update_conversation(
        old.id,
        started_at=_iso(timedelta(days=-30)),
        ended_at=_iso(timedelta(days=-30, hours=1)),
    )
    # Recent conversation on current-focus.
    recent = mem.conversations.start_conversation(interface="pi", journey="current-focus")
    mem.store.update_conversation(recent.id, ended_at=_iso(timedelta(hours=-2)))

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    assert "Active journey: current-focus" in out
    assert "old-journey" not in out


def test_welcome_does_not_render_old_conversation_as_context(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "launch-mirror-mind", JOURNEY_LAUNCH)
    mem.set_journey_path(journey="launch-mirror-mind", content=JOURNEY_PATH_LAUNCH)

    conv = mem.conversations.start_conversation(
        interface="pi", journey="launch-mirror-mind", title="ancient talk"
    )
    mem.store.update_conversation(conv.id, ended_at=_iso(timedelta(days=-7)))

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    assert "Last conversation" not in out
    assert "ancient talk" not in out


def test_welcome_ends_with_invitation(tmp_path, capsys):
    _mem(tmp_path, user="alisson-vale")

    from memory.cli.welcome import main

    main(["--mirror-home", str(tmp_path / ".mirror" / "alisson-vale")])

    out = capsys.readouterr().out
    assert out.rstrip().endswith("→ Where shall we begin?")


# ---------- robustness --------------------------------------------------


@pytest.mark.parametrize(
    "stage_label",
    ["Current stage", "Etapa atual", "Fase"],
)
def test_welcome_handles_multiple_stage_labels(tmp_path, capsys, stage_label):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "j", JOURNEY_LAUNCH)
    mem.set_journey_path(journey="j", content=f"# Path\n\n**{stage_label}:** kickoff\n")

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    assert "kickoff" in out


def test_welcome_omits_dangling_separators_when_next_missing(tmp_path, capsys):
    mem, home = _mem(tmp_path, user="alisson-vale")
    mem.set_identity("journey", "j", JOURNEY_LAUNCH)
    mem.set_journey_path(journey="j", content="# Path\n\n**Current stage:** kickoff\n")

    from memory.cli.welcome import main

    main(["--mirror-home", home])

    out = capsys.readouterr().out
    # No trailing " · next:" fragment when next is absent.
    for line in out.splitlines():
        if line.startswith("Active journey"):
            assert not line.rstrip().endswith("·")
            assert "next:" not in line or line.split("next:")[1].strip()
