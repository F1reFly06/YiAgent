from openai import OpenAI

from yiagent.config import embeddings_settings as settings

BATCH_SIZE = 32

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """惰性建 client: 整个进程只建一次, import 本模块不产生任何副作用"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.api_key.get_secret_value(),
            base_url=settings.base_url,
        )
    return _client


def embed(texts: list[str]) -> list[list[float]]:
    """把一批文本向量化, 返回顺序与输入严格一致。

    - 空输入直接返回 [], 不发请求
    - 按 BATCH_SIZE 分批, 每批校验返回条数, 每条校验维度
    - 不吞异常: 401 / 400 原样抛出, 别让真实原因被 try/except 吃掉
    """
    if not texts:
        return []

    vectors: list[list[float]] = []
    for batch_index, start in enumerate(range(0, len(texts), BATCH_SIZE), start=1):
        batch = texts[start : start + BATCH_SIZE]
        response = _get_client().embeddings.create(model=settings.model, input=batch)

        if len(response.data) != len(batch):
            raise ValueError(
                f"第 {batch_index} 批条数不对: 期望 {len(batch)}, 实际{len(response.data)}"
            )

        for item in response.data:
            vector = item.embedding
            if len(vector) != settings.dim:
                raise ValueError(f"向量维度不对: 期望 {settings.dim}, 实际 {len(vector)}")
            vectors.append(vector)

    if len(vectors) != len(texts):
        raise ValueError(f"向量总数不对: 期望 {len(texts)}, 实际 {len(vectors)}")
    return vectors
