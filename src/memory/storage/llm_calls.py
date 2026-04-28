"""Storage component for LLM call observability logs."""

from memory.models import _now, _uuid
from memory.storage.base import ConnectionBacked


class LLMCallStore(ConnectionBacked):
    """Writes and reads rows from the llm_calls table."""

    def log_llm_call(
        self,
        *,
        role: str,
        model: str,
        prompt: str,
        response_text: str,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        latency_ms: int | None = None,
        cost_usd: float | None = None,
        conversation_id: str | None = None,
        session_id: str | None = None,
    ) -> str:
        """Insert one LLM call row and return its id."""
        row_id = _uuid()
        self.conn.execute(
            """
            INSERT INTO llm_calls (
                id, role, model, prompt, response,
                prompt_tokens, completion_tokens, latency_ms, cost_usd,
                conversation_id, session_id, called_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row_id,
                role,
                model,
                prompt,
                response_text,
                prompt_tokens,
                completion_tokens,
                latency_ms,
                cost_usd,
                conversation_id,
                session_id,
                _now(),
            ),
        )
        self.conn.commit()
        return row_id

    def get_llm_calls(
        self,
        *,
        conversation_id: str | None = None,
        role: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Return llm_calls rows as dicts, newest first."""
        clauses = []
        params: list = []
        if conversation_id:
            clauses.append("conversation_id = ?")
            params.append(conversation_id)
        if role:
            clauses.append("role = ?")
            params.append(role)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        params.append(limit)

        rows = self.conn.execute(
            f"""
            SELECT id, role, model, prompt, response,
                   prompt_tokens, completion_tokens, latency_ms, cost_usd,
                   conversation_id, session_id, called_at
            FROM llm_calls
            {where}
            ORDER BY called_at DESC
            LIMIT ?
            """,
            params,
        ).fetchall()

        keys = [
            "id", "role", "model", "prompt", "response",
            "prompt_tokens", "completion_tokens", "latency_ms", "cost_usd",
            "conversation_id", "session_id", "called_at",
        ]
        return [dict(zip(keys, row, strict=True)) for row in rows]
