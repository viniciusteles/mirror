from concurrent.futures import ThreadPoolExecutor

from memory import MemoryClient
from memory.cli.conversation_logger import get_or_create_conversation


def test_concurrent_session_creation_preserves_all_bindings(tmp_path):
    mirror_home = tmp_path / ".mirror" / "testuser"
    mirror_home.mkdir(parents=True)

    # Warm the database once so the concurrency test exercises session creation,
    # not first-time directory setup noise.
    MemoryClient(db_path=mirror_home / "memory.db").close()

    session_ids = [f"sess-{i}" for i in range(20)]

    def create(session_id: str) -> str:
        return get_or_create_conversation(session_id, mirror_home=mirror_home)

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(create, session_ids))

    assert len(results) == 20
    assert len(set(results)) == 20

    with MemoryClient(db_path=mirror_home / "memory.db") as client:
        stored = [client.store.get_runtime_session(session_id) for session_id in session_ids]
        assert all(session is not None for session in stored)
        assert {session.conversation_id for session in stored if session is not None} == set(
            results
        )


def test_concurrent_memory_client_open_on_fresh_db_is_safe(tmp_path):
    # Use a high worker count and repeat across several fresh databases so the
    # race window in bootstrap is hit reliably, not flakily. Historically this
    # test passed ~80% of the time at 12 workers, which is not acceptable for a
    # concurrency regression test.
    worker_count = 32
    iterations = 5

    for iteration in range(iterations):
        db_path = tmp_path / f"memory-{iteration}.db"

        def open_client(_: int, path=db_path) -> str:
            # Close each client explicitly: sqlite3.Connection does not release
            # its file descriptors on refcount-based cleanup (Python 3.14),
            # so leaving clients to GC will exhaust RLIMIT_NOFILE under stress.
            with MemoryClient(db_path=path) as client:
                return str(client.db_path)

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            results = list(executor.map(open_client, range(worker_count)))

        assert len(results) == worker_count
        assert db_path.exists()

        with MemoryClient(db_path=db_path) as client:
            row = client.conn.execute("SELECT COUNT(*) FROM _migrations").fetchone()
            assert row[0] >= 0
            # Sanity: modern schema is in place and usable.
            client.conn.execute("SELECT journey FROM memories WHERE 1 = 0").fetchall()
            client.conn.execute("SELECT session_id FROM runtime_sessions WHERE 1 = 0").fetchall()
