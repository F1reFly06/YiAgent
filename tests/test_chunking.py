from yiagent.core.chunking import DEFAULT_MAX_CHARS, split_markdown

FENCE_MD = """# 标题
正文

```python
# 注释一
print(1)
# 注释二
```

结尾
"""


def test_chunks_are_never_empty() -> None:
    text = "# A\n正文一\n\n## B\n\n### C\n正文三\n"
    chunks = split_markdown(text, "t.md")

    assert chunks
    assert all(chunk.text.strip() for chunk in chunks)


def test_heading_path_has_no_duplicate_levels() -> None:
    text = "# A\n一\n\n## B\n二\n\n## C\n三\n\n# D\n四\n"
    chunks = split_markdown(text, "t.md")

    for chunk in chunks:
        parts = chunk.heading.split(" > ")
        assert len(parts) == len(set(parts)), f"同级标题被叠进了路径: {chunk.heading}"


def test_code_fence_hash_is_not_a_heading() -> None:
    chunks = split_markdown(FENCE_MD, "t.md")

    assert len(chunks) == 1
    assert chunks[0].heading == "标题"
    assert "# 注释一" in chunks[0].text
    assert "结尾" in chunks[0].text


def test_isolated_hashes_line_is_dropped() -> None:
    text = "## Day4\n###\n- 今天没做什么\n"
    chunks = split_markdown(text, "t.md")

    assert len(chunks) == 1
    assert chunks[0].heading == "Day4"
    assert "###" not in chunks[0].text
    assert chunks[0].text.endswith("- 今天没做什么")


def test_long_block_with_heading_is_split() -> None:
    chunks = split_markdown(f"# 标题\n{'字' * 3000}", "t.md")

    assert len(chunks) > 1
    assert all(len(chunk.text) <= DEFAULT_MAX_CHARS for chunk in chunks)


def test_long_block_without_heading_is_split() -> None:
    """无标题正文也必须是切完的: 这条专门守 flush() 的 else 分支。"""
    chunks = split_markdown("字" * 3000, "t.md")

    assert len(chunks) > 1
    assert all(len(chunk.text) <= DEFAULT_MAX_CHARS for chunk in chunks)