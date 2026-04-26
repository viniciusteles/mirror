"""Shared typing for storage components."""

import sqlite3


class ConnectionBacked:
    conn: sqlite3.Connection
