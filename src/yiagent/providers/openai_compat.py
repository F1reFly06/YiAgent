import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import cast, override

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from yiagent.config import chat_settings
from yiagent.core.llm import Done, LLMProvider, StreamEvent, TextDelta, ToolCall
from yiagent.core.message import Message
from yiagent.core.tools import TOOLS, Tool


def _to_openai_tools(tools: dict[str, Tool]) -> list[ChatCompletionToolParam]:
    """把内部 Tool 注册表翻译成 OpenAI 协议的 tools 参数。"""
    return cast(
        list[ChatCompletionToolParam],
        [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools.values()
        ],
    )


@dataclass
class _ToolCallDraft:
    """流式积累中的工具调用草稿。事件是 frozen 的事实, 草稿是施工中的可变状态"""

    id: str = ""
    name: str = ""
    arguments: str = ""


def _parse_arguments(raw: str) -> dict[str, object]:
    """把积累好的参数 JSON 解析成 dict; 解析不了就给空 dict。"""
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return cast(dict[str, object], parsed)


class OpenAIChatProvider(LLMProvider):
    def __init__(self) -> None:
        self.client: OpenAI = OpenAI(
            api_key=chat_settings.api_key.get_secret_value(),
            base_url=chat_settings.base_url,
        )
        self.model: str = chat_settings.model
        self.tools: list[ChatCompletionToolParam] = _to_openai_tools(TOOLS)

    @override
    def stream(self, messages: list[Message]) -> Iterator[StreamEvent]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], [m.to_dict() for m in messages]),
            tools=self.tools,
            stream=True,
        )
        finish_reason = "stop"
        drafts: dict[int, _ToolCallDraft] = {}
        for chunk in response:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            if choice.delta.content:
                yield TextDelta(text=choice.delta.content)
            for tc in choice.delta.tool_calls or []:
                draft = drafts.setdefault(tc.index, _ToolCallDraft())
                if tc.id:
                    draft.id = tc.id
                if tc.function:
                    if tc.function.name:
                        draft.name = tc.function.name
                    if tc.function.arguments:
                        draft.arguments += tc.function.arguments
            if choice.finish_reason:
                finish_reason = choice.finish_reason
        for index in sorted(drafts):
            draft = drafts[index]
            yield ToolCall(
                id=draft.id, name=draft.name, arguments=_parse_arguments(draft.arguments)
            )
        yield Done(finish_reason=finish_reason)
