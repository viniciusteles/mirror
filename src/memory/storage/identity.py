"""Identity persistence operations."""

from datetime import datetime, timezone

from memory.models import Identity
from memory.storage.base import ConnectionBacked


class IdentityStore(ConnectionBacked):
    # --- Identity ---

    def upsert_identity(self, identity: Identity) -> Identity:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        existing = self.get_identity(identity.layer, identity.key)
        if existing:
            self.conn.execute(
                """UPDATE identity SET content = ?, version = ?, updated_at = ?, metadata = ?
                   WHERE layer = ? AND key = ?""",
                (
                    identity.content,
                    identity.version,
                    now,
                    identity.metadata,
                    identity.layer,
                    identity.key,
                ),
            )
            identity.id = existing.id
            identity.updated_at = now
        else:
            identity.created_at = now
            identity.updated_at = now
            self.conn.execute(
                """INSERT INTO identity (id, layer, key, content, version, created_at, updated_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    identity.id,
                    identity.layer,
                    identity.key,
                    identity.content,
                    identity.version,
                    identity.created_at,
                    identity.updated_at,
                    identity.metadata,
                ),
            )
        self.conn.commit()
        return identity

    def get_identity(self, layer: str, key: str) -> Identity | None:
        row = self.conn.execute(
            "SELECT * FROM identity WHERE layer = ? AND key = ?", (layer, key)
        ).fetchone()
        if not row:
            return None
        return Identity(**dict(row))

    def get_identity_by_layer(self, layer: str) -> list[Identity]:
        rows = self.conn.execute(
            "SELECT * FROM identity WHERE layer = ? ORDER BY key", (layer,)
        ).fetchall()
        return [Identity(**dict(r)) for r in rows]

    def get_all_identity(self) -> list[Identity]:
        rows = self.conn.execute("SELECT * FROM identity ORDER BY layer, key").fetchall()
        return [Identity(**dict(r)) for r in rows]

    def update_identity_metadata(self, layer: str, key: str, metadata: str) -> None:
        from memory.models import _now

        self.conn.execute(
            "UPDATE identity SET metadata = ?, updated_at = ? WHERE layer = ? AND key = ?",
            (metadata, _now(), layer, key),
        )
        self.conn.commit()

    def delete_identity(self, layer: str, key: str) -> bool:
        cursor = self.conn.execute("DELETE FROM identity WHERE layer = ? AND key = ?", (layer, key))
        self.conn.commit()
        return cursor.rowcount > 0
