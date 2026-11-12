import math

from openai import OpenAI

from yiagent.config import embeddings_settings as settings



raw = settings.api_key.get_secret_value()
print("key 长度:", len(raw))
print("key 前6:", repr(raw[:6]))
print("key 后4:", repr(raw[-4:]))
print("首尾有空白:", raw != raw.strip())


client = OpenAI(
    api_key=settings.api_key.get_secret_value(),
    base_url=settings.base_url,
)


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


texts = [
    "按 E 进入驾驶模式，开船期间不能钓鱼",
    "开船的时候不能抛竿",
    "红烧肉要小火慢炖两个小时"
]
resp = client.embeddings.create(model=settings.model, input=texts)
vectors: list[list[float]] = [d.embedding for d in resp.data]

print("维度:", [len(v) for v in vectors])
print("相关对 (0,1):", round(cosine(vectors[0], vectors[1]), 4))
print("无关对 (0,2):", round(cosine(vectors[0], vectors[2]), 4))
