"""Tests for ExtensionAPI: DB enforcement, registries, embeddings, LLM, transactions."""

from __future__ import annotations

import numpy as np
import pytest

from memory.extensions import (
    ContextRequest,
    ExtensionAPI,
    ExtensionPermissionError,
)


def _api(db_conn, **kwargs) -> ExtensionAPI:
    return ExtensionAPI(
        extension_id=kwargs.pop("extension_id", "hello"),
        connection=db_conn,
        **kwargs,
    )


def _seed_ext_table(db_conn, name: str = "ext_hello_pings") -> None:
    db_conn.execute(f"CREATE TABLE {name} (id INTEGER PRIMARY KEY, msg TEXT)")
    db_conn.commit()


# --- Identity / prefix ----------------------------------------------------


def test_api_exposes_extension_id_and_prefix(db_conn):
    api = _api(db_conn)
    assert api.extension_id == "hello"
    assert api.table_prefix == "ext_hello_"


def test_api_prefix_translates_dashes_to_underscores(db_conn):
    api = _api(db_conn, extension_id="review-copy")
    assert api.table_prefix == "ext_review_copy_"


# --- execute / read / executemany -----------------------------------------


def test_execute_allows_write_to_own_table(db_conn):
    _seed_ext_table(db_conn)
    api = _api(db_conn)
    api.execute(
        "INSERT INTO ext_hello_pings (msg) VALUES (?)",
        ("first",),
    )
    rows = db_conn.execute("SELECT msg FROM ext_hello_pings").fetchall()
    assert [row["msg"] for row in rows] == ["first"]


def test_execute_rejects_write_to_core_table(db_conn):
    api = _api(db_conn)
    with pytest.raises(ExtensionPermissionError) as excinfo:
        api.execute(
            "INSERT INTO memories (id, memory_type, layer, title, content, created_at) "
            "VALUES ('x', 'insight', 'ego', 't', 'c', '2026-05-11')"
        )
    assert "memories" in str(excinfo.value)


def test_execute_rejects_write_to_other_extension_table(db_conn):
    api = _api(db_conn)
    with pytest.raises(ExtensionPermissionError):
        api.execute("INSERT INTO ext_finances_accounts (id) VALUES (1)")


def test_execute_allows_read_anywhere(db_conn):
    api = _api(db_conn)
    # read of a core table should be fine even without seeding
    api.execute("SELECT count(*) FROM memories")


def test_read_allows_query_against_core_table(db_conn):
    api = _api(db_conn)
    cursor = api.read("SELECT count(*) AS c FROM memories")
    assert cursor.fetchone()["c"] == 0


def test_read_rejects_write(db_conn):
    _seed_ext_table(db_conn)
    api = _api(db_conn)
    with pytest.raises(ExtensionPermissionError):
        api.read("INSERT INTO ext_hello_pings (msg) VALUES ('x')")


def test_executemany_allows_bulk_write_to_own_table(db_conn):
    _seed_ext_table(db_conn)
    api = _api(db_conn)
    api.executemany(
        "INSERT INTO ext_hello_pings (msg) VALUES (?)",
        [("a",), ("b",), ("c",)],
    )
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM ext_hello_pings").fetchone()
    assert rows["c"] == 3


def test_executemany_rejects_write_to_core_table(db_conn):
    api = _api(db_conn)
    with pytest.raises(ExtensionPermissionError):
        api.executemany(
            "INSERT INTO memories (id, memory_type, layer, title, content, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [("x", "i", "ego", "t", "c", "2026-05-11")],
        )


# --- transaction ----------------------------------------------------------


def test_transaction_commits_on_success(db_conn):
    _seed_ext_table(db_conn)
    api = _api(db_conn)
    with api.transaction():
        api.execute("INSERT INTO ext_hello_pings (msg) VALUES ('one')")
        api.execute("INSERT INTO ext_hello_pings (msg) VALUES ('two')")
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM ext_hello_pings").fetchone()
    assert rows["c"] == 2


def test_transaction_rolls_back_on_exception(db_conn):
    _seed_ext_table(db_conn)
    api = _api(db_conn)
    with pytest.raises(RuntimeError):
        with api.transaction():
            api.execute("INSERT INTO ext_hello_pings (msg) VALUES ('one')")
            raise RuntimeError("boom")
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM ext_hello_pings").fetchone()
    assert rows["c"] == 0


# --- Registries -----------------------------------------------------------


def test_register_cli_adds_handler(db_conn):
    api = _api(db_conn)

    def handler(api, args):
        return 0

    api.register_cli("ping", handler)
    assert api.cli_registry["ping"] is handler


def test_register_cli_rejects_invalid_args(db_conn):
    api = _api(db_conn)
    with pytest.raises(ValueError):
        api.register_cli("", lambda a, b: 0)
    with pytest.raises(ValueError):
        api.register_cli("ping", "not-callable")  # type: ignore[arg-type]


def test_register_mirror_context_adds_provider(db_conn):
    api = _api(db_conn)

    def provider(api, ctx):
        return "hello"

    api.register_mirror_context("greeting", provider)
    assert api.context_registry["greeting"] is provider


def test_register_mirror_context_rejects_invalid_args(db_conn):
    api = _api(db_conn)
    with pytest.raises(ValueError):
        api.register_mirror_context("", lambda a, b: None)
    with pytest.raises(ValueError):
        api.register_mirror_context("cap", "not-callable")  # type: ignore[arg-type]


# --- Embeddings -----------------------------------------------------------


def test_embed_uses_injected_fn(db_conn):
    vec = np.ones(1536, dtype=np.float32) / np.sqrt(1536)
    api = _api(db_conn, embed_fn=lambda text: vec)
    blob = api.embed("any text")
    assert isinstance(blob, (bytes, bytearray))
    assert len(blob) == 1536 * 4  # 1536 float32 values


# --- LLM ------------------------------------------------------------------


def test_llm_uses_injected_fn(db_conn):
    received = {}

    def fake_llm(prompt, **kwargs):
        received["prompt"] = prompt
        received["kwargs"] = kwargs
        return "echo: " + prompt

    api = _api(db_conn, llm_fn=fake_llm)
    out = api.llm("say hi", system="be terse")
    assert out == "echo: say hi"
    assert received["prompt"] == "say hi"
    assert received["kwargs"]["system"] == "be terse"


# --- ContextRequest -------------------------------------------------------


def test_context_request_is_frozen_dataclass():
    ctx = ContextRequest(
        persona_id="tesoureira",
        journey_id="eudaimon",
        user="alisson-vale",
        query="how is runway?",
        binding_kind="persona",
        binding_target="tesoureira",
    )
    assert ctx.persona_id == "tesoureira"
    # Frozen dataclass: any attribute assignment raises FrozenInstanceError
    # (a subclass of AttributeError).
    import dataclasses

    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.persona_id = "other"  # type: ignore[misc]
