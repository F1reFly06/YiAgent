from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Tool:
    """一个可供模型调用的工具。

    name / description / parameters 三样会发给模型看, 
    func 只在本地执行, 模型永远看不到。

    """

    name: str
    description: str
    parameters: dict[str,object]
    func: Callable[...,str]


def _get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _word_count(text: str) -> str:
    return f"共 {len(text)} 个字符"


TIME_TOOL = Tool(
    name="get_current_time",
    description="获取当前的日期和时间。当用户询问现在几点、今天几号、当前日期时调用。",
    parameters={"type": "object", "properties": {}},
    func=_get_current_time,
)

WORD_COUNT_TOOL = Tool(
    name="word_count",
    description="统计一段文本的字符数。当用户要求统计字数或字符数时调用。",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要统计的文本"},
        },
        "required": ["text"],
    },
    func=_word_count,
)

TOOLS: dict[str, Tool] = {t.name: t for t in (TIME_TOOL, WORD_COUNT_TOOL)}


def execute_tool(name: str, arguments: dict[str, object]) -> str:
    """执行指定工具; 任何失败都返回错误说明, 不抛异常。"""

    tool = TOOLS.get(name)
    if tool is None:
        return f"错误: 没有名为 {name} 的工具"
    try:
        return tool.func(**arguments)
    except TypeError as exc:
        return f"错误: {name} 的参数不正确({exc})"
    except Exception as exc:
        return f"错误: {name} 执行失败({exc})"
        