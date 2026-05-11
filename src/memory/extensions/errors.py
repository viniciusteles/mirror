"""Exception hierarchy for the extension system.

All exceptions raised by the extension contract inherit from
``ExtensionError`` so callers can catch the whole family with a single
``except`` clause. Each subclass carries the optional ``extension_id``
of the offending extension when known, which makes log lines and error
messages easy to attribute.
"""

from __future__ import annotations


class ExtensionError(Exception):
    """Base class for every error raised by the extension subsystem.

    ``extension_id`` is optional because some errors (e.g. malformed
    manifest discovered during scanning) happen before the id is known.
    """

    def __init__(self, message: str, *, extension_id: str | None = None) -> None:
        super().__init__(self._format(message, extension_id))
        self.extension_id = extension_id

    @staticmethod
    def _format(message: str, extension_id: str | None) -> str:
        if extension_id:
            return f"[extension/{extension_id}] {message}"
        return message


class ExtensionValidationError(ExtensionError):
    """Raised when an extension's manifest fails validation."""


class ExtensionMigrationError(ExtensionError):
    """Raised when a SQL migration fails to apply.

    Covers prefix violations, checksum mismatches, and SQL execution
    errors. The cause (when available) is chained through ``__cause__``.
    """


class ExtensionPermissionError(ExtensionError):
    """Raised when an extension attempts to write outside its table prefix."""


class ExtensionLoadError(ExtensionError):
    """Raised when importing or registering an extension fails."""
