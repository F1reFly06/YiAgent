"""打印某个 Markdown 文件的切块结果, 用来肉眼检查切块质量。"""

import sys
from pathlib import Path

from yiagent.core.chunking import DEFAULT_MAX_CHARS, split_markdown


def main() -> None:
    target = Path(sys.argv[1])
    chunks = split_markdown(target.read_text(encoding="utf-8"), str(target))

    print(f"{target} -> {len(chunks)} 块\n")
    for chunk in chunks:
        body = chunk.text[len(chunk.heading) :].lstrip("\n") if chunk.heading else chunk.text
        print(f"[{chunk.line_start:>4}] {len(chunk.text):>5}字 {chunk.heading or '(无标题)'}")
        print(f"        {body[:70]!r}")

    lengths = [len(c.text) for c in chunks]
    print(
        f"\n平均 {sum(lengths) // len(lengths)} 字, 最长 {max(lengths)} 字, "
        f"超 {DEFAULT_MAX_CHARS} 的 {sum(1 for n in lengths if n > DEFAULT_MAX_CHARS)} 块"
    )


if __name__ == "__main__":
    main()
