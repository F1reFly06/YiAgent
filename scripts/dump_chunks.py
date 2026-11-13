"""打印某个 Markdown 文件的切块结果, 用来肉眼检查切块质量。"""

import sys 
from pathlib import Path

from yiagent.core.chunking import split_markdown


def main() -> None:
    target = Path(sys.argv[1])
    chunks = split_markdown(target.read_text(encoding="utf-8"), str(target))

    print(f"{target} -> {len(chunks)} 块\n")
    for chunk in chunks:
        print(f"[{chunk.line_start:>4}] {chunk.heading or '(无标题)'}")
        print(f"        {chunk.text[:50]!r}")


if __name__ == "__main__":
    main()