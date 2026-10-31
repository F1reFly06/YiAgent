import typer
from openai import AuthenticationError
from rich.console import Console

from yiagent.core.llm import LLMProvider
from yiagent.core.message import Message, Role
from yiagent.core.prompt import load_system_prompt
from yiagent.providers.openai_compat import OpenAIChatProvider

app = typer.Typer()
console = Console()


def _stream_reply(provider: LLMProvider, messages: list[Message]) -> str:
    """把messages发给模型, 逐块打印, 返回完整回答。不修改messages。"""
    collected = ""
    for piece in provider.stream(messages):
        console.print(piece, end="", markup=False)
        collected += piece
    console.print()
    return collected


def _chat_loop(provider: LLMProvider, messages: list[Message]) -> None:
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

        messages.append(Message(Role.USER, text))
        try:
            collected = _stream_reply(provider, messages)
        except AuthenticationError:
            console.print("鉴权失败, 请检查 .env 里的 CHAT_API_KEY")
            break
        except Exception as exc:
            console.print(f"请求失败: {exc}")
            messages.pop()
            continue

        messages.append(Message(Role.ASSISTANT, collected))


@app.command()
def main() -> None:
    console.print("YiAgent 启动！")
    provider: LLMProvider = OpenAIChatProvider()
    messages = [
        Message(Role.SYSTEM, load_system_prompt()),
    ]
    _chat_loop(provider, messages)


if __name__ == "__main__":
    app()
