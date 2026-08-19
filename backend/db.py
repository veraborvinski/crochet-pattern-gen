import sqlite3
import json
import os
import hashlib
from pathlib import Path
from data.schema import Pattern

_DB_PATH = os.environ.get("SQLITE_PATH", str(Path(__file__).parent.parent / "patterns.db"))

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            json TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts
        USING fts5(id UNINDEXED, searchtext, tokenize='porter ascii')
    """)
    return conn

def store_pattern(pattern: Pattern) -> str:
    pid = pattern.id or hashlib.md5(
        (pattern.title + (pattern.source_url or "")).encode()
    ).hexdigest()[:12]
    pattern = pattern.model_copy(update={"id": pid})
    searchtext = f"{pattern.title} {pattern.description} {' '.join(pattern.tags)}"
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO patterns VALUES (?, ?)",
            (pid, pattern.model_dump_json()),
        )
        conn.execute("DELETE FROM patterns_fts WHERE id = ?", (pid,))
        conn.execute(
            "INSERT INTO patterns_fts (id, searchtext) VALUES (?, ?)",
            (pid, searchtext),
        )
    return pid

def search_patterns(query: str, k: int = 5) -> list[Pattern]:
    # Escape FTS5 special characters
    safe_query = query.replace('"', '""')
    with _conn() as conn:
        try:
            rows = conn.execute(
                """
                SELECT p.json FROM patterns p
                JOIN patterns_fts f ON f.id = p.id
                WHERE patterns_fts MATCH ?
                ORDER BY rank LIMIT ?
                """,
                (safe_query, k),
            ).fetchall()
        except sqlite3.OperationalError:
            # Fallback: LIKE search if FTS query is malformed
            rows = conn.execute(
                "SELECT json FROM patterns WHERE json LIKE ? LIMIT ?",
                (f"%{query}%", k),
            ).fetchall()
    return [Pattern.model_validate_json(r[0]) for r in rows]

def get_pattern_by_id(pattern_id: str) -> Pattern | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT json FROM patterns WHERE id = ?", (pattern_id,)
        ).fetchone()
    return Pattern.model_validate_json(row[0]) if row else None
