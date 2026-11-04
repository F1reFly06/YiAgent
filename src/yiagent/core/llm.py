from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from yiagent.core.message import Message


@dataclass(frozen=True)
class TextDelta:
    """模型生成的一小段文字(通常1个字)。"""

    text: str


@dataclass(frozen=True)
class ToolCall:
    """模型请求执行一次工具调用, 参数已解析成dict。"""

    id: str
    name: str
    arguments: dict[str, object]


@dataclass(frozen=True)
class Done:
    """一轮响应结束。finish_reason 说明为什么结束: stop/tool_calls/length ..."""

    finish_reason: str


StreamEvent = TextDelta | ToolCall | Done


class LLMProvider(Protocol):
    """模型提供方的统一接口：任何接入的模型都要满足这个形状。"""

    def stream(self, messages: list[Message]) -> Iterator[StreamEvent]:
        """接收信息列表，逐段产出模型生成文字。"""
        ...
