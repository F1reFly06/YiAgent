""" 端到端 spike: 真笔记 -> 切块 -> 真向量 -> 入库 -> 检索。

只打印, 不断言; 命中质量靠人眼判断。
"""

from pathlib import Path

from yiagent.config import embeddings_settings as settings
from yiagent.core.chunking import split_markdown
from yiagent.core.vector_store import VectorStore
from yiagent.providers.embedding import embed

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "DEVLOG.md"
QUERIES = ["怎么写测试", "红烧肉要小火慢炖两个小时"] # 第二条是噪声基线, 用来定 min_score
TOP_K = 3
PREVIEW_CHARS = 80


def preview(chunk_text: str, heading: str) -> str:
    """剥掉 heading 前缀 + 压成单行, 只留前 80 字。"""
    body = chunk_text.removeprefix(heading).strip()
    return body[:PREVIEW_CHARS].replace("\n", " ")


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")

    chunks = split_markdown(text, source=SOURCE.name)
    vectors = embed([chunk.text for chunk in chunks])

    store = VectorStore()
    store.add(chunks, vectors)

    print(f"文件 {SOURCE.name} | 块数 {len(chunks)} | 向量数 {len(vectors)} | 库内 {len(store)}")
    print(f"模型 {settings.model} | 维度 {settings.dim}\n")

    for query in QUERIES:
        hits = store.search(embed([query])[0], top_k=TOP_K)
        print(f"查询: {query!r}")
        for rank, hit in enumerate(hits, start=1):
            print(f" #{rank} {hit.score: 4f} {hit.chunk.heading} (L{hit.chunk.line_start})")
            print(f"     {preview(hit.chunk.text, hit.chunk.heading)}")
        print()


if __name__ == "__main__":
    main()