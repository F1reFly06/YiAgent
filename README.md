# YiAgent

> 一个能检索自己 Markdown 笔记、会调用工具的对话助手。

**状态：开发中 · 项目骨架已就绪（Phase 0 / 7）· 当前暂无可用功能**

## 这是什么

我把自己的 Markdown 笔记当作知识库，让模型在回答前自己判断需不需要去查。和普通 ChatGPT 对话的区别是：它引用的是我自己的资料，而且「要不要检索」是模型自己决定的，不是我硬塞进 prompt 里的。

本质上这不是一个产品，而是一个学习项目——目标是把 Agent 的内部机制拆开看清楚，而不是拿框架拼一个能跑的东西。

## 现在能做什么 / 不能做什么

**已经完成**

- 项目骨架：分层目录结构、依赖管理（uv）、代码规范（ruff + `pyproject.toml` 配置）
- 配置模板 `.env.example`：对话模型走 DeepSeek，向量化走硅基流动
- 文档：架构决策、开发日志、项目总览

**还没有**

- 不能对话——没有 CLI 入口
- 不能检索笔记——RAG 管线尚未开始
- 没有测试、没有 CI

## 为什么手写而不用 LangChain 这类框架

工具调用循环本质只有四步：带工具定义请求 → 模型返回 `tool_calls` → 执行工具 → 结果塞回 `messages` 再请求。手写不到 100 行。

而框架会把这四步藏在内部。一旦模型不按预期调用工具、反复调同一个工具、或者参数格式出错，你无法判断问题出在哪一层。这个项目的目的正是把这层拆开看，所以选择手写。

## 计划中的能力

| Phase | 内容 | 状态 |
|---|---|---|
| 0 | 环境与项目骨架 | ✅ 已完成 |
| 1 | 最小流式对话（CLI 边生成边打印） | 未开始 |
| 2 | 工具调用循环 | 未开始 |
| 3 | 会话与持久化（SQLite） | 未开始 |
| 4 | RAG 入库与检索 | 未开始 |
| 5 | 检索接入为工具（模型自主决定何时检索） | 未开始 |
| 6 | 评测集 | 未开始 |
| 7 | Web 界面与部署 | 未开始 |

> 详细的决策记录与当前进度见 [docs/PROJECT.md](docs/PROJECT.md)。

## 技术栈

Python 3.12 · [uv](https://docs.astral.sh/uv/) · openai SDK（OpenAI 兼容协议）· typer · rich · pydantic-settings · ruff

规划中：SQLite（会话持久化）、numpy 向量检索（RAG）

## 开发环境

需要 [uv](https://docs.astral.sh/uv/) 与 Python 3.12。

```bash
git clone https://github.com/F1reFly06/yiagent.git
cd yiagent
uv sync
cp .env.example .env    # 填入自己的 API key
```

> 目前还没有可运行的命令，Phase 1 完成后补充使用说明。

## 项目结构

```
src/yiagent/
  core/         协议与数据模型（不含具体实现）
  providers/    模型接入（当前：OpenAI 兼容协议）
  agent/        工具调用循环
  tools/        工具实现
  retrieval/    RAG 管线
  cli/          命令行入口
docs/           项目总览、开发日志、架构决策
```

> `src/yiagent/` 下的子包按阶段逐个建立，当前尚未创建。
> 各层职责与关键决策见 [docs/PROJECT.md](docs/PROJECT.md)。

## License

[MIT](LICENSE)
