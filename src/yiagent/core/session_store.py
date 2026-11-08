import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from yiagent.core.message import Message, Role

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


def append_message(db_path: str, session_id: int, message: Message) -> None:
    """把一条消息追加到会话末尾, seq自动递增。"""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) AS last_seq FROM messages WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        last_seq = int(row["last_seq"]) if row is not None else 0

        _ = conn.execute(
            "INSERT INTO messages(session_id, seq, role, content, tool_calls ,tool_call_id)"
            + "VALUES (?, ?, ?, ?, ?, ?)",
            (
                session_id,
                last_seq + 1,
                str(message.role),
                message.content,
                json.dumps(message.tool_calls, ensure_ascii=False) if message.tool_calls else None,
                message.tool_call_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_session(db_path: str, session_id: int) -> list[Message]:
    """按照seq的顺序读出会话的全部消息。"""
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT role, content, tool_calls, tool_call_id FROM messages"
            + " WHERE session_id = ? ORDER BY seq", 
            (session_id,),
        ).fetchall()
        return[
            Message(
                role=Role(row["role"]),
                content=row["content"],
                tool_calls=json.loads(row["tool_calls"]) if row["tool_calls"] else None,
                tool_call_id=row["tool_call_id"],
            )
            for row in rows
        ]
    finally:
        conn.close()
