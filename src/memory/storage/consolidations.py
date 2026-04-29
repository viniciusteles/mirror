"""Consolidation persistence operations."""

from datetime import datetime, timezone

from memory.models import Consolidation
from memory.storage.base import ConnectionBacked


class ConsolidationStore(ConnectionBacked):
    # --- Consolidations ---

    def create_consolidation(self, consolidation: Consolidation) -> Consolidation:
        self.conn.execute(
            """INSERT INTO consolidations
               (id, action, proposal, result, source_memory_ids, target_layer,
                target_key, rationale, status, created_at, reviewed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                consolidation.id,
                consolidation.action,
                consolidation.proposal,
                consolidation.result,
                consolidation.source_memory_ids,
                consolidation.target_layer,
                consolidation.target_key,
                consolidation.rationale,
                consolidation.status,
                consolidation.created_at,
                consolidation.reviewed_at,
            ),
        )
        self.conn.commit()
        return consolidation

    def get_consolidation(self, consolidation_id: str) -> Consolidation | None:
        row = self.conn.execute(
            "SELECT * FROM consolidations WHERE id = ?", (consolidation_id,)
        ).fetchone()
        return Consolidation(**dict(row)) if row else None

    def update_consolidation_status(
        self,
        consolidation_id: str,
        status: str,
        result: str | None = None,
    ) -> None:
        """Mark a consolidation as accepted or rejected, recording the final result."""
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.conn.execute(
            """UPDATE consolidations
               SET status = ?, result = COALESCE(?, result), reviewed_at = ?
               WHERE id = ?""",
            (status, result, now, consolidation_id),
        )
        self.conn.commit()

    def list_consolidations(
        self,
        status: str | None = None,
        limit: int = 20,
    ) -> list[Consolidation]:
        conditions = ["1=1"]
        params: list = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        where = " AND ".join(conditions)
        params.append(limit)
        rows = self.conn.execute(
            f"SELECT * FROM consolidations WHERE {where} ORDER BY created_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [Consolidation(**dict(r)) for r in rows]

    def list_pending_consolidations(self) -> list[Consolidation]:
        """Return all proposals awaiting review."""
        return self.list_consolidations(status="pending")

    def update_memory_readiness_state(self, memory_id: str, state: str) -> None:
        """Advance the readiness state of a memory.

        Valid states: observed | candidate | surfaced | acknowledged | integrated
        """
        self.conn.execute(
            "UPDATE memories SET readiness_state = ? WHERE id = ?",
            (state, memory_id),
        )
        self.conn.commit()
