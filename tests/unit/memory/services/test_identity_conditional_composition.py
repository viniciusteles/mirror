"""Tests for conditional identity composition gated by touches_identity.

Tests load_mirror_context() directly on IdentityService — no need to mock
mirror.py's routing logic or module-level config constants.
"""

import pytest

pytestmark = pytest.mark.unit

_SOUL = "I am the soul."
_EGO_IDENTITY = "I am the ego identity."
_BEHAVIOR = "I behave directly."
_USER = "User is Vinícius."


@pytest.fixture
def seeded_identity(identity_service):
    identity_service.set_identity("self", "soul", _SOUL)
    identity_service.set_identity("ego", "behavior", _BEHAVIOR)
    identity_service.set_identity("ego", "identity", _EGO_IDENTITY)
    identity_service.set_identity("user", "identity", _USER)
    return identity_service


class TestTouchesIdentityTrue:
    def test_soul_present(self, seeded_identity):
        ctx = seeded_identity.load_mirror_context(touches_identity=True)
        assert _SOUL in ctx

    def test_ego_identity_present(self, seeded_identity):
        ctx = seeded_identity.load_mirror_context(touches_identity=True)
        assert _EGO_IDENTITY in ctx

    def test_behavior_present(self, seeded_identity):
        ctx = seeded_identity.load_mirror_context(touches_identity=True)
        assert _BEHAVIOR in ctx

    def test_user_identity_present(self, seeded_identity):
        ctx = seeded_identity.load_mirror_context(touches_identity=True)
        assert _USER in ctx


class TestTouchesIdentityFalse:
    def test_soul_absent(self, seeded_identity):
        ctx = seeded_identity.load_mirror_context(touches_identity=False)
        assert _SOUL not in ctx

    def test_ego_identity_absent(self, seeded_identity):
        ctx = seeded_identity.load_mirror_context(touches_identity=False)
        assert _EGO_IDENTITY not in ctx

    def test_behavior_still_present(self, seeded_identity):
        """ego/behavior is always loaded — governs tone, not deep identity."""
        ctx = seeded_identity.load_mirror_context(touches_identity=False)
        assert _BEHAVIOR in ctx

    def test_user_identity_still_present(self, seeded_identity):
        """user/identity is always loaded — provides basic user context."""
        ctx = seeded_identity.load_mirror_context(touches_identity=False)
        assert _USER in ctx


class TestDefaultBehaviour:
    def test_default_loads_full_context(self, seeded_identity):
        """touches_identity defaults True — existing callers get full context."""
        ctx = seeded_identity.load_mirror_context()
        assert _SOUL in ctx
        assert _EGO_IDENTITY in ctx

    def test_persona_loaded_regardless_of_touches_identity(self, seeded_identity):
        seeded_identity.set_identity("persona", "engineer", "I am the engineer.")
        ctx_with = seeded_identity.load_mirror_context(persona="engineer", touches_identity=True)
        ctx_without = seeded_identity.load_mirror_context(
            persona="engineer", touches_identity=False
        )
        assert "I am the engineer." in ctx_with
        assert "I am the engineer." in ctx_without

    def test_journey_loaded_regardless_of_touches_identity(self, seeded_identity):
        seeded_identity.set_identity("journey", "mirror", "Mirror Mind journey.")
        ctx_with = seeded_identity.load_mirror_context(journey="mirror", touches_identity=True)
        ctx_without = seeded_identity.load_mirror_context(journey="mirror", touches_identity=False)
        assert "Mirror Mind journey." in ctx_with
        assert "Mirror Mind journey." in ctx_without
