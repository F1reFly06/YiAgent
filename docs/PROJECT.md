# YiAgent 项目总览

> 最后更新：2026-11-11 · 当前阶段：Phase 3 ✅ 与过渡任务 3.5（pytest）✅ 均已完成，下一步进 Phase 4（RAG 入库与检索）
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
| 4 | RAG 入库与检索 | 未开始 |
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
src/yiagent/providers/openai_compat.py  OpenAIChatProvider：唯一碰网络的地方，产出事件流
src/yiagent/cli/main.py       typer + rich 入口：main(建表/续接会话/载历史) + _chat_loop / _run_turn(带 session_id, 结束写库) / _save_new_messages / _stream_reply

tests/test_session_store.py  持久化层测试：db fixture(tmp_path 临时库) + _seqs() 直查 helper + 6 个用例
```

Phase 2 完成（2026-11-04）：工具调用闭环打通。provider 侧 `tools=` + 按 `tc.index` 分桶累积 `tool_calls` + 循环外先 `ToolCall` 后 `Done`；CLI 侧 `_run_turn` 工具轮次循环（开关是 `finish_reason == "tool_calls"` **且** `tool_calls` 非空）、三段式历史、`MAX_TOOL_ROUNDS = 5`、异常时 `del messages[start:]` 回滚。

Phase 3 完成（2026-11-09）：会话持久化闭环打通。`session_store` 六个函数齐全（`_connect` / `init_db` / `create_session` / `latest_session` / `append_message` / `load_session`）；`main()` 启动流程 `init_db → latest_session（为 None 才 create_session）→ load_session → [system, *history]`；`_run_turn` 带上 `session_id`，在 `finally` 里把 `messages[start:]` 逐条落库（失败时该切片已被 `del` 清空，天然不写）。端到端验收：**同一进程内、以及退出重开后，都能答出「我是任旭阳」**。
表结构 `sessions(id, created_at, title)` / `messages(id, session_id, seq, role, content, tool_calls, tool_call_id)` + 索引 `idx_messages_session_seq`；`_connect()` 统一做 `PRAGMA foreign_keys = ON` 和 `row_factory = sqlite3.Row`。

Phase 3.5 完成（2026-11-11）：持久化层补上测试护栏。`tests/test_session_store.py` 6 个用例全绿（`6 passed in 0.13s`），覆盖往返保真、`None` / `[]` 边界返回值、`seq` 自增与按会话独立、外键约束生效；`pyproject.toml` 新增 `[tool.pytest.ini_options]`（`testpaths = ["tests"]` + `pythonpath = ["src"]` + `addopts = "-q"`）。

## 8. 下次接着干的入口

- **当前在**：**Phase 3 ✅ + Phase 3.5（pytest）✅ 均已完成**（2026-11-11）。持久化闭环已有测试护栏：6 个用例覆盖「往返保真 / 空库与空会话的边界返回值 / `seq` 自增与按会话独立 / 外键约束真生效」
- **下次第一件事**：进 **Phase 4（RAG 入库与检索）**。先只定接口与数据结构（切块函数签名、`core/vector_store.py` 的 add/search、embedding 调用位置），再动手写实现；Phase 4 的拆分步骤下次开工时先补进本节
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
- **遗留问题（不阻塞进 Phase 4）**：
  1. `/clear` 只清内存不清库，清完继续聊会接着原 `seq` 往后排；建议改成「顺带 `create_session` 换新会话」
  2. `load_session` 名字与返回值（`list[Message]`）不匹配，将来加「读会话元信息」时统一改名
  3. `list_sessions` 未实现，做「选择 / 切换会话」时再加
  4. 裁剪历史必须按“轮”切（以 `Role.USER` 为界）：按条数切会在 `assistant(tool_calls)` 与 `tool` 之间断开，产生孤儿消息、请求直接 400
  5. `messages` 表没有时间戳列，做会话列表时无法按“最近活跃”排序（Phase 7 前再说）
- **未验证的代码分支（3.5 这批没覆盖到，需伪造 provider 才能测）**：`MAX_TOOL_ROUNDS` 超限退出、`_run_turn` 的 `except → del messages[start:]` 回滚路径
- **阻塞项**：无。**但注意 `api.deepseek.com` 在校园网下 TCP 不可达（WinError 10060），需用手机热点，或把 `.env` 的 `CHAT_BASE_URL` 换成硅基流动 `https://api.siliconflow.cn/v1`**
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
- **空行归 formatter，不归 linter**：`ruff check` 不报空行（`E302`），但 `ruff format` 会修。流程永远是 `ruff check --fix .` **再** `ruff format .`，只跑一个会漏
- PEP 8 空行只有一句：**顶层定义之间 2 行，类内成员之间 1 行**；文件末尾必须有一个换行符（否则 git diff 出现 `\ No newline at end of file`）
- `_collections_abc` 是 CPython 私有模块（`collections.abc` 的底层实现），编辑器自动补全常推荐它，**不要用**
- 事件对象统一 `@dataclass(frozen=True)`：事件是“已发生的事实”，不可变可以防住“有人中途改掉 finish_reason 导致错误被静默吞掉”

