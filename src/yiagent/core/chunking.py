import re
from dataclasses import dataclass

DEFAULT_MAX_CHARS = 800

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


@dataclass(frozen=True)
class Chunk:
    """一个可被检索的最小单元"""

    text: str
    source: str
    heading: str
    line_start: int


def split_markdown(text: str, source: str, max_char: int = DEFAULT_MAX_CHARS) -> list[Chunk]:
    """按 Markdown 标题层级把文本切成 Chunk

    v1 只按标题切:
    - max_chars 暂时没用, 留给 B1 处理超长块
    - TODO(B1): 代码块 ``` 内的 # 不算标题
    """
    chunks: list[Chunk] = []
    stack: list[tuple[int, str]] = []  # (级别, 标题), 栈顶是当前最深一级
    buffer: list[str] = []  # 当前块的正文行
    heading_line = 1  # 当前块标题所在行号

    def flush() -> None:
        """把 buffer 里的正文落成一个Chunk; 空白块直接丢弃"""
        body = "\n".join(buffer).strip()
        if not body:
            return
        heading = " > ".join(title for _, title in stack)
        chunks.append(
            Chunk(
                text=f"{heading}\n{body}" if heading else body,
                source=source,
                heading=heading,
                line_start=heading_line,
            )
        )

    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _HEADING_RE.match(line)
        if match is None:
            buffer.append(line)
            continue

        flush()
        buffer.clear()

        level = len(match.group(1))
        title = match.group(2).strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        heading_line = lineno

    flush()
    return chunks
