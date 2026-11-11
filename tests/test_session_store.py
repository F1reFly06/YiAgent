import sqlite3
from pathlib import Path

import pytest

from yiagent.core.message import Message, Role
from yiagent.core.session_store import (
    append_message,
    create_session,
    init_db,
    latest_session,
    load_session,
)

TOOL_CALLS: list[dict[str, object]] = [
    {
        "id": "call_abc",
        "type": "function",
        "function": {"name": "get_weather", "arguments": '{"city":"上海"}'},
    }
]


@pytest.fixture
def db(tmp_path: Path) -> str:
    """每个测试一个独立临时库, 绝不碰 data/yiagent.db"""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


def _seqs(db_path: str, session_id: int) -> list[int]:
    """直接查库看 seq, 绕开 load_session 的排序, 避免自证。"""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT seq FROM messages WHERE session_id = ? ORDER BY seq", (session_id,)
        ).fetchall()
    finally:
        conn.close()
    return [row[0] for row in rows]


def test_save_and_load_roundtrip(db: str) -> None:
    session_id = create_session(db, title="测试会话")
    append_message(db, session_id, Message(Role.USER, "今天天气怎么样"))
    append_message(db, session_id, Message(Role.ASSISTANT, None, tool_calls=TOOL_CALLS))
    append_message(db, session_id, Message(Role.TOOL, '{"temp": 21}', tool_call_id="call_abc"))

    history = load_session(db, session_id)

    assert [m.role for m in history] == [Role.USER, Role.ASSISTANT, Role.TOOL]
    assert history[0].content == "今天天气怎么样"

    assistant_msg = history[1]
    assert assistant_msg.content is None
    assert isinstance(assistant_msg.tool_calls, list)
    assert assistant_msg.tool_calls == TOOL_CALLS

    tool_msg = history[2]
    assert tool_msg.tool_call_id == "call_abc"
    assert tool_msg.tool_calls is None


def test_latest_session_none_then_latest(db: str) -> None:
    assert latest_session(db) is None

    first = create_session(db, title="第一个")
    assert latest_session(db) == first

    second = create_session(db, title="第二个")
    assert latest_session(db) == second


def test_empty_session_returns_empty_list(db: str) -> None:
    session_id = create_session(db)
    assert load_session(db, session_id) == []


def test_append_message_seq_autoincrement(db: str) -> None:
    session_id = create_session(db)
    for i in range(3):
        append_message(db, session_id, Message(Role.USER, f"第{i}条"))

    assert _seqs(db, session_id) == [1, 2, 3]


def test_seq_is_per_session(db: str) -> None:
    first = create_session(db)
    second = create_session(db)
    append_message(db, first, Message(Role.USER, "a"))
    append_message(db, first, Message(Role.USER, "b"))
    append_message(db, second, Message(Role.USER, "c"))

    assert _seqs(db, first) == [1, 2]
    assert _seqs(db, second) == [1]


def test_foreign_key_enforced(db: str) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        append_message(db, 999, Message(Role.USER, "孤儿信息"))
