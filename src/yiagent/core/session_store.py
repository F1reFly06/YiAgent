import sqlite3
from datetime import UTC, datetime
from pathlib import Path


_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT    NOT NULL,
    title      TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    seq          INTEGER NOT NULL,
    role         TEXT    NOT NULL,
    content      TEXT,
    tool_calls   TEXT,
    tool_call_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session_seq ON messages(session_id,seq);
"""



def _connect(db_path: str) -> sqlite3.Connection:
    """打开连接, 并统一做好每次连接都必须做的设置。"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """建表(幂等): 不存在则创建, 已存在则什么都不做。"""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(db_path)
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def create_session(db_path: str, title: str | None = None) -> int:
    """新建一个会话, 返回新会话的id。"""
    conn = _connect(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO sessions (created_at, title) VALUES (?, ?)",
            (datetime.now(UTC).isoformat(timespec="seconds"), title),
        )
        conn.commit()
        return int(cur.lastrowid or 0)
    finally:
        conn.close()