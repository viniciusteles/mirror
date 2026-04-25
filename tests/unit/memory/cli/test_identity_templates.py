"""Tests for repository identity starter templates."""

import json
from pathlib import Path

from memory.cli.seed import load_journey_content, load_persona_content

TEMPLATES_IDENTITY_ROOT = Path(__file__).resolve().parents[4] / "templates" / "identity"


def test_starter_persona_templates_are_meaningful_runtime_defaults():
    personas_dir = TEMPLATES_IDENTITY_ROOT / "personas"

    assert sorted(path.name for path in personas_dir.glob("*.yaml")) == [
        "engineer.yaml",
        "thinker.yaml",
        "writer.yaml",
    ]

    for persona_id in ["writer", "thinker", "engineer"]:
        loaded_id, content, version, metadata_json = load_persona_content(
            personas_dir / f"{persona_id}.yaml"
        )
        metadata = json.loads(metadata_json)

        assert loaded_id == persona_id
        assert version == "1.0.0"
        assert "your-persona" not in content
        assert len(content) > 500
        assert metadata["routing_keywords"]


def test_starter_journey_template_is_personal_growth():
    journeys_dir = TEMPLATES_IDENTITY_ROOT / "journeys"

    assert sorted(path.name for path in journeys_dir.glob("*.yaml")) == ["personal-growth.yaml"]

    journey_id, content, version = load_journey_content(journeys_dir / "personal-growth.yaml")

    assert journey_id == "personal-growth"
    assert version == "1.0.0"
    assert "# Personal Growth" in content
    assert "your-journey" not in content
    assert len(content) > 500
