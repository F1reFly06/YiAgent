import json
import sqlite3
from dataclasses import dataclass, field

import typer
from openai import AuthenticationError
from rich.console import Console

from yiagent.core import session_store
from yiagent.core.llm import Done, LLMProvider, TextDelta, ToolCall
from yiagent.core.message import Message, Role
from yiagent.core.prompt import load_system_prompt
from yiagent.core.tools import execute_tool
from yiagent.providers.openai_compat import OpenAIChatProvider

app = typer.Typer()
console = Console()
MAX_TOOL_ROUNDS = 5
DB = "data/yiagent.db"


@dataclass
class _ReplyResult:
    """一次请求的产出: 文本 / 工具调用 / 结束原因。"""

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"


def _stream_reply(provider: LLMProvider, messages: list[Message]) -> _ReplyResult:
    """向模型发起一次请求, 边收边打印文字, 返回本次请求的汇总结果。不修改 messages。"""

    result = _ReplyResult()
    started = False
    for event in provider.stream(messages):
        if isinstance(event, TextDelta):
            if not started:
                console.print("Yi: ", end="", style="bold cyan")
                started = True
            console.print(event.text, end="", markup=False)
            result.text += event.text
        elif isinstance(event, ToolCall):
            result.tool_calls.append(event)
        elif isinstance(event, Done):
            result.finish_reason = event.finish_reason
    if result.text:
        console.print()
    return result


def _tool_call_to_dict(tc: ToolCall) -> dict[str, object]:
    """把内部 ToolCall 转回协议形状, 写回历史时用。"""
    return {
        "id": tc.id,
        "type": "function",
        "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
    }


def _save_new_messages(new_messages: list[Message], session_id: int) -> None:
    """把本轮新增的消息写入 SQLite。写失败只警告, 不打断已经完成的对话"""
    for message in new_messages:
        try:
            session_store.append_message(DB, session_id, message)
        except sqlite3.Error as exc:
            console.print(f"[写入历史失败] {exc}", style="yellow", markup=False)
            return


def _run_turn(provider: LLMProvider, messages: list[Message], session_id: int, start: int) -> str:
    """完成一轮提问: 需要时执行工具并再请求, 返回最终回答。异常时回滚本轮追加的消息。"""
    last_text = ""
    try:
        for _ in range(MAX_TOOL_ROUNDS):
            result = _stream_reply(provider, messages)
            last_text = result.text
            messages.append(
                Message(
                    Role.ASSISTANT,
                    result.text or None,
                    tool_calls=[_tool_call_to_dict(tc) for tc in result.tool_calls] or None,
                )
            )

            if result.finish_reason != "tool_calls" or not result.tool_calls:
                return result.text

            for tc in result.tool_calls:
                output = execute_tool(tc.name, tc.arguments)
                console.print(f"[调用 {tc.name}] {output}", style="dim", markup=False)
                messages.append(Message(Role.TOOL, output, tool_call_id=tc.id))

        console.print(f"已连续调用工具 {MAX_TOOL_ROUNDS} 轮, 停止本轮", style="yellow")
        return last_text
    except Exception:
        del messages[start:]
        raise
    finally:
        _save_new_messages(messages[start:], session_id)


def _chat_loop(provider: LLMProvider, messages: list[Message], session_id: int) -> None:
    while True:
        try:
            text = console.input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print()
            break

        if not text:
            continue
        if text in {"/exit", "/quit"}:
            break
        if text == "/clear":
            del messages[1:]
            console.print("已清空历史")
            continue

        start = len(messages)
        messages.append(Message(Role.USER, text))
        try:
            _run_turn(provider, messages, session_id, start)
        except AuthenticationError:
            console.print("鉴权失败, 请检查 .env 里的 CHAT_API_KEY")
            break
        except Exception as exc:
            console.print(f"请求失败: {exc}")
            continue


@app.command()
def main() -> None:
    console.print("YiAgent 启动！")
    session_store.init_db(DB)

    session_id = session_store.latest_session(DB)
    if session_id is None:
        session_id = session_store.create_session(DB)
        console.print(f"已新建对话 {session_id}", style="dim")
    else:
        console.print(f"继续会话 {session_id}", style="dim")

    history = session_store.load_session(DB, session_id)
    if history:
        console.print(f"已载入 {len(history)} 条历史消息", style="dim")
    provider: LLMProvider = OpenAIChatProvider()
    messages = [Message(Role.SYSTEM, load_system_prompt()), *history]
    _chat_loop(provider, messages, session_id)


if __name__ == "__main__":
    app()
