from collections.abc import Iterator
from typing import Protocol


from yiagent.core.message import Message


class LLMProvider(Protocol):
    """模型提供方的统一接口：任何接入的模型都要满足这个形状。"""

    def stream(self,message: list[Message]) -> Iterator[str]:
        """接收信息列表，逐段产出模型生成文字。"""
        ...