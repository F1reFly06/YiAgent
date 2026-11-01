from collections.abc import Iterator
from typing import cast, override

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from yiagent.config import chat_settings
from yiagent.core.llm import Done, LLMProvider, StreamEvent, TextDelta
from yiagent.core.message import Message


class OpenAIChatProvider(LLMProvider):
    def __init__(self) -> None:
        self.client: OpenAI = OpenAI(
            api_key=chat_settings.api_key.get_secret_value(),
            base_url=chat_settings.base_url,
        )
        self.model: str = chat_settings.model

    @override
    def stream(self, messages: list[Message]) -> Iterator[StreamEvent]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=cast(list[ChatCompletionMessageParam], [m.to_dict() for m in messages]),
            stream=True,
        )
        finish_reason = "stop"
        for chunk in response:
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            content = choice.delta.content
            if content:
                yield TextDelta(text=content)
            if choice.finish_reason:
                finish_reason = choice.finish_reason
        yield Done(finish_reason=finish_reason)
