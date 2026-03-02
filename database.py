import json
import sqlite3
from datetime import datetime

import numpy as np

from config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the snapshots table and index if they don't already exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                company_key    TEXT    NOT NULL,
                company_name   TEXT    NOT NULL,
                timestamp      TEXT    NOT NULL,
                messaging_json TEXT    NOT NULL,
                embedding_text TEXT    NOT NULL,
                embedding_blob BLOB    NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_company_timestamp
            ON snapshots (company_key, timestamp)
        """)


def store_snapshot(
    company_key: str,
    company_name: str,
    messaging: dict,
    embedding_text: str,
    embedding: np.ndarray,
    timestamp: str | None = None,
) -> None:
    """Insert a positioning snapshot into the database.

    Args:
        company_key:    Slug key matching the COMPETITORS dict in config.py.
        company_name:   Human-readable company name.
        messaging:      Structured dict from extract_messaging.
        embedding_text: Flattened pipe-separated string that was embedded.
        embedding:      Normalised numpy array from generate_embedding.
        timestamp:      ISO-format datetime string; defaults to now.
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO snapshots
                (company_key, company_name, timestamp, messaging_json, embedding_text, embedding_blob)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                company_key,
                company_name,
                timestamp,
                json.dumps(messaging),
                embedding_text,
                embedding.tobytes(),
            ),
        )


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, deserialising JSON and blob fields."""
    d = dict(row)
    d["messaging"] = json.loads(d.pop("messaging_json"))
    d["embedding"] = np.frombuffer(d.pop("embedding_blob"), dtype=np.float32)
    return d


def get_latest_snapshots() -> list[dict]:
    """Return the most recent snapshot for each company.

    Uses a subquery to find the MAX timestamp per company_key, then joins back
    to retrieve the full row for that snapshot.

    Returns:
        List of dicts, one per company, each containing all snapshot fields plus
        a deserialised 'messaging' dict and 'embedding' numpy array.
    """
    with _connect() as conn:
        rows = conn.execute("""
            SELECT s.*
            FROM snapshots s
            INNER JOIN (
                SELECT company_key, MAX(timestamp) AS max_ts
                FROM snapshots
                GROUP BY company_key
            ) latest
                ON s.company_key = latest.company_key
               AND s.timestamp   = latest.max_ts
            ORDER BY s.company_key
        """).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_historical_snapshots(company_key: str | None = None) -> list[dict]:
    """Return all snapshots ordered by timestamp, optionally filtered by company.

    Args:
        company_key: If provided, return only snapshots for that company.
                     If None, return snapshots for all companies.

    Returns:
        List of dicts ordered by timestamp ascending, each containing all snapshot
        fields plus a deserialised 'messaging' dict and 'embedding' numpy array.
    """
    with _connect() as conn:
        if company_key is None:
            rows = conn.execute(
                "SELECT * FROM snapshots ORDER BY timestamp"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM snapshots WHERE company_key = ? ORDER BY timestamp",
                (company_key,),
            ).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_snapshot_count() -> int:
    """Return the total number of snapshots stored in the database.

    Returns:
        Integer row count.
    """
    with _connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()
    return result[0]
