"""Tests for the extension error hierarchy."""

from __future__ import annotations

import pytest

from memory.extensions import (
    ExtensionError,
    ExtensionLoadError,
    ExtensionMigrationError,
    ExtensionPermissionError,
    ExtensionValidationError,
)


def test_all_errors_inherit_from_extension_error():
    for cls in (
        ExtensionValidationError,
        ExtensionMigrationError,
        ExtensionPermissionError,
        ExtensionLoadError,
    ):
        assert issubclass(cls, ExtensionError)


def test_error_without_extension_id_keeps_plain_message():
    err = ExtensionValidationError("missing field 'id'")
    assert str(err) == "missing field 'id'"
    assert err.extension_id is None


def test_error_with_extension_id_prefixes_message():
    err = ExtensionMigrationError("checksum mismatch", extension_id="finances")
    assert str(err) == "[extension/finances] checksum mismatch"
    assert err.extension_id == "finances"


def test_caller_can_catch_family_in_one_clause():
    with pytest.raises(ExtensionError):
        raise ExtensionPermissionError("write outside prefix", extension_id="hello")
