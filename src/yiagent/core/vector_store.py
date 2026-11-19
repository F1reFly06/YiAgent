from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from yiagent.core.chunking import Chunk


@dataclass(frozen=True)
class SearchHit:
    """一次命中的结果: 哪个块 + 多相似。"""

    chunk: Chunk
    score: float


class VectorStore:
    """内存版向量库: 散向量进矩阵, 检索时一次矩阵乘法算完全部分数。"""

    def __init__(self) -> None:
        self._matrix: NDArray[np.float32] = np.zeros((0, 0), dtype=np.float32)
        self._chunks: list[Chunk] = []
        self._dim: int = 0

    def __len__(self) -> int:
        return len(self._chunks)

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(f"chunks 与 vectors 数量不一致: {len(chunks)} != {len(vectors)}")
        if not chunks:
            return

        matrix: NDArray[np.float32] = np.asarray(vectors, dtype=np.float32)
        if matrix.ndim != 2:
            raise ValueError(f"vectors 必须是二维, 实际形状 {matrix.shape}")

        dim = matrix.shape[1]
        if self._dim == 0:
            self._dim = dim
        elif dim != self._dim:
            raise ValueError(f"向量维度不一致: 已有 {self._dim}, 本次 {dim}")

        self._matrix = matrix if not self._chunks else np.vstack([self._matrix, matrix])
        self._chunks.extend(chunks)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[SearchHit]:
        if not self._chunks or top_k <= 0:
            return []

        query = np.asarray(query_vector, dtype=np.float32)
        if query.shape != (self._dim,):
            raise ValueError(f"查询向量维度不对: 期望 ({self._dim},), 实际 {query.shape}")

        scores = self._matrix @ query
        order = np.argsort(scores)[::-1][:top_k]
        return [
            SearchHit(chunk=self._chunks[int(index)], score=float(scores[int(index)]))
            for index in order
        ]
