"""Storage contract tests for identity_descriptors sidecar table."""

import pytest

from memory import MemoryClient

pytestmark = pytest.mark.unit


@pytest.fixture
def mem(tmp_path):
    db_path = str(tmp_path / "test.db")
    client = MemoryClient(db_path=db_path)
    yield client
    client.close()


class TestIdentityDescriptorStorage:
    def test_upsert_and_get_descriptor(self, mem):
        mem.store.upsert_descriptor("persona", "engineer", "Handles code and architecture.")
        d = mem.store.get_descriptor("persona", "engineer")
        assert d is not None
        assert d.layer == "persona"
        assert d.key == "engineer"
        assert d.descriptor == "Handles code and architecture."
        assert d.generated_at

    def test_get_descriptor_returns_none_when_absent(self, mem):
        result = mem.store.get_descriptor("persona", "nonexistent")
        assert result is None

    def test_upsert_overwrites_existing_descriptor(self, mem):
        mem.store.upsert_descriptor("persona", "engineer", "First version.")
        mem.store.upsert_descriptor("persona", "engineer", "Updated version.")
        d = mem.store.get_descriptor("persona", "engineer")
        assert d is not None
        assert d.descriptor == "Updated version."

    def test_get_descriptors_by_layer_returns_dict(self, mem):
        mem.store.upsert_descriptor("persona", "engineer", "Code and debugging.")
        mem.store.upsert_descriptor("persona", "writer", "Writing and publishing.")
        result = mem.store.get_descriptors_by_layer("persona")
        assert result == {
            "engineer": "Code and debugging.",
            "writer": "Writing and publishing.",
        }

    def test_get_descriptors_by_layer_returns_empty_dict_when_none(self, mem):
        result = mem.store.get_descriptors_by_layer("persona")
        assert result == {}

    def test_descriptors_isolated_by_layer(self, mem):
        mem.store.upsert_descriptor("persona", "engineer", "Code.")
        mem.store.upsert_descriptor("journey", "mirror", "Mirror Mind infra.")
        personas = mem.store.get_descriptors_by_layer("persona")
        journeys = mem.store.get_descriptors_by_layer("journey")
        assert list(personas.keys()) == ["engineer"]
        assert list(journeys.keys()) == ["mirror"]
