"""Tests for transcript export path resolution."""

from pathlib import Path

from memory.cli.transcript_export import export_last_turn, export_transcript

_SAMPLE_JSONL = """
{"type":"user","timestamp":"2026-04-18T10:00:00Z","message":{"content":"Hello mirror"}}
{"type":"assistant","timestamp":"2026-04-18T10:00:01Z","message":{"content":[{"type":"text","text":"Hello back"}]}}
""".strip()


def test_export_last_turn_uses_explicit_mirror_home_transcript_dir(tmp_path):
    jsonl_path = tmp_path / "session.jsonl"
    jsonl_path.write_text(_SAMPLE_JSONL + "\n", encoding="utf-8")
    mirror_home = tmp_path / ".mirror" / "testuser"

    out_path = export_last_turn(str(jsonl_path), mirror_home=mirror_home)

    expected_dir = mirror_home / "exports" / "transcripts"
    assert Path(out_path).parent == expected_dir
    assert Path(out_path).exists()


def test_export_transcript_uses_explicit_mirror_home_transcript_dir(tmp_path):
    jsonl_path = tmp_path / "session.jsonl"
    jsonl_path.write_text(_SAMPLE_JSONL + "\n", encoding="utf-8")
    mirror_home = tmp_path / ".mirror" / "pati"

    out_path = export_transcript(str(jsonl_path), mirror_home=mirror_home)

    expected_dir = mirror_home / "exports" / "transcripts"
    assert Path(out_path).parent == expected_dir
    assert Path(out_path).exists()


def test_export_last_turn_uses_explicit_output_dir_over_mirror_home(tmp_path):
    jsonl_path = tmp_path / "session.jsonl"
    jsonl_path.write_text(_SAMPLE_JSONL + "\n", encoding="utf-8")
    mirror_home = tmp_path / ".mirror" / "testuser"
    output_dir = tmp_path / "custom-exports"

    out_path = export_last_turn(
        str(jsonl_path), output_dir=str(output_dir), mirror_home=mirror_home
    )

    assert Path(out_path).parent == output_dir


def test_export_transcript_uses_configured_transcript_export_dir_when_no_mirror_home(
    tmp_path, mocker
):
    jsonl_path = tmp_path / "session.jsonl"
    jsonl_path.write_text(_SAMPLE_JSONL + "\n", encoding="utf-8")
    configured_dir = tmp_path / "configured" / "transcripts"
    mocker.patch("memory.cli.transcript_export.TRANSCRIPT_EXPORT_DIR", configured_dir)

    out_path = export_transcript(str(jsonl_path))

    assert Path(out_path).parent == configured_dir
