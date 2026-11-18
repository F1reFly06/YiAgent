"""手工验证 VectorStore 的排序行为, 不调网络。"""

from yiagent.core.chunking import Chunk
from yiagent.core.vector_store import VectorStore

a = Chunk("a", "t.md", "A", 1)
b = Chunk("b", "t.md", "B", 10)
c = Chunk("c", "t.md", "C", 20)

store = VectorStore()
store.add([a, b, c], [[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]])

print("条数:", len(store))
for hit in store.search([1.0, 0.0]):
    print(f"{hit.chunk.heading}  {hit.score:.3f}")
