"""Unit tests for python -m memory CLI dispatch."""

import sys
from unittest.mock import patch

import pytest


def _run_main(args: list[str]) -> None:
    """Run __main__.main() with the given argv."""
    with patch.object(sys, "argv", ["python -m memory", *args]):
        from memory.__main__ import main

        main()


def test_mirror_load_dispatches():
    with patch("memory.skills.mirror.main") as mock_mirror_main:
        _run_main(["mirror", "load", "--journey", "mirror-poc"])

    mock_mirror_main.assert_called_once_with(["load", "--journey", "mirror-poc"])


def test_mirror_unknown_subcommand_exits():
    with pytest.raises(SystemExit):
        _run_main(["mirror", "nosuchsubcommand"])


def test_conversation_logger_status_dispatches():
    with patch("memory.cli.conversation_logger.main") as mock_logger_main:
        _run_main(["conversation-logger", "status"])

    mock_logger_main.assert_called_once_with(["status"])


def test_unknown_top_level_command_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        _run_main(["nosuchcommand"])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out


def test_backup_dispatches_without_leaking_the_top_level_command():
    def _check_argv() -> None:
        assert sys.argv == ["python -m memory", "--silent"]

    with patch("memory.cli.backup.main", side_effect=_check_argv) as mock_backup_main:
        _run_main(["backup", "--silent"])

    mock_backup_main.assert_called_once()


def test_journeys_dispatches_without_leaking_the_top_level_command():
    def _check_argv() -> None:
        assert sys.argv == ["python -m memory", "--mirror-home", "/tmp/pati"]

    with patch("memory.cli.journeys.main", side_effect=_check_argv) as mock_journeys_main:
        _run_main(["journeys", "--mirror-home", "/tmp/pati"])

    mock_journeys_main.assert_called_once()


def test_migrate_legacy_dispatches():
    with patch("memory.cli.migrate_legacy.main") as mock_migrate_legacy_main:
        _run_main(
            [
                "migrate-legacy",
                "validate",
                "--source",
                "legacy.db",
                "--target-home",
                "~/.mirror/vinicius",
            ]
        )

    mock_migrate_legacy_main.assert_called_once()
