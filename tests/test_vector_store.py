import pytest

from yiagent.core.chunking import Chunk
from yiagent.core.vector_store import VectorStore

CHUNK_A = Chunk("A 的内容", "t.md", "A", 1)
CHUNK_B = Chunk("B 的内容", "t.md", "B", 10)
CHUNK_C = Chunk("C 的内容", "t.md", "C", 10)

VEC_A = [1.0, 0.0]
VEC_B = [0.0, 1.0]
VEC_C = [0.7, 0.7]


def _store() -> VectorStore:
    """A/B/C + 三条二维向量, 顺序与 CHUNK_* 对齐。"""
    store = VectorStore()
    store.add([CHUNK_A, CHUNK_B, CHUNK_C], [VEC_A, VEC_B, VEC_C])
    return store


def test_search_returns_nearest_first() -> None:
    hits = _store().search([1.0, 0.0])

    assert [hit.chunk.heading for hit in hits] == ["A", "C", "B"]

    # 手算点积: A=1.0, C=0.7, B=0.0; float32 需要 approx 比较
    assert hits[0].score == pytest.approx(1.0)
    assert hits[1].score == pytest.approx(0.7)
    assert hits[2].score == pytest.approx(0.0)

    scores = [hit.score for hit in hits]
    assert scores == sorted(scores, reverse=True)


def test_add_length_mismath_raise() -> None:
    store = VectorStore()

    with pytest.raises(ValueError, match="数量不一致"):
        store.add([CHUNK_A, CHUNK_B], [VEC_A])

    assert len(store) == 0


def test_add_dim_mismatch_raises() -> None:
    store = VectorStore()
    store.add([CHUNK_A], [VEC_A])

    with pytest.raises(ValueError, match="维度不一致"):
        store.add([CHUNK_B], [[1.0, 0.0, 0.0]])

    # 校验必须在 vstack 之前: 抛错后库不能被污染
    assert len(store) == 1
    assert store.search([1.0, 0.0])[0].chunk.heading == "A"


def test_search_on_empty_returns_empty() -> None:
    store = VectorStore()

    assert store.search([1.0, 0.0]) == []


def test_top_k_larger_than_size() -> None:
    hits = _store().search([1.0, 0.0], top_k=5)

    assert len(hits) == 3
    assert [hit.chunk.heading for hit in hits] == ["A", "C", "B"]
