from functools import lru_cache
from importlib.resources import files


@lru_cache
def load_system_prompt() -> str:
    return files("yiagent").joinpath("prompts", "system.md").read_text(encoding="utf-8")
