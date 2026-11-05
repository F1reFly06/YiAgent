# YiAgent 项目总览

> 最后更新：2026-11-05 · 当前阶段：Phase 3（会话与持久化）进行中
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
| 2 | **工具调用循环 ★** | ✅ 已完成（2026-11-04） |
| 3 | 会话与持久化 | 🔨 进行中（2026-11-05 开始，Day10） |
| 4 | RAG 入库与检索 | 未开始 |
| 5 | **检索变成工具 ★** | 未开始 |
| 6 | 评测集 | 未开始 |
| 7 | Web + 部署 | 未开始 |

★ = 核心竞争力，其余是支撑。**第 4 周末**即可在简历上写第一段（Phase 0–2）。

实际进度：Phase 0–1 用 5 天完成（2026-10-27 ~ 10-31），Phase 2 用 4 天完成（11-01 ~ 11-04），共 9 天走完前置三个阶段，比排期（4 周末完成 Phase 0–2）提前约 2 周。

Phase 2 内部三步：① 事件流接口 ✅ ② 工具定义与执行 ✅ ③ provider 接工具 + CLI 工具循环 ✅。

Phase 3 从 2026-11-05（Day10）开始，当天完成建表 + 三个读写函数骨架，尚未接入 `cli/main.py`。

但后半程难度更高（RAG 的召回质量、评测集设计），**不要按前半程速度外推**。

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

data/yiagent.db           本地 SQLite 库（运行产物，已在 .gitignore，不进 git）
src/yiagent/__init__.py   空（脚手架残留的 main() 已删）
src/yiagent/config.py     两个 BaseSettings 子类 + 模块级单例 chat_settings / embedding_settings
src/yiagent/core/message.py   Role 枚举 + Message dataclass + to_dict()
src/yiagent/core/llm.py       LLMProvider 协议 + 三个事件（TextDelta / ToolCall / Done）
src/yiagent/core/tools.py     Tool 数据结构 + 两个示例工具 + TOOLS 注册表 + execute_tool
src/yiagent/core/prompt.py    load_system_prompt()，importlib.resources + lru_cache
src/yiagent/core/session_store.py  会话持久化：_SCHEMA（sessions / messages）+ _connect + init_db；**全项目唯一写 SQL 的地方**（create_session / append_message / load_messages 待写）
src/yiagent/prompts/system.md 系统提示词（人设 / 能力边界 / 风格 / 不编造）
src/yiagent/providers/openai_compat.py  OpenAIChatProvider：唯一碰网络的地方，产出事件流
src/yiagent/cli/main.py       typer + rich 入口：_chat_loop / _run_turn / _stream_reply 三层 + main 装配
```

Phase 2 完成（2026-11-04）：工具调用闭环打通。provider 侧 `tools=` + 按 `tc.index` 分桶累积 `tool_calls` + 循环外先 `ToolCall` 后 `Done`；CLI 侧 `_run_turn` 工具轮次循环（开关是 `finish_reason == "tool_calls"` **且** `tool_calls` 非空）、三段式历史、`MAX_TOOL_ROUNDS = 5`、异常时 `del messages[start:]` 回滚。

Phase 3 进行中（2026-11-05 起）：`core/session_store.py` **只有建表这一层**（`_SCHEMA` + `_connect` + `init_db`），读写函数（`create_session` / `append_message` / `load_messages`）尚未写，也未接入 CLI。表结构 `sessions(id, created_at, title)` / `messages(id, session_id, seq, role, content, tool_calls, tool_call_id)` + 索引 `idx_messages_session_seq`；`_connect()` 统一做 `PRAGMA foreign_keys = ON` 和 `row_factory = sqlite3.Row`。

## 8. 下次接着干的入口

- **当前在**：Phase 3（会话与持久化）进行中，**卡在「建表已完成，读写函数未写」这一步**。`core/session_store.py` 只有 `_SCHEMA` / `_connect` / `init_db`，能建库建表，但不会写也不会读一条数据
- **明天的第一件事**：写 `create_session()` —— 只写这一个函数，写完 review 再继续 `append_message`
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
- **`create_session` 的设计已定（明天照着写，接口层）**：
  - 签名 `create_session(db_path: str, title: str | None = None) -> int`
  - 传 `db_path` 不传 `conn`：与 `init_db` 一致，函数自己管连接，避免「该谁 commit」的歧义
  - 返回 `int`（新会话 id）而不是 `Session` 对象：现阶段调用方只要一个数字，等做 `list_sessions` 时再引入 dataclass
  - 函数体四步：`_connect()` → 参数化 `INSERT INTO sessions (created_at, title) VALUES (?, ?)` → `commit()` → `return int(cur.lastrowid or 0)`
  - `created_at` 必须显式给值（`NOT NULL`），取 `datetime.now(UTC).isoformat(timespec="seconds")`，import 是 `from datetime import UTC, datetime`
- **三个已定的小决定**：
  1. 时间不用 `datetime.utcnow()`（已废弃且返回 naive），也不用 SQLite 的 `CURRENT_TIMESTAMP`（无时区、空格分隔，和 ISO 8601 不统一）
  2. 不用 `with sqlite3.connect(...) as conn`：那是**事务上下文**，退出时 commit 但**不关闭连接**
  3. 表不存在就让 `sqlite3.OperationalError: no such table` 报出来，不在 `create_session` 里隐式调 `init_db`；建表归启动装配阶段管
- **Phase 3 后续顺序**：`create_session` → `append_message`（`seq` 取 `COALESCE(MAX(seq),0)+1`）→ `load_messages`（`ORDER BY seq`、`role` 转 `Role`、`tool_calls` 走 `json.loads`）→ 接入 `main.py` 三行（`init_db` → 建/取会话 → `load_messages` 结果直接当 `messages`）
- **仍待定**：「继续上次会话」走 `latest_session()` 自动续（`ORDER BY id DESC LIMIT 1`）还是 CLI 参数 `--session <id>`；写时机仍是「`_run_turn` 成功后写 `messages[start:]`，失败已回滚、天然不写」
- **函数数量与原计划的偏差**（有意为之）：`append_messages`（批量）改成 `append_message`（单条），`load_session` 拆成 `load_messages` —— 逐条写可以边聊边存，不必等一整轮结束；`list_sessions` 暂缓，等真需要「会话列表 / 继续上次」时再加
- **未验证的技术债**：`MAX_TOOL_ROUNDS` 超限分支、`del messages[start:]` 回滚分支从未执行过，等 Phase 3 引入 pytest 后补测
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

