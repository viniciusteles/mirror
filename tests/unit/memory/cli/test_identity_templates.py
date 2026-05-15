"""Tests for repository identity starter templates."""

import json
from pathlib import Path

import yaml

from memory.cli.seed import load_journey_content, load_persona_content

TEMPLATES_IDENTITY_ROOT = Path(__file__).resolve().parents[4] / "templates" / "identity"


_EXPECTED_PERSONAS = [
    "coach.yaml",
    "designer.yaml",
    "doctor.yaml",
    "engineer.yaml",
    "financial.yaml",
    "prompt-engineer.yaml",
    "researcher.yaml",
    "strategist.yaml",
    "teacher.yaml",
    "therapist.yaml",
    "thinker.yaml",
    "writer.yaml",
]


def test_starter_persona_templates_are_meaningful_runtime_defaults():
    personas_dir = TEMPLATES_IDENTITY_ROOT / "personas"

    assert sorted(path.name for path in personas_dir.glob("*.yaml")) == _EXPECTED_PERSONAS

    for persona_file in personas_dir.glob("*.yaml"):
        _loaded_id, content, version, metadata_json = load_persona_content(persona_file)
        metadata = json.loads(metadata_json)

        assert version == "1.0.0", f"{persona_file.name}: expected version 1.0.0"
        assert "your-persona" not in content, f"{persona_file.name}: contains placeholder text"
        assert "{{user_name}}" not in content, f"{persona_file.name}: contains unsubstituted token"
        assert len(content) > 500, f"{persona_file.name}: content too short"
        assert metadata["routing_keywords"], f"{persona_file.name}: missing routing_keywords"


def test_core_identity_templates_have_real_content():
    """Verify the core identity YAML files ship with real, non-placeholder content."""
    # constraints.yaml is intentionally empty by default — users add their own
    required_files = [
        ("self/soul.yaml", "soul"),
        ("ego/identity.yaml", "identity"),
        ("ego/behavior.yaml", "behavior"),
        ("user/identity.yaml", "user"),
    ]
    for yaml_path, field in required_files:
        full_path = TEMPLATES_IDENTITY_ROOT / yaml_path
        assert full_path.exists(), f"Missing template: {yaml_path}"
        with open(full_path) as f:
            data = yaml.safe_load(f)
        content = data.get(field, "")
        assert content, f"{yaml_path}: field '{field}' is empty"
        assert len(content) > 200, f"{yaml_path}: content too short to be real"
        assert "Describe" not in content or yaml_path.startswith("organization"), (
            f"{yaml_path}: still contains fill-in placeholder instructions"
        )
        assert "Examples:" not in content or yaml_path.startswith("organization"), (
            f"{yaml_path}: still contains fill-in example instructions"
        )


def test_user_identity_template_contains_user_name_token():
    """The user identity template must use {{user_name}} so init can substitute it."""
    user_yaml = TEMPLATES_IDENTITY_ROOT / "user" / "identity.yaml"
    content = user_yaml.read_text(encoding="utf-8")
    assert "{{user_name}}" in content, "user/identity.yaml must contain {{user_name}} token"


def test_soul_template_contains_user_name_token():
    """The soul template must use {{user_name}} so init can substitute it."""
    soul_yaml = TEMPLATES_IDENTITY_ROOT / "self" / "soul.yaml"
    content = soul_yaml.read_text(encoding="utf-8")
    assert "{{user_name}}" in content, "self/soul.yaml must contain {{user_name}} token"


def test_starter_journey_template_is_personal_growth():
    journeys_dir = TEMPLATES_IDENTITY_ROOT / "journeys"

    assert sorted(path.name for path in journeys_dir.glob("*.yaml")) == ["personal-growth.yaml"]

    journey_id, content, version = load_journey_content(journeys_dir / "personal-growth.yaml")

    assert journey_id == "personal-growth"
    assert version == "1.0.0"
    assert "# Personal Growth" in content
    assert "your-journey" not in content
    assert len(content) > 500
