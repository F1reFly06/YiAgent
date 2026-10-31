# YiAgent 项目总览

> 最后更新：2026-10-31 · 当前阶段：Phase 2（工具调用循环）
> 每次开工前读这份，收工后更新第 8、9 节。

## 1. 一句话是什么

一个能检索自己 Markdown 笔记、会调用工具的对话助手。现阶段只做 CLI，Phase 7 再加 Web。
核心目标是**学明白 Agent 内部怎么运转**，顺带产出一个能写进简历的公开项目。

## 2. 明确不做什么

- 不做账号体系、计费、多租户（"商业化"指工程规范，不是真去卖）
- 不接 PDF，第一版只支持 Markdown / txt
- 不使用 LangChain 等框架，工具循环手写
- 第一版不做多 agent、不做 rerank、不做混合检索

## 3. 协作约定

- **代码由我主写**，AI 负责讲概念、给目录/接口建议、review、解释报错、起文档骨架
- 只有我明确说"帮我写 X"，AI 才写代码，且只写那一块
- **一次只推进一小步**，一步做完再进下一步
- 每完成一步，更新本文件第 6、8 节和 `docs/DEVLOG.md`

## 4. 已定决策（改动前必须重新讨论）

| 决策 | 取值 | 理由 |
|---|---|---|
| Python | 3.12 | 3.14 太新，带 C 扩展的库没有预编译包，Windows 上会编译失败 |
| 代码组织 | 单包 `src/yiagent/` 内部分层 | 不是 monorepo：一个人 + 纯 Python，拆 workspace 是净负担 |
| Agent 框架 | 不选，手写工具循环 | 求职要能讲清 loop 内部；框架会把这层黑盒化 |
| 对话模型 | DeepSeek `deepseek-chat`（OpenAI 兼容协议） | 便宜、国内直连、便于跑评测 |
| Embedding | 硅基流动 `BAAI/bge-m3`（1024 维） | DeepSeek 没有 embedding 接口，必须另一家 |
| 向量检索 | 第一版 numpy 暴力 cosine | 千级 chunk 够用，不装重依赖，也便于理解原理 |
| 向量库（后续） | 视情况换 chromadb | `store.py` 只有 add/search 两个方法，换库只改一个文件 |
| 会话持久化 | SQLite（Phase 3 引入） | 比 JSON 文件能讲事务和索引，比 Postgres 轻 |
| RAG 接入方式 | 做成 `knowledge_search` **工具** | 让模型自主决定何时检索（agentic RAG），这是核心亮点 |
| 知识库语料 | 自己的 Markdown 笔记 | 切块按标题层级切，质量最好控 |
| 交付形态 | CLI 优先，Phase 7 加 FastAPI + Web | 核心与入口分离，加 Web 时核心不改 |
| 工程规范 | ruff + 类型注解 → Phase 3 后加 pytest/pre-commit → Phase 6 后加 CI | 一次性全上会劝退，分阶段引入 |
| 仓库 | 公开到 GitHub，MIT License | 简历需要可访问链接 |

## 5. 技术栈

`uv`（依赖与解释器管理）· `ruff`（lint + format）· `openai` SDK（走 base_url 兼容 DeepSeek）
`typer` + `rich`（CLI）· `pydantic-settings`（配置）· `pytest`（Phase 3 后）· `SQLite`（Phase 3）

## 6. 进度

总工期预估 **8–10 周**（每周 10 小时以上）。

| Phase | 内容 | 状态 |
|---|---|---|
| 0 | 环境与骨架 | ✅ 已完成（2026-10-28 首次提交并推送到 GitHub） |
| 1 | 最小流式对话（CLI 能边生成边打印） | ✅ 已完成（2026-10-31） |
| 2 | **工具调用循环 ★** | **进行中** |
| 3 | 会话与持久化 | 未开始 |
| 4 | RAG 入库与检索 | 未开始 |
| 5 | **检索变成工具 ★** | 未开始 |
| 6 | 评测集 | 未开始 |
| 7 | Web + 部署 | 未开始 |

★ = 核心竞争力，其余是支撑。**第 4 周末**即可在简历上写第一段（Phase 0–2）。

实际进度：Phase 0–1 用 5 天完成（2026-10-27 ~ 10-31），比排期提前约 1 周。但后半程难度更高（工具循环的状态机、RAG 的召回质量），**不要按前半程速度外推**。

## 7. 目录地图

只列**当前真实存在**的文件，随开发增长。`src/yiagent/` 下的子包按 Phase 逐个建，不提前占位。

```
pyproject.toml            依赖清单 + ruff 配置 + [project.scripts] 入口
uv.lock                   锁定版本（提交）
.python-version           钉 Python 3.12（提交）
.gitignore                忽略密钥与 IDE 配置
.env                      本地真实密钥（不提交）
.env.example              配置模板（值全为假，进 git）
.vscode/settings.json     解释器 / ruff 保存即格式化与自动修复
README.md                 对外说明（定位 / 进度 / 开发环境）
LICENSE                   MIT 许可证
docs/DEVLOG.md            开发日志：每天做了什么、踩了什么坑
docs/PROJECT.md           本文件：目标 / 决策 / 状态

src/yiagent/__init__.py   空（脚手架残留的 main() 已删）
src/yiagent/config.py     两个 BaseSettings 子类 + 模块级单例 chat_settings / embedding_settings
src/yiagent/core/message.py   Role 枚举 + Message dataclass + to_dict()
src/yiagent/core/llm.py       LLMProvider 协议（唯一的接口契约）
src/yiagent/core/prompt.py    load_system_prompt()，importlib.resources + lru_cache
src/yiagent/prompts/system.md 系统提示词（人设 / 能力边界 / 风格 / 不编造）
src/yiagent/providers/openai_compat.py  OpenAIChatProvider：唯一碰网络的地方
src/yiagent/cli/main.py       typer + rich 入口：_stream_reply / _chat_loop / main 三层
```

Phase 2 预计新增：`core/message.py` 加工具调用字段的辅助构造、`core/tools.py`（工具注册表 + 执行分发）、`providers/openai_compat.py` 加 `tools=` 参数与 `tool_calls` 分片拼装、`cli/main.py` 加“工具循环”（一轮可能包含多次请求）。

## 8. 下次接着干的入口

- **当前在**：Phase 2（工具调用循环），代码还没动
- **Phase 1 已完成（2026-10-31）**：`uv run yiagent` 可直接流式对话，支持多轮历史、`/clear`、`/exit`、Ctrl+C 与 API 异常兜底；`ruff check` 0 错误
  - `config.py`：两个 BaseSettings 子类 + 模块级单例
  - `core/message.py`：`Role` + `Message` + `to_dict()`（只输出有值字段）
  - `core/llm.py`：`LLMProvider` 协议（`stream(messages) -> Iterator[str]`）
  - `core/prompt.py`：`load_system_prompt()`（`importlib.resources` + `lru_cache`）
  - `prompts/system.md`：人设 / 能力边界 / 风格 / 不编造
  - `providers/openai_compat.py`：`OpenAIChatProvider`，把 chunk 收窄成 `str`
  - `cli/main.py`：三层结构 —— `main`（装配）/ `_chat_loop`（轮次 + 历史）/ `_stream_reply`（打印 + 聚合，只读 messages）
- **Phase 2 第一步（下次开工从这里开始）**：
  1. 先想清楚“工具清单怎么传给 `create(tools=...)`”——定义在 `core/tools.py`，用 JSON Schema 描述，**不要让 core 依赖 openai 的类型**
  2. `Message` 加 `tool_calls` 的写入路径：模型返回时如何把分片拼成完整 JSON
  3. 改 `providers/openai_compat.py` 的出口：`str` 不够了，要能产出“文本增量 / 工具调用增量”两类事件（建议自定义事件类型，放在 `core/llm.py`）
  4. `cli/main.py` 增加工具循环：请求 → 若 `finish_reason == "tool_calls"` → 执行工具 → 追加 `role="tool"` 消息 → 再请求
- **阻塞项**：无。DeepSeek key 已在 `.env`，`chat_settings` 可用
- **协作约定**：我主写代码，AI 只讲解 / review / 起草文档（见第 3 节）

### 几个已踩过的坑（细节在 DEVLOG）

- `config.py` 只写类不写实例 → `from yiagent.config import chat_settings` 报「未知导入符号」，末尾必须有 `chat_settings = ChatSettings()`
- basedpyright 会把 `api_key: SecretStr` 这类无默认值字段标红，是误报（运行时由 pydantic-settings 从 `.env` 读），**不要**改成手动传参
- `openai` SDK 的 `messages` 形参要求 `list[ChatCompletionMessageParam]`，直接传 `list[dict]` 会报类型错，用 `cast` 过去
- `providers/__init__.py` 保持空文件，不在里面做转发导出
- `@override` 缩进少一个空格 → 解析器崩，连带报「此处应有表达式」「语句必须用换行符或分号分隔」等 6 条离谱错误。**看到这类报错先往上找缩进/括号**
- VS Code 自动导入会把 `from openai.types.responses import response`、`from httpx2 import Response` 塞进文件（openai 3.x 内部用 `httpx2`，撞名）
- 给 `response: Any` 消错是陷阱：`Any` 会向下传播，把 `chunk` / `choices` / `delta` 全变成未知；一条根因（重载匹配失败）会连带出 6 条「类型未知」
- `Protocol` 覆盖检查**连参数名都要求一致**：`llm.py` 写 `message`、实现写 `messages` → `reportIncompatibleMethodOverride`
- `rich.console.print` 打印任意文本必须 `markup=False`，否则内容里的 `[` 会被当标记语法（`MarkupError` 或丢字）



## 9. 已知的坑

- `.gitignore` 只对**未跟踪**的文件生效；已提交过的文件要 `git rm --cached` 才能停跟，且历史里仍有记录
- `.env` 这条规则只匹配恰好叫 `.env` 的文件，不含 `.env.local` 等
- Markdown 的 `#` 后面**必须有空格**，否则不渲染成标题
- Windows 上安装带 C 扩展的库容易触发本地编译失败，这是钉 3.12 的原因
- DeepSeek 没有 embedding 接口，向量化必须用另一家
- `uv sync` 重建 `.venv` 后，PyCharm 里需要重新指定解释器
- `.idea/` 可随时删除，PyCharm 会重建，只影响解释器和源码根目录设置
- **模块级代码在 import 时执行**：`config.py` 末尾的单例一被 import 就读 `.env`，缺字段时错误发生在 import 那一刻，栈里看不出业务上下文
- `env_file=".env"` 是**相对 cwd** 解析的，换个目录跑就找不到（`importlib.resources` 定位 `system.md` 就避开了这个问题）
- **在非项目目录 `uv run` 会找不到包**：`PyCharm/D:\` 下 `uv run python` 会用一个不含 `yiagent` 的环境，要加 `--project d:/YiAgent` 或先 `cd` 回项目根
- 缩进错误在 Python 里是**语义错误不是格式错误**：模型调用段掉出 `while` → 表现为“只重复提示、从不回答”，程序不报错、lint 也不报错
- `while True` 里 `break` 之后，循环**外面**的代码会执行一次（不是“永不执行”）；判断命令必须在 `messages.append` **之前**，否则命令文本会被发给模型
- `/clear` 要用 `del messages[1:]`（保留 index 0 的 system），写成 `messages = []` 只改局部引用、`clear()` 会把人设一起删掉
- `stream=True` 只改变**响应**方式（SSE 分块），请求体始终是整包，模型无状态、每轮都要重发全部历史
- `python.analysis.extraPaths` 是 Pylance 的设置，basedpyright 不读它（本项目靠 editable 安装的 `.pth` 解决导入）

