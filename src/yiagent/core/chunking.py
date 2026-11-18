import re
from dataclasses import dataclass

DEFAULT_MAX_CHARS = 800

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_FENCE_RE = re.compile(r"^\s*```")
_ONLY_HASHES_RE = re.compile(r"^#{1,6}$")


@dataclass(frozen=True)
class Chunk:
    """一个可被检索的最小单元"""

    text: str
    source: str
    heading: str
    line_start: int


def _split_long(body: str, max_chars: int) -> list[str]:
    """把超长正文按空行分段后重新打包; 单段仍超长则硬切。"""
    if max_chars <= 0 or len(body) <= max_chars:
        return [body]

    pieces: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in body.split("\n\n"):
        para = para.strip()
        if not para:
            continue

        if len(para) > max_chars:
            if current:
                pieces.append("\n\n".join(current))
                current, current_len = [], 0
            pieces.extend(para[i : i + max_chars] for i in range(0, len(para), max_chars))
            continue

        if current and current_len + len(para) + 2 > max_chars:
            pieces.append("\n\n".join(current))
            current, current_len = [], 0

        current.append(para)
        current_len += len(para) + 2

    if current:
        pieces.append("\n\n".join(current))
    return pieces



def split_markdown(text: str, source: str, max_chars: int = DEFAULT_MAX_CHARS) -> list[Chunk]:
    """按 Markdown 标题层级把文本切成 Chunk

    - 代码块 ``` 内的 # 不算标题
    - 孤立的一行 #/##/### (后面没有文字) 直接跳过
    - 单块超过 max_chars 时段落重新打包, 仍超长则硬切
    - 已知限制: 代码块未闭合时, 后面所有标题都会被当成正文
    """
    chunks: list[Chunk] = []
    stack: list[tuple[int, str]] = []  # (级别, 标题), 栈顶是当前最深一级
    buffer: list[str] = []  # 当前块的正文行
    heading_line = 1  # 当前块标题所在行号
    in_fence = False  # 是否在 ``` 代码块中

    def flush() -> None:
        """把 buffer 里的正文落成一个Chunk; 空白块直接丢弃"""
        body = "\n".join(buffer).strip()
        if not body:
            return
        heading = " > ".join(title for _, title in stack)
        prefix_len = len(heading) + 1 if heading else 0
        for piece in _split_long(body, max_chars - prefix_len):
            chunks.append(
                Chunk(
                    text=f"{heading}\n{piece}" if heading else piece,
                    source=source,
                    heading=heading,
                    line_start=heading_line, # 切出的多块共享标题行号
                )
            )

    for lineno, line in enumerate(text.splitlines(), start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            buffer.append(line)
            continue

        if not in_fence and _ONLY_HASHES_RE.match(line.strip()):
            continue

        match = None if in_fence else _HEADING_RE.match(line)
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
