# YiAgent 项目总览

> 最后更新：2026-11-23 · 当前阶段：**Phase 4（RAG 入库与检索）进行中** —— A1 / A2 / A4 / B1 完成（全仓 17 passed），A5 前置 `providers/embedding.py` 已就绪，下一步 A5 端到端 spike
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
| Embedding 代码位置 | `providers/embedding.py`（不放 `core/`） | 网络请求一律留在 `providers/`；`core/` 保持纯逻辑，不用 key 也能 import 和测试。代价是 `core/` 里看不到“文本→向量”这一步，要在目录地图里写明 |
| 向量检索 | 第一版 numpy 暴力 cosine | 千级 chunk 够用，不装重依赖，也便于理解原理 |
| 向量库（后续） | 视情况换 chromadb | `core/vector_store.py`（拟）只有 add/search 两个方法，换库只改一个文件 |
| 会话持久化 | SQLite（Phase 3 引入） | 比 JSON 文件能讲事务和索引，比 Postgres 轻 |
| 会话持久化模块命名 | `core/session_store.py` | 原名 `store.py` 与上一条「向量库 store」撞名，同一个词指两个东西；加前缀后两文件各表一职，读代码不用猜 |
| `system` 消息是否入库 | **不入库**，每次启动用 `load_system_prompt()` 现生成 | prompt 会反复修改，存进库就是旧版本、改了不生效；库里只留真实对话（user / assistant / tool） |
| 会话续接策略 | 默认**继续上次**：`latest_session()` 找到就复用，找不到才 `create_session()` | 每次新建会让 `load_session` 永远返回空列表，持久化等于白做 |
| RAG 接入方式 | 做成 `knowledge_search` **工具** | 让模型自主决定何时检索（agentic RAG），这是核心亮点 |
| 知识库语料 | 自己的 Markdown 笔记 | 切块按标题层级切，质量最好控 |
| 交付形态 | CLI 优先，Phase 7 加 FastAPI + Web | 核心与入口分离，加 Web 时核心不改 |
| 工程规范 | ruff + 类型注解 → Phase 3 后加 pytest/pre-commit → Phase 6 后加 CI | 一次性全上会劝退，分阶段引入 |
| pytest 的定位 | 作为 **Phase 3 → Phase 4 的过渡任务**，不算单独的 Phase | 持久化层已经出过两个「不报错但静默错」的 bug，值得先上保险再进 RAG |
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
| 2 | **工具调用循环 ★** | ✅ 已完成（2026-11-04） |
| 3 | 会话与持久化 | ✅ 已完成（2026-11-05 ~ 11-09） |
| 3.5 | **过渡：pytest 测试持久化层** | ✅ 已完成（2026-11-11，6 passed / 0.13s；不计入 Phase，见第 4 节决策） |
| 4 | RAG 入库与检索 | 🔨 进行中（A1 ✅ / A2 ✅ / A4 ✅ / B1 ✅，A5 前置 `providers/embedding.py` ✅；共 11 小步，见第 8 节） |
| 5 | **检索变成工具 ★** | 未开始 |
| 6 | 评测集 | 未开始 |
| 7 | Web + 部署 | 未开始 |

★ = 核心竞争力，其余是支撑。**第 4 周末**即可在简历上写第一段（Phase 0–2）。

实际进度：Phase 0–1 用 5 天完成（2026-10-27 ~ 10-31），Phase 2 用 4 天完成（11-01 ~ 11-04），共 9 天走完前置三个阶段，比排期（4 周末完成 Phase 0–2）提前约 2 周。

Phase 2 内部三步：① 事件流接口 ✅ ② 工具定义与执行 ✅ ③ provider 接工具 + CLI 工具循环 ✅。

Phase 3 时间线（2026-11-05 ~ 11-09，共 4 个工作日）：Day10 建表 → Day12（11-07）`create_session` → Day13（11-08）`append_message` + `load_session` → Day14（11-09）`latest_session` + 接入 `cli/main.py` + 端到端跑通（重启后能答出「我是任旭阳」）。

但后半程难度更高（RAG 的召回质量、评测集设计），**不要按前半程速度外推**。

## 7. 目录地图

只列**当前真实存在**的文件，随开发增长。`src/yiagent/` 下的子包按 Phase 逐个建，不提前占位。

```
pyproject.toml            依赖清单 + ruff 配置 + pytest 配置 + [project.scripts] 入口
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

data/yiagent.db           本地 SQLite 库（运行产物，已在 .gitignore，不进 git）
src/yiagent/__init__.py   空（脚手架残留的 main() 已删）
src/yiagent/config.py     两个 BaseSettings 子类 + 模块级单例 chat_settings / embedding_settings
src/yiagent/core/message.py   Role 枚举 + Message dataclass + to_dict()
src/yiagent/core/llm.py       LLMProvider 协议 + 三个事件（TextDelta / ToolCall / Done）
src/yiagent/core/tools.py     Tool 数据结构 + 两个示例工具 + TOOLS 注册表 + execute_tool
src/yiagent/core/prompt.py    load_system_prompt()，importlib.resources + lru_cache
src/yiagent/core/session_store.py  会话持久化：_SCHEMA（sessions / messages）+ _connect / init_db / create_session / latest_session / append_message / load_session；**全项目唯一写 SQL 的地方**
src/yiagent/prompts/system.md 系统提示词（人设 / 能力边界 / 风格 / 不编造）
src/yiagent/providers/openai_compat.py  OpenAIChatProvider：chat 方向唯一碰网络的地方，产出事件流
src/yiagent/providers/embedding.py  embedding 方向的网络层：embed(texts) -> list[list[float]]（惰性 client + 分批 32 + 条数/维度校验 + 不吞异常）
src/yiagent/cli/main.py       typer + rich 入口：main(建表/续接会话/载历史) + _chat_loop / _run_turn(带 session_id, 结束写库) / _save_new_messages / _stream_reply
src/yiagent/core/chunking.py  切块：Chunk 数据契约(frozen, 4 字段) + split_markdown(标题栈 + 代码块保护 + 孤立#过滤 + 超长切分)
src/yiagent/core/vector_store.py  内存向量库：SearchHit + VectorStore(_matrix/_chunks/_dim + add 四关校验 + search 暴力点积)

tests/test_session_store.py  持久化层测试：db fixture(tmp_path 临时库) + _seqs() 直查 helper + 6 个用例
tests/test_chunking.py       切块测试：6 条性质用例（非空 / 无同级嵌套 / 代码块保护 / 孤立#丢弃 / 超长切分 ×2）
tests/test_vector_store.py   向量库测试：5 条（排序+分数归属 / 数量不一致 / 维度不一致且不污染 / 空库 / top_k 超长）
scripts/probe_embedding.py  embedding 链路自检：key 长度 / 维度 / 相关对 vs 无关对（对照组）
scripts/dump_chunks.py      切块检视器：剥掉 heading 前缀打印正文 + 每块字数 + 长度分布（不断言）
scripts/spike_vector.py     向量库手工冒烟：3 条假向量验排序与条数，不调网络
```

Phase 2 完成（2026-11-04）：工具调用闭环打通。provider 侧 `tools=` + 按 `tc.index` 分桶累积 `tool_calls` + 循环外先 `ToolCall` 后 `Done`；CLI 侧 `_run_turn` 工具轮次循环（开关是 `finish_reason == "tool_calls"` **且** `tool_calls` 非空）、三段式历史、`MAX_TOOL_ROUNDS = 5`、异常时 `del messages[start:]` 回滚。

Phase 3 完成（2026-11-09）：会话持久化闭环打通。`session_store` 六个函数齐全（`_connect` / `init_db` / `create_session` / `latest_session` / `append_message` / `load_session`）；`main()` 启动流程 `init_db → latest_session（为 None 才 create_session）→ load_session → [system, *history]`；`_run_turn` 带上 `session_id`，在 `finally` 里把 `messages[start:]` 逐条落库（失败时该切片已被 `del` 清空，天然不写）。端到端验收：**同一进程内、以及退出重开后，都能答出「我是任旭阳」**。
表结构 `sessions(id, created_at, title)` / `messages(id, session_id, seq, role, content, tool_calls, tool_call_id)` + 索引 `idx_messages_session_seq`；`_connect()` 统一做 `PRAGMA foreign_keys = ON` 和 `row_factory = sqlite3.Row`。

Phase 3.5 完成（2026-11-11）：持久化层补上测试护栏。`tests/test_session_store.py` 6 个用例全绿（`6 passed in 0.13s`），覆盖往返保真、`None` / `[]` 边界返回值、`seq` 自增与按会话独立、外键约束生效；`pyproject.toml` 新增 `[tool.pytest.ini_options]`（`testpaths = ["tests"]` + `pythonpath = ["src"]` + `addopts = "-q"`）。

## 8. 下次接着干的入口

- **当前在**：**Phase 4 进行中**（2026-11-12 ~ 11-23）。已完成：embedding 链路验证、A1 依赖与契约、A2 切块 v1、B1 切块打磨 + 测试护栏（`test_chunking.py` 6 条）、A4 `VectorStore` 内存版 + 测试护栏（`test_vector_store.py` 5 条）、A5 前置 `providers/embedding.py`；全仓 **17 passed**
- **下次第一件事**：① 写 `scripts/spike_e2e.py` 跑 A5（`docs/DEVLOG.md` → `split_markdown` → `embed` → `store.add` → `embed("怎么写测试")[0]` → 打印 top-3 的 heading / line_start / score / 正文前 80 字）② 人眼判命中，顺便记下真实语料的分数区间，为 B2 的 `min_score` 提供依据 ③ 进 B2（L2 归一化 + `min_score`）；可选收尾：补 `add` 累积路径、非空库 `top_k=0` 两条用例
- **Phase 1 已完成（2026-10-31）**：`uv run yiagent` 可流式对话，支持多轮历史、`/clear`、`/exit`、Ctrl+C 与 API 异常兜底；`ruff check` 0 错误
  - `config.py` 单例 / `core/message.py` 数据契约 / `core/prompt.py` 加载 prompt / `prompts/system.md`
  - `cli/main.py`：三层 —— `main`（装配）/ `_chat_loop`（轮次 + 历史）/ `_stream_reply`（打印 + 聚合，只读 messages）
- **Phase 2 已完成（2026-11-01 ~ 11-04）**：
  - `core/llm.py`：三个冻结 dataclass —— `TextDelta` / `ToolCall(id, name, arguments)` / `Done(finish_reason)`，别名 `StreamEvent`，`LLMProvider.stream` 返回 `Iterator[StreamEvent]`
  - `core/tools.py`：`Tool(name, description, parameters, func)`、`get_current_time` / `word_count` 两个工具、`TOOLS` 注册表、`execute_tool()` —— **任何失败都返回错误字符串，绝不抛异常**（让模型能自我纠正）
  - `providers/openai_compat.py`：
    - `_to_openai_tools()`：协议转换，`__init__` 里装配一次存 `self.tools`（判断标准是「进程内变不变」）；`create()` 带 `tools=`
    - `_ToolCallDraft`：按 `tc.index` 分桶累积；`id` / `name` 只在首块出现，必须 `if tc.id:` 才赋值；`arguments` 用 `+=` 拼碎片
    - `_parse_arguments()`：三道兜底（空串 / 畸形 JSON / 非 dict）都返回 `{}`，永不抛异常
    - 循环外按 index 排序先 `yield ToolCall` 再 `yield Done`（顺序反了工具调用会被静默丢弃；异常时不发 Done）
  - `cli/main.py` 三层：`_chat_loop`（用户轮次）→ `_run_turn`（工具轮次，**唯一改历史的地方**）→ `_stream_reply`（一次请求，返回 `_ReplyResult`）
    - `_ReplyResult(text, tool_calls, finish_reason)` 取代裸 `str`：一次请求的产出自带意图，只有 `str` 的话无法区分「不说话只调工具」「出错返回空」「内容被过滤」
    - 历史三段式：`assistant(tool_calls)` → `tool(结果)` → `assistant(最终回答)`
    - `_tool_call_to_dict()`：`arguments` 用 `json.dumps(ensure_ascii=False)` 转回字符串写进历史
    - 继续条件：`finish_reason == "tool_calls"` **且** `tool_calls` 非空；`MAX_TOOL_ROUNDS = 5`
    - 异常时 `del messages[start:]` 回滚本轮，`_chat_loop` 再 `pop()` 用户消息（两层各删各的）
- **Phase 3 已完成（2026-11-05，Day10）**：
  - 表结构落地：`sessions(id, created_at, title)` + `messages(id, session_id, seq, role, content, tool_calls, tool_call_id)`，`session_id` 带 `REFERENCES sessions(id) ON DELETE CASCADE`，索引 `idx_messages_session_seq(session_id, seq)`；`tool_calls` 存 JSON 字符串（SQLite 没数组类型），`content` 允许 `NULL`（assistant 只调工具时没有文本）
  - `_connect()`：唯一开连接入口，每条新连接都设 `PRAGMA foreign_keys = ON` + `row_factory = sqlite3.Row` —— 这两项是**连接级**的，不继承上一次连接
  - `init_db()`：`Path(...).parent.mkdir(parents=True)` + `executescript(_SCHEMA)` + commit，幂等，启动时调一次
  - 文件原名 `store.py`，已 `git mv` 为 `session_store.py`（git 状态 `R`，历史不断），理由见第 4 节；改名与 `.gitignore` 已提交
- **决策：Phase 3 的读写函数改由我自己写（2026-11-05）**
  - 起因：AI 曾顺着上下文补完 `create_session` / `append_message` / `load_messages`，与第 3 节「代码由我主写」冲突，已回退（commit `d90636d`）
  - 现在的分工：**AI 只给接口设计和坑点，函数体我自己敲，写完再让 AI review**
  - 理由：`lastrowid` 的类型、ISO 时间能不能被 `fromisoformat()` 解析回来、异常路径漏没漏 `close`，这些自己写一遍才记得住
- **Phase 3 最终实现（2026-11-05 ~ 11-09）**：
  - `create_session(db_path, title=None) -> int`：参数化 INSERT → `commit` → `int(cur.lastrowid or 0)`；`created_at` 用 `datetime.now(UTC).isoformat(timespec="seconds")`
  - `latest_session(db_path) -> int | None`：`SELECT id FROM sessions ORDER BY id DESC LIMIT 1`，`fetchone()` 为 `None` 时返回 `None`（排序用 `id` 不用 `created_at`，后者只到秒、同秒会并列）
  - `append_message(db_path, session_id, message) -> None`：先 `SELECT COALESCE(MAX(seq),0) AS last_seq`，再 INSERT 六列；`tool_calls` 走 `json.dumps(ensure_ascii=False)`，`role` 显式 `str(...)`，`seq` 由函数内部算
  - `load_session(db_path, session_id) -> list[Message]`：`WHERE session_id=? ORDER BY seq` + `fetchall()`，`Role(...)` 反查、`json.loads` 还原
  - `cli/main.py`：`DB = "data/yiagent.db"`；`main()` 走 `init_db → latest_session（None 才 create）→ load_session → [system, *history]`；`_run_turn(provider, messages, session_id, start)` 里 **`start` 由调用方在 `append(USER)` 之前算好传进来**，`finally: _save_new_messages(messages[start:], session_id)`；`_chat_loop(provider, messages, session_id)`
- **Phase 3.5 已完成：pytest 覆盖持久化层（2026-11-11）**
  - 依赖与配置：`uv add --dev pytest`（落到 `[dependency-groups] dev`）；`pyproject.toml` 末尾加 `[tool.pytest.ini_options]` —— `testpaths = ["tests"]`、`pythonpath = ["src"]`（src 布局兜底，不依赖 editable 安装）、`addopts = "-q"`
  - 目录：`tests/` 与 `src/` 平级（测试不进包、不随 wheel 发布），**不需要 `__init__.py`**（pytest 按文件名 `test_*.py` 收集）
  - `tests/test_session_store.py` 实际 6 个用例，全部跑绿（`uv run pytest` → `6 passed in 0.13s`）：
    1. `test_save_and_load_roundtrip` —— user 文本 / assistant(`content=None` + `tool_calls`) / tool(`tool_call_id`) 三条往返，断言 role 顺序、`content` 仍为 `None`（不是 `"None"`）、`tool_calls` 仍是 `list` 且内容相等、`tool_call_id` 保留
    2. `test_latest_session_none_then_latest` —— 空库 `None`；建两个会话后分别返回 `first` / `second`
    3. `test_empty_session_returns_empty_list` —— 空会话返回 `[]`（不是 `None`，否则 `[system, *history]` 会 `TypeError`）
    4. `test_append_message_seq_autoincrement` —— 连写 3 条，库里 `seq` 必须是 `[1,2,3]`
    5. `test_seq_is_per_session` —— 两会话各写 2 / 1 条，`seq` 各自从 1 起（`[1,2]` / `[1]`）；**专门抓 `SELECT MAX(seq)` 漏 `WHERE session_id` 的静默 bug**
    6. `test_foreign_key_enforced` —— 往 id=999 写消息抛 `sqlite3.IntegrityError`，证明 `_connect()` 里的 `PRAGMA foreign_keys = ON` 真生效（SQLite 默认 OFF，删掉那行功能照常、`ON DELETE CASCADE` 静默失效）
  - 实现约定：`db` fixture 基于 `tmp_path` 每测一份全新空库（`init_db` 后返回 `str` 路径），**绝不碰 `data/yiagent.db`**；`_seqs()` helper 直接 `SELECT seq` 查库，刻意不用 `load_session` 验 `seq`（避免用它自己的 `ORDER BY seq` 自证）
  - `TOOL_CALLS` 必须显式标注 `list[dict[str, object]]`：字面量会被推断成更窄的 `list[dict[str, str | dict[str, str]]]`，而 `list` / `dict` 都是不变的，与 `Message.tool_calls` 的声明不兼容（basedpyright 报错，运行时无影响）
  - **本批未覆盖**：`MAX_TOOL_ROUNDS` 超限、`_run_turn` 的 `except → del messages[start:]` 回滚——这两条要伪造 `LLMProvider`（`stream()` 按剧本吐 `ToolCall` 事件）才测得到，留给后续
- **Phase 4 拆步（A 打通 → B 做对 → C 可用，共 11 小步）**：
  - **A 最小闭环**：A1 依赖与契约 ✅ / A2 切块 v1 ✅（2026-11-16 验收）/ A3 embedding 链路 ✅（探针）/ A4 `VectorStore` 内存版 ✅（2026-11-18 代码 + 2026-11-19 测试护栏）/ A5 端到端 spike 脚本 ← 下一步（前置 `providers/embedding.py` ✅ 2026-11-23）
  - **B 做对**：B1 切块 v2 ✅（2026-11-16，代码块保护 + 孤立 `#` 过滤 + 超长块按段落累积 + 硬切）/ B2 L2 归一化 + `min_score` / B3 `save` / `load` + `meta.json` 校验 `dim` 与 `model`
  - **C 可用**：C1 `indexer.py` 扫目录 + `build_index` / C2 `yiagent index` 子命令（**注意：Typer 加第二个 command 后裸跑会变 help 页，必须先把 `main` 改成 `@app.callback(invoke_without_command=True)`**）/ C3 真实语料 10 个问题看 top-3 命中率（同时是 Phase 5 的检索基线）
- **Phase 4 进度：A1 ✅ / A2 ✅ / B1 ✅（2026-11-12 ~ 11-16）**：
  - `Chunk(text, source, heading, line_start)`，`frozen=True`；只留 4 个字段，每个都必须有下游消费者；`heading` 单独存一份而不只拼进 `text`（从 `text` 反解析标题很脆弱）
  - `split_markdown(text, source, max_chars=DEFAULT_MAX_CHARS) -> list[Chunk]`：栈 `list[tuple[int, str]]` 维护标题路径、`buffer` 攒正文行、`heading_line` 记块起始行号（初始 1，因为开头可能有无标题正文）
  - 关键时机：**块是在「遇到下一个标题」那一刻封口的**，所以循环结束后必须再 `flush()` 一次，否则最后一块永远出不来
  - 栈弹出条件是 `stack[-1][0] >= level`（**`>=` 不是 `>`**）：同级互斥、子级累加，用 `>` 会拼出「二级 > 二级」
  - 正则 `^(#{1,6})\s+(.+)$`：`^` 保证缩进的 `#` 不算标题，`\s+` 强制 `#` 后有空格（与 Markdown 规范一致）
  - 空块（只有标题没正文）**有意丢弃**：对检索无价值，留着只制造噪声
  - 命名已统一（2026-11-16）：常量 `DEFAULT_MAX_CHARS`、参数 `max_chars`
  - v1 验收数据（`docs/DEVLOG.md`）：27 块 / 平均 285 字 / 最长 1002 字 / 超 800 的 1 块；标题路径全部两级递进、无同级嵌套、正文可连读
  - **B1 打磨（2026-11-16，同文件）**：
    - 代码块保护：`_FENCE_RE = r"^\s*```"` + 循环内 `in_fence` 翻转；翻转后该行直接进 buffer，且 `match = None if in_fence else _HEADING_RE.match(line)` 让代码块内的 `#` 强制走「非标题」分支（**不复制一遍 `buffer.append` 逻辑**）
    - 孤立 `#` 行过滤：`_ONLY_HASHES_RE = r"^#{1,6}$"`，`###`（后面没文字）直接丢弃，不进 buffer 也不算标题
    - 超长切分：`_split_long(body, max_chars) -> list[str]`，按 `"\n\n"` 拆段后重新累积打包（`+2` 计入段落间 `\n\n`），单段仍超预算则切片硬切；`flush()` 里用 `for piece in _split_long(body, max_chars - prefix_len)`，**`prefix_len = len(heading) + 1`（标题前缀也占预算）**，切出的多块共享同一 `heading` 与 `line_start`
    - 验收数据：`DEVLOG.md` 27 → **28 块**、**超 800 的 0 块**、第 61 块开头不再有 `###`
    - `dump_chunks.py` 已改成「剥掉 heading 前缀再打印 + 每块字数 + 末尾分布统计」：原先 `text[:50]` 被标题前缀吃满，正文一个字都看不见，会误判成「内容丢了」
  - **B1 的两个静默 bug（已修，值得记住）**：
    1. `flush()` 里写成 `text=f"{heading}\n{body}"`（应为 `piece`）：循环变量是 `piece`，拼进去的却是完整 `body` → 超长章节被拆成 N 个**内容完全相同**的巨块，块数正确、`ruff` 干净、不报任何错
    2. `re.compile(r"^#{1.6}$")`：量词必须是 `{1,6}`（逗号）。写成 `{1.6}` 时 Python **不抛异常**，把 `{1.6}` 当字面量，该正则永远不命中 `###`，过滤功能静默失效
  - v1 明确不做、B1 已补上的：超长块切分、代码块 ``` 内的 `#` 保护
  - 检视器 vs 测试：切块输出形态不唯一，写不出精确期望值，所以 `dump_chunks.py` 只打印不断言；能自动化的只有「性质」（每块非空、heading 无同级重复、`#` 不产生假标题、超长块被拆到上限内）
- **B1 收尾：切块测试护栏（2026-11-17）**：
  - `tests/test_chunking.py` 6 条用例，与 `test_session_store.py` 合计 **12 passed**：
    1. `test_chunks_are_never_empty` —— 各种输入下每块 `text.strip()` 非空
    2. `test_heading_path_has_no_duplicate_levels` —— `heading.split(" > ")` 无重复项（抓「二级 > 二级」）
    3. `test_code_fence_hash_is_not_a_heading` —— ``` 内的 `# 注释` 不产生新块，且整块只有 1 块
    4. `test_isolated_hashes_line_is_dropped` —— 孤立 `###` 不进正文
    5. `test_long_block_with_heading_is_split` —— 3000 字带标题，每块 `len(text) <= 800`
    6. `test_long_block_without_heading_is_split` —— **专门守 `flush()` 的 else 分支**；这条在修 `else body → else piece` 之前是红的（`assert 3000 <= 800`）
  - TDD 时序有价值：先跑出 1 红（`else` 分支的 `body/piece` bug），修完变 12 绿，证明这条测试真的能抓 bug
  - 断言设计原则：**断言行为，不断言全文**。`assert "###" not in text` 比 `assert text == "Day4\n- 今天没做什么"` 更能表达意图，也不会因为 `.strip()` 细节变化而误红
  - 两条偏弱的用例已加固（2026-11-18）：`test_chunks_are_never_empty` 补 `len(chunks) == 2`（原来删掉空块丢弃也照样绿）；`test_heading_path_has_no_duplicate_levels` 改为 `test_heading_path_matches_structure` 精确断言 `["A", "A > B", "A > C", "D"]`（原「无重复字符串」的写法在 `>=` 改成 `>` 时仍然全绿，因为同级标题名字不同，路径里不会出现重复项）
  - 判断测试强度的通用方法：**问「我故意把这行改坏，这条测试会不会红」**（手动变异测试）。对 `>=` 做过一次验证——只有精确断言那条会红
- **A4 完成：`core/vector_store.py` 内存版（2026-11-18）**：
  - `SearchHit(chunk, score)`（frozen）：不用 `tuple[Chunk, float]`，避免 `hit[0]` 这种靠位置取值
  - 三个内部字段：`_matrix: NDArray[np.float32]` 形状 `(n, dim)`、`_chunks: list[Chunk]`、`_dim: int`（0 = 未初始化）；`_matrix` 初始用 `np.zeros((0, 0))` 而不是 `None` / `np.array([])`，**保证形状维度数永远是二维**，`@` 和 `vstack` 都能直接用
  - 核心不变量：**`_matrix` 第 i 行 ↔ `_chunks[i]`**。破了不报错，只是「B 的分数配 A 的内容」
  - `add` 四关：数量一致 → 非空直接返回 → `ndim == 2` → 维度与 `_dim` 一致；然后 `_matrix = matrix if not self._chunks else np.vstack([旧, 新])` + `_chunks.extend(chunks)`（判空必须在 extend **之前**；`vstack` 顺序反了会和 extend 错位）
  - `search` 四步：空库/`top_k<=0` 提前返回（**必须在维度校验之前**，否则空库查询会抛错）→ query 形状必须是 `(dim,)` → `scores = _matrix @ query` 一次算完 → `argsort(scores)[::-1][:top_k]` 取索引 → 用同一行号取 `_chunks[int(i)]`
  - `argsort` 而非 `sort`：`sort` 只给排好序的分数，丢了「属于哪一行」；`scores.sort()` 更是原地改分数但不动 `_chunks`，直接错位
  - **当前是裸点积，不是余弦**：模长大的向量分数偏高。现在能工作是因为 bge-m3 输出向量模长都接近 1；这是个未声明的假设，B2 用 L2 归一化把它变成显式保证
  - 手工验证（`scripts/spike_vector.py`）：3 条假向量 `[1,0] / [0,1] / [0.7,0.7]`，query `[1,0]` → `条数 3`，输出 `A 1.000 / C 0.700 / B 0.000`（手算点积 1.0 / 0.7 / 0.0，顺序对应 `argsort[::-1]`）
  - **A4 测试护栏（2026-11-19）：`tests/test_vector_store.py` 5 条，全仓 17 passed**
    1. `test_search_returns_nearest_first` —— A=`[1,0]` / B=`[0,1]` / C=`[0.7,0.7]`，query=`[1,0]` → 顺序必须是 `A, C, B`；三个分数 1.0 / 0.7 / 0.0 逐项 `pytest.approx`（**抓 `_matrix` 第 i 行与 `_chunks[i]` 错位**：顺序看着对、分数却是别人的）；再补一条 `scores == sorted(scores, reverse=True)` 兜住单调性
    2. `test_add_length_mismatch_raises` —— 2 个 chunk + 1 个 vector → `ValueError(match="数量不一致")`，并断言 `len(store) == 0`（抓「先 extend 再校验」，会留下半条数据且不报错）
    3. `test_add_dim_mismatch_raises` —— 先 add 二维再 add 三维 → `ValueError(match="维度不一致")`，并断言 `len(store) == 1`、原数据仍能检索（**抓「先 vstack 再校验」**：抛错时矩阵已被拼成 `(2,3)`，状态脏了但没报错）
    4. `test_search_on_empty_returns_empty` —— 空库 `search` 返回 `[]`；空库 `_dim == 0`，所以这条同时守「提前返回必须在维度校验之前」
    5. `test_top_k_larger_than_size` —— 3 条数据 `top_k=5` → 返回 3 条且顺序不变（`[:top_k]` 的切片语义；弱测试，属回归保险，不追求它能抓 bug）
  - 用 `match=` 而非裸 `pytest.raises(ValueError)`：删掉校验后代码可能崩在 `np.asarray` 上抛别的 `ValueError`，只判类型区分不出「有没有校验」
  - **首次跑红 2 条，是期望值错不是代码错**：实际 `['A','C','B']`、期望写成了 `['A','B','C']`。手算点积 A=1.0 / C=0.7 / B=0.0，实际顺序才对；判断链照旧「实际值是否合理 → 回看实现有没有对应处理 → 再决定改哪边」
  - **未覆盖（可补）**：① `add` 累积成功的路径——唯一走到 `np.vstack` 的用例在校验阶段就抛了，「第二批拼进矩阵后行仍与 chunk 对齐」零覆盖；补 `add([A]) + add([B,C])` 后断言 `["A","C","B"]`，把 `vstack` 参数顺序调反才会红 ② 非空库 `top_k=0` → `[]`
  - 遗留小瑕疵：`test_add_length_mismath_raise` 名字里 `mismath` / `raise` 是笔误（应为 `mismatch` / `raises`）；`CHUNK_B` 与 `CHUNK_C` 的 `line_start` 都是 10（当前只用 `heading` 区分，改 C 为 20 更省未来的事）
- **A5 前置完成：`providers/embedding.py`（2026-11-23）**：
  - 契约：`embed(texts: list[str]) -> list[list[float]]`，**第 i 个向量对应 `texts[i]`**，顺序是契约的一部分（破了不报错，只是「B 的内容配上 A 的向量」）
  - 放 `providers/` 不放 `core/`：网络只出现在 `providers/`，`core/` 保持纯逻辑、离线可测（见第 4 节决策）
  - `BATCH_SIZE = 32`：由 L0 限流决定（RPM 2000 / TPM 500,000，单条 ≤ 8K token；切块 800 字符 ≈ 1200 token，一批约 3.8 万 token）；常量不做成参数，调用方没有按场景改它的理由
  - `_client: OpenAI | None` + `_get_client()` 惰性 + `global`：`OpenAI(...)` 会建连接池，立刻执行就等于 import 本模块就付这份开销；不做成单例类，因为本模块无状态
  - 循环用 `range(0, len(texts), BATCH_SIZE)` + 切片：最后一批天然短，切片越界不报错；`enumerate(start=1)` 只服务报错文案（「第 2 批」能直接定位 `texts[32:64]`）
  - **三处校验**：① 批内 `len(response.data) == len(batch)`——少一条会让后续所有向量整体错位一格，放 append 之前 ② 逐条 `len(vector) == settings.dim`——换模型忘改 `dim` 时立刻炸（比默默存 768 维安全） ③ 末尾 `len(vectors) == len(texts)`——唯一声明「输出条数 = 输入条数」的地方，将来有人 `except: continue` 跳过失败批次时只有它报警
  - 顺序取 `response.data` 的自然顺序，**不按 `Embedding.index` 排序**：`index` 只是回显，自然顺序才是协议承诺
  - `if not texts: return []`：`input=[]` 大概率 400，且无意义往返
  - 无 `try/except`：401 / 400 / 429 原样抛出，否则 A5 只会看到「检索质量差」而非真实原因；重试/退避留给 C 阶段或不做
  - **不做 L2 归一化**：留给 B2 与 `search` 一起改（否则 `min_score` 阈值失去可比性，且换模型时会误以为已处理）
  - 网络层不写正式测试：靠 A5 真机 spike 验证（`embed([]) == []`、单条结果与多条结果的第一条 `approx` 相等——后者能抓批边界错位，只验 `len` 验不出来）
- **遗留问题（不阻塞进 Phase 4）**：
  1. `/clear` 只清内存不清库，清完继续聊会接着原 `seq` 往后排；建议改成「顺带 `create_session` 换新会话」
  2. `load_session` 名字与返回值（`list[Message]`）不匹配，将来加「读会话元信息」时统一改名
  3. `list_sessions` 未实现，做「选择 / 切换会话」时再加
  4. 裁剪历史必须按“轮”切（以 `Role.USER` 为界）：按条数切会在 `assistant(tool_calls)` 与 `tool` 之间断开，产生孤儿消息、请求直接 400
  5. `messages` 表没有时间戳列，做会话列表时无法按“最近活跃”排序（Phase 7 前再说）
- **未验证的代码分支（3.5 这批没覆盖到，需伪造 provider 才能测）**：`MAX_TOOL_ROUNDS` 超限退出、`_run_turn` 的 `except → del messages[start:]` 回滚路径
- **阻塞项**：无。**`api.deepseek.com` 在校园网下 TCP 不可达（WinError 10060）**，需用手机热点，或把 `.env` 的 `CHAT_BASE_URL` 换成硅基流动 `https://api.siliconflow.cn/v1`
- **Phase 4 前置验证已完成（2026-11-12）**：`scripts/probe_embedding.py` 跑通硅基流动 embedding——`api.siliconflow.cn` 在校园网下**可达**（与 DeepSeek 不同），`BAAI/bge-m3` 免费（¥0.000000/K tokens，标签 `free-embedding/reranker-model.online.input-tokens`），返回 1024 维
  - 实测分数：语义相关的两句 cosine **0.714**，无关两句 **0.353** —— 说明「无关」基线不接近 0，`min_score` 阈值起点取 **0.4~0.45**（取 0.2/0.3 等于不过滤，取 0.6+ 会误杀相关块）；真值待 C3 用真实语料再调
  - 服务限制（影响批处理与切块）：单条输入上限 **8K token**（`max_chars=800` 约 1200 token，安全，但硬切逻辑出 bug 造出巨块会直接 400）；L0 级别 **RPM 2000 / TPM 500,000** → 批大小 32 合适，建索引用「总 token ÷ 50 万 = 最少分钟数」估算耗时，慢不等于卡死
  - 首次跑失败的坑：`EMBEDDING_API_KEY` 仍是模板值 `your-siliconflow-key`（**长度正好 20**），pydantic 校验能过、一路传到服务器才 401。排查时先打 `len(key)` 与前后几位的 `repr`
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
- `@dataclass(forzen=True)` 拼错 → 装饰器没生效 → 连锁报「重载不匹配」「字段未初始化」「装饰器遮蔽类型」共 6 条。**三个相同结构里只有一个报错时，差异就在那一处**
- `dict.get(k)` 返回 `V | None`，不要手写注解成 `V`（`tool: str = TOOLS.get(name)`）；注解写错会向下传播，后面全红。不确定类型时**先不写注解**
- 参数名语义错位比类型错误更坑：`execute_tool(tool: str, ...)` 里参数其实是“工具名”，应叫 `name`，否则读代码的人以为传的是对象
- **JSON Schema 的 `"type"` 拼成 `"type:"` 不会报错**，本地测试也发现不了（`execute_tool` 走的是 `func`，不碰 `parameters`），直到发给模型才暴露：模型不知道参数结构、死活不调用该工具
- `function` 拼成 `fuction`（`"type"` 的值和外层键各错一处）与上一条同类：`cast` 零运行时检查、`ruff` 也查不出，只有离线 `json.dumps` 打印一眼能发现。**改完协议结构先打印序列化结果**
- **`cast` 是类型担保不是转换**：运行时原样返回、零检查，写错了当场不报，要等很久以后才炸。用之前先用 `isinstance` 验掉能验的部分
- **F841「赋值给未使用变量」先别删赋值**：多半是漏了下游消费代码（比如漏了 `yield Done(finish_reason=...)`）。用 `--unsafe-fixes` 改成 `pass` 会让功能静默失效、且不报任何错
- 给返回值标 `Any` 消红最贵：`execute_tool` 明明是 `-> str`，标成 `Any` 会让 `Message(content=...)` 一并变成 Unknown，一路污染。**补 import 修根因**才对
- 少了逗号（`parameters={...}` 后直接换行写 `func=`）会引发 SyntaxError，导致整块代码被标红——**报错的行号常常在真正出错处的下一行**
- **SQLite 的连接配置不跨连接继承**：`PRAGMA foreign_keys = ON`、`row_factory` 只作用于当前 connection 对象，`close()` 后归零。所以「init 时设一次就完事」不成立，每条新连接都得设一遍——这就是把它们收进 `_connect()` 的原因
- **「必须先 init 再 connect」是误解**：`CREATE TABLE` 是 DDL 写进 `.db` 文件，持久存在，之后任何连接都能看到表。失效的只是连接配置，不是表结构
- **`git mv` 报 `fatal: bad source, source=...`** = 源文件在磁盘上已不存在（改名早做过了 / 路径写错），不是「git 不跟踪这个文件」。先 `git status --short` 看状态
- **改名成功的标志是状态里的 `R`**（rename），不是 `D` + `A`。git 按内容哈希存对象、文件名只是索引，`git mv` 后能自动识别，`git log --follow` 可穿透改名追溯历史
- `cur.lastrowid` 类型是 `int | None`（只有新增行才有值），basedpyright 会报；写 `int(cur.lastrowid or 0)` 比 `cast` 稳（**写 `create_session` 时就会碰到**）
- `datetime.utcnow()` 已废弃且返回 **naive** 时间；统一用 `datetime.now(UTC).isoformat(timespec="seconds")`，这样 `datetime.fromisoformat()` 能原样解析回来，也不会混进本地时区
- **单元素元组必须写 `(x,)`**：逗号才是元组的标志，`(x)` 只是括号。`conn.execute(sql, 5)` 报 `Parameters are of unsupported type`；更坑的是传字符串——`conn.execute(sql, "abc")` 会被逐字符拆成 3 个参数，报 `The current statement uses 1, and there are 3 supplied`
- **`fetchone()` / `fetchall()` 在 typeshed 里返回 `Any`**（`row_factory` 可换，类型无法静态确定），所以 `row["col"]` 全是 `Any`，会连带报一片 `reportAny`。给 `row` 加注解也没用（`Row.__getitem__` 同样返回 `Any`）——**这是库的类型洞，别为消警告写畸形代码**
- **关键字实参少一个逗号会报「括号未闭合」**：`tool_calls=... else None` 后面漏逗号直接接下一行 `tool_call_id=...`，basedpyright 报的是 `[` 未闭合、`(` 未闭合，还连带「rows 未使用」「返回类型未知」。**报错位置在真正出错处的上一行，先看上一行行尾**
- **长 SQL 超 `line-length = 100` 分行时用 `+` 显式拼接**：隐式拼接（相邻字符串）会掩盖「少逗号」这类 bug，basedpyright 报 `reportImplicitStringConcatenation`；拼接处空格要自己补，`"…FROM messages"` + `" WHERE…"` 两边只留一个，都漏会拼成 `messagesWHERE`
- **`list` / `dict` 是「不变（invariant）」的**：字面量 `[... {"id": "x"}]` 会被推断成 `list[dict[str, str]]`，赋给 `list[dict[str, object]]` 会报不兼容（`dict[str, str]` 不是 `dict[str, object]` 的子类型，因为 dict 可变、放行等于允许往里塞任意对象）。**修法是给变量显式标注宽类型，不是 `# type: ignore`**（写测试常量 `TOOL_CALLS` 时就会碰到）
- **`pyproject.toml` 的数组引号没闭合不会给你好脸色**：`testpaths = ["tests]` 少一个 `"` → TOML 解析直接 `unterminated string`，`uv` 的任何命令（包括 `uv run pytest`）都起不来，报错行号却指在这行，容易误以为是 pytest 配置项写错
- **断言缩进掉进 `for` 循环 = 必挂**：循环 3 次却要求某时刻已有 3 条记录，第一次迭代就 `assert [1] == [1,2,3]` 失败。这类错误的报错信息本身就带 diff（左右值都打印），**先看是「值不对」还是「时机不对」**——`assert` 位置错了时，值往往只差一个元素
- **常量名拼错，只要定义和使用错成同一个串就不会报错**：`DEFFAULT_MAX_CHARS` / `DEFALUT_MAX_CHARS` 这类错误，单文件内完全自洽，代码照跑；暴露的时机是「别处 `from ... import DEFAULT_MAX_CHARS`」，而那时你已经忘了当初怎么拼的。**常量比变量更该核对拼写，因为它注定被跨文件引用**。同理 `max_char` / `max_chars` 单复数不一致，会让 `max_chars=2000` 这种关键字调用直接 `TypeError`
- **`@dataclass` 漏 `frozen=True` 不会报错**：纯数据类会变成可变、且 `__hash__` 为 `None`——下游改了 `text` 却不改 `heading`（两者不再一致，且不报错），也不能放进 `set` 或当 dict key。`Tool` 和三个事件类都是冻结的，纯数据类照做
- **正则量词是 `{m,n}`，用逗号不是点**：`r"^#{1.6}$"` **不会抛异常**——`{1.6}` 不是合法量词语法，被当作字面字符 `{1.6}`，正则永远匹配不到 `###`，过滤逻辑静默失效。`ruff` / 类型检查都抓不到，只能靠「改完立刻用真实数据验证行为」（跑 `dump_chunks.py` 看第 61 块还有没有 `###`）
- **`for piece in ...:` 循环体里却用 `body`**：变量名相近时极易写错，表现是「块数正确、`ruff` 干净、不报错，但每块内容完全一样且都超长」。抓它的唯一办法是**给输出加一条不变量断言**（每块长度 ≤ 上限 / 块内容不重复），而不是靠眼睛扫一遍。同理 `max_char` / `max_chars` 这类单复数差异也属于同一类
- **条件表达式只改了一个分支**：`f"{heading}\n{piece}" if heading else body` —— 主分支从 `body` 改成 `piece` 了，`else` 分支还留着 `body`。因为「无标题块」在真实文档里几乎不出现（`DEVLOG.md` 顶部有 `# 开发日志`，栈永远非空），跑 `dump_chunks.py` 完全看不出来。**改三元表达式时，两个分支都要逐个确认**；这类 bug 只能靠专门构造「无标题 + 超长」的测试来抓
- **测试红了，先分清是代码错还是期望值错**：判断链是「实际值是否合理 → 回看实现里有没有对应的处理 → 再决定改哪边」。实测踩过的例子：期望 `"Day4\n- 今天没做什么\n"`，实际 `"Day4\n- 今天没做什么"`——因为 `flush()` 里 `body` 过了 `.strip()`，**实际值才是对的**，该改的是期望值。反过来看 `assert [1] == [1,2,3]` 那种，实际值明显是半成品，那才是代码错
- **`np.float32` 算出来的分数不能用 `==` 比**：`float(np.float32(0.7))` 是 `0.699999988079071`，`assert score == 0.7` 必红且看不出原因。凡是经过 numpy 的浮点都要 `pytest.approx`（测试里 C=`[0.7,0.7]` 正好撞上）
- **IDE 的红波浪不等于仓库工具链的红**：IDE 报 `np.vstack` 重载不匹配、实参类型 `list[NDArray | _Array2D[floating[_32Bit]]]`，而 `uv run --with basedpyright basedpyright`（1.40.2，numpy 2.2~2.5.5 全试过）是 **0 error**——两边解析的 numpy stub 不是同一份（`_Array2D` 是形状特化别名，只在某些版本出现）。判断顺序：先确认 IDE 解释器指向 `.venv\Scripts\python.exe`，再用命令行版复核，别照着 IDE 的红波浪改代码
- **`np.vstack([a, b])` 的元素类型不一致时泛型推不出来**：`vstack[ScalarT](tup: Sequence[_ArrayLike[ScalarT]])` 要求整个列表的标量类型统一。给 `matrix` 加显式标注 `NDArray[np.float32]`（与 `_matrix` 同型）后列表变成单一类型，报错消失；这也是「显式标注宽类型」比 `# type: ignore` 好的地方

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
- **写入语句被多缩进一层掉进 `elif` 分支**（`vector_store.add`）：`self._matrix = ...` 和 `self._chunks.extend(...)` 缩进了 4 个空格，恰好落进 `elif dim != self._dim:` 的块里。因为首次 `add` 走的是 `if self._dim == 0` 分支，那两行永远不执行 → `len(store)` 恒为 0，且零报错。**`if / elif / else` 之间夹带无关语句时，先确认缩进层级**；能靠 `print(len(...))` 发现，说明「先暴露状态再查原因」比逐行读代码快
- `while True` 里 `break` 之后，循环**外面**的代码会执行一次（不是“永不执行”）；判断命令必须在 `messages.append` **之前**，否则命令文本会被发给模型
- `/clear` 要用 `del messages[1:]`（保留 index 0 的 system），写成 `messages = []` 只改局部引用、`clear()` 会把人设一起删掉
- `stream=True` 只改变**响应**方式（SSE 分块），请求体始终是整包，模型无状态、每轮都要重发全部历史
- `python.analysis.extraPaths` 是 Pylance 的设置，basedpyright 不读它（本项目靠 editable 安装的 `.pth` 解决导入）
- **空行归 formatter，不归 linter**：`ruff check` 不报空行（`E302`），但 `ruff format` 会修。流程永远是 `ruff check --fix .` **再** `ruff format .`，只跑一个会漏
- PEP 8 空行只有一句：**顶层定义之间 2 行，类内成员之间 1 行**；文件末尾必须有一个换行符（否则 git diff 出现 `\ No newline at end of file`）
- `_collections_abc` 是 CPython 私有模块（`collections.abc` 的底层实现），编辑器自动补全常推荐它，**不要用**
- 事件对象统一 `@dataclass(frozen=True)`：事件是“已发生的事实”，不可变可以防住“有人中途改掉 finish_reason 导致错误被静默吞掉”

