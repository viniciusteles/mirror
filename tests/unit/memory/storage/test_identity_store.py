"""Focused tests for identity storage behavior."""

from memory.models import Identity


def test_upsert_identity_preserves_id_when_updating(store):
    created = store.upsert_identity(Identity(layer="ego", key="behavior", content="First"))

    updated = store.upsert_identity(Identity(layer="ego", key="behavior", content="Second"))
    fetched = store.get_identity("ego", "behavior")

    assert updated.id == created.id
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.content == "Second"


def test_update_identity_metadata_preserves_content(store):
    store.upsert_identity(
        Identity(layer="journey", key="mirror", content="Original", metadata='{"old": true}')
    )

    store.update_identity_metadata("journey", "mirror", '{"project_path": "/tmp/mirror"}')
    fetched = store.get_identity("journey", "mirror")

    assert fetched is not None
    assert fetched.content == "Original"
    assert fetched.metadata == '{"project_path": "/tmp/mirror"}'


def test_delete_identity_returns_true_then_false(store):
    store.upsert_identity(Identity(layer="user", key="identity", content="User"))

    assert store.delete_identity("user", "identity") is True
    assert store.delete_identity("user", "identity") is False
