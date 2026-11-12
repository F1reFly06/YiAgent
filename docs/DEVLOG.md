# 开发日志

## 2026-10-27 Day1 项目初始化

### 做了
- 补gitignore,忽略了.env，.idea/
- 钉Python版本到3.12 （cli：uv python pin 3.12）
- uv sync让环境和版本一致
- 补了docs/PROJECT.md,项目总览
- .env.example (相当于env的模板，公开到仓库的，CHAT*为deepseek，embedding*为硅基流动)
- `pyproject.toml`：`openai` / `rich` / `pydantic-settings` / `typer` 四个运行时依赖；`ruff` 单独进 dev 组
- 配了 `[tool.ruff]`（行宽、目标版本）和 `[tool.ruff.lint]`（`select` 规则集）


### 决策
- Python 用 3.12 而不是本机的 3.14：3.14 太新，带 C 扩展的库还没预编译包，
  装库会触发本地编译而在 Windows 上失败
- `.python-version` 要提交进 git，保证本机和以后的 CI 用同一个解释器
- 依赖用 uv add 而不是手写 dependencies：让工具负责版本解析和 lock 更新
- ruff 进 dev 组而不是运行时依赖：部署时 uv sync --no-dev 可以跳过它
- requires-python 收紧成 >=3.12,<3.13：只承诺测过的版本
- authors 换成 GitHub noreply，避免 QQ 号公开

### 想明白的
- `.gitignore` 只对「未跟踪」的文件生效；已提交过的文件要 `git rm --cached` 才能停止跟踪
- `.idea/` 是 IDE 的项目配置目录，含本机绝对路径，删了不影响代码，PyCharm 会自己重建
- 任意子目录都可以有 `.gitignore`，规则对所在目录及其子目录生效

### 踩坑
- Markdown 的 `#` 后必须有空格，否则不渲染成标题
- 长文档粘贴后要按 `Ctrl+End` 检查末尾，`PROJECT.md` 第一次就断在第 7 节

## 2026-10-28 Day2 收尾Phase 0 + 起步 Phase 1

### 做了
- 完成 Phase 0：`LICENSE`(MIT)、`pyproject` 的 `license` / `license-files` / `[project.urls]`、`README`
- 首次提交 `70a2a2a` 并推送到 GitHub（SSH）
- 配好 Ruff 编辑器扩展 + `.vscode/settings.json`（解释器、src 路径、保存即格式化）
- 写了`src/yiagent/config.py`: 引入`pydantic_settings`里的`BaseSettings`，自己新建两个子类分别读取`CHAT_*`和`EMBEDDING_*`的环境变量
- 写了src/yiagent/core/message.py: 定义了枚举'Role`和`Message`类（和Message类下的to_dict()方法)`，这个message.py的作用是数据契约和转换层，将传进来的数据转换为message定义的数据，变成Message类的对象。

### 决策
- 密钥字段用 `SecretStr` 而不是 `str`：打印显示 `**********`，日志和截图里不会泄露
- 消息用 `dataclass` 而不是 pydantic：内部构造的数据不需要重校验，更轻
- `tool_calls` 用 `list[dict[str, object]]` 而不是 `Any`：basedpyright 禁止显式 `Any`，`object` 语义已够
- `to_dict()` 只输出有值的字段：普通消息带 `tool_calls: null` 会被 API 拒绝

### 踩过的坑
- `.env` 只认 `KEY=VALUE`，写成冒号这一行会被忽略，字段读不到
- - PowerShell 的 `Get-Content` 默认按 GBK 解码，看 UTF-8 中文要加 `-Encoding UTF8`

## 2026-10-29 Day3 继续做Phase 1

### 做了
- 写了`src/yiagent/core/llm.py`: 这个文件主要是声明接口形状，创建了一个LLMProvider（一个Protocol（协议类）），让providers继承，前者（llm.py不做任何实现，只做声明，后者providers做具体实现）。
- 写了`src/yiagent/providers/openai_compat.py`: 这个文件是具体实现，继承了LLMProvider，并实现了它，同时也是接触网络的地方。所写类下，__init__是对client的初始化，传入apikey和baseurl，这些都是构建一次反复使用的，所以写入init；建client，这相当于是本地请求的发送端，是发送请求给模型供应商的。stream方法拆开看，`response = self.client.chat.completions.create（）`是发送请求后得到的返回内容的经过处，chunk就是经过response的产物，然后content是对chunk的提取，作为最终输出结果的一部分。

### 踩过的坑
- 没有对类实例化而直接调用（config.py文件里最后两行是对类进行实例化）

## 2026-10-30 Day4

###
- 开发上没有什么进度，把概念弄懂了一下，主要是`src/yiagent/core下的llm.py和openai_compat.py`

## 2026-10-31 Day5 继续做Phase 1, 完成Phase 1

### 做了
- 写了`src/core/prompts/system.md`作为提示词单独提出来成为一个独立文件, 专门写提示词用。
- 写了`src/yiagent/prompt.py` 用于加载`src/core/prompts/system.md`的提示词，并被`src/yiagent/cli/main.py`引用。
- 写了`src/yiagent/cli/main.py`这个是今天所写的主要的内容, 也是Phase1的核心实现, 就是完成对话循环的, main.py文件中，main()函数完成provider和massages的初始化, _chat_loop函数完成输入处理，然后把输入的内容传入messages(Role:USER), 函数_stream_reply拿到messages, 其中的调用provider的stream方法, stream实现网络请求和接收返回值，_stream_reply流式打印返回值(在_chat_loop函数中被调用), 同时_chat_loop函数把这个值完整的存入messages(Role:ASSISTANT)中, 这个过程是循环体, 就是_chat_loop()所做的事情。同时_chat_loop()里也做了清理历史记录，退出，以及请求模型失败等情况的返回值。

### 想写的记录
- uv run ruff format . 格式化代码
- uv run ruff check . 检查代码
- uv run ruff check --fix . 检查代码并自动修复

## 2026-11-1 Day6 开始Phase 2
### 做了
- 首先改了接口, 原本的stream直出str改成了事件流Event(这个修改位于文件llm.py), 将模型的输出由str变为Event(目前包括TextDelta(模型输出的一小段文字), ToolCall(模型请求一次调用工具), Done(一次请求结束))
- 同步修改`src/yiagent/providers/openai_compat.py`, yield TextDelta 和循坏外yield Done
- 新建文件`scr/yiagent/core/tools.py`, 写了Tool数据结构, 写了两个工具, 写了工具注册表, 写了execute_tool(同时包括执行工具和工具使用失败抛出原因而非异常).

## 2026-11-2 Day7 继续Phase 2
### 做了
- 写了一点openai_compat.py 的代码, 主要是为工具参数发给模型做格式适配。

## 2026-11-3 Day8 继续Phase 2
### 做了
- 把昨天没写完的`openai_compat.py ` 的代码补完了，在这里具体说明。首先写了`_to_openai_tools()`: 把`TOOLS`翻译成符合openaiSDK的形式。
- 写了`_ToolCallDraft`(`openai_compat.py`里): 储存工具调用的草稿, 后面让chunk从response中提取并赋值(id,name,arguments赋值给draft, 用一个字典接收, 字典键值从0开始, draft.id对应的是response里的具体的id, 通过这个id去定位具体的工具)
- 写了`_parse_arguments`(同为`openai_compat.py`里), 作用是将模型返回的JSON格式解析为dict(), 用于后续再次发给模型, 供模型阅读调取工具。

## 想写的记录
- cast 是 typing 模块的一个函数, 作用是向静态检查器声明某个值的类型, 对应值则原封不动返回, 告诉检查器把这个值当作目标类型(cast声明的)来处理。

## 2026-11-4 Day9 结束Phase 2
### 做了
- 主要完成了`cli/main.py` 的代码, 实现命令行的完成, 同时对main.py进行了修改, 新写了一个dataclass类, 这个的作用是代替原先stream请求模型的产出物, 原先是str一段文本, 现在是_ReplyResult, 包括文本, 工具调用, 结束原因。
- 修改`_stream_reply`(`cli/main.py`), 让它不仅从能输出文本, 变为按照StreamEvent事件分流, 分别从provider.stream()中获取到TextDelta, ToolCall, Done, 分别对应文本, 工具调用, 结束原因。如果是文本则直接输出(result.text(由event.text累加而成))
- 写`_tool_call_to_dict`(`cli/main.py`), 作用是将内部ToolCall转化为协议dict(), 写回历史用。
- 写 `_run_turn`（`cli/main.py`），这是工具调用的核心流程，返回模型最终的答案文本。
  注意：工具执行结果**不从**这里返回，它是作为 `role="tool"` 消息进历史，
  等下一次请求随整份历史带给模型。（打印也归它管——它调用 `_stream_reply`。）

  设定最大轮数（`MAX_TOOL_ROUNDS = 5`）后进入循环，每一轮：
  1. 用 `_stream_reply` 发一次请求，拿回文本 / 工具调用 / finish_reason
  2. 把这一轮的 assistant 消息写进历史（有工具调用就带 tool_calls，没有就带文本）
  3. 判断要不要继续——**只有** `finish_reason == "tool_calls"` 且 `tool_calls` 非空才继续，
     其它情况（`stop` / `length` / 列表为空）一律 return
  4. 要继续时，遍历每个 ToolCall，用它的 name 和 arguments 调 `execute_tool`，
     把返回的字符串追加成 `role="tool"` 消息（带 `tool_call_id`）
  5. 回到循环顶部再请求一次，让模型看到工具结果

### 决策
- 历史必须三段式：`assistant(tool_calls)` → `tool(结果)` → `assistant(最终回答)`，
  三段不能合并。原因是模型无状态，每次请求都要把整份历史重发，服务端靠 `tool_call_id`
  把结果和调用配对
- 继续循环的条件是 `finish_reason == "tool_calls"` **且** `tool_calls` 非空。
  双条件：只判前者，遇到“声称要调工具但列表为空”会空转 5 轮
- 工具结果不是单独“发”给模型的，只是 append 进 `messages`，等下一次请求随整份历史带过去
- 最大轮数 5 轮，超限不抛异常（历史此刻是合法的，下一轮还能用）
- 异常时 `del messages[start:]` 回滚本轮追加的全部消息，`_chat_loop` 再 `pop()` 掉用户消息，
- `_stream_reply` 的返回值从 `str` 改成 `_ReplyResult`（text / tool_calls / finish_reason）。
  原因不是“字段变多了”，而是一次请求的产出**自带意图**：text 给用户看，tool_calls 用来执行，
  finish_reason 用来判断要不要再请求一次。如果只返回 str，`_run_turn` 就只能靠“文本是否为空”
  猜——而“模型不说话只调工具”“请求出错返回空”“内容被过滤”这三种情况在 str 里无法区分。
  这和 provider 层 `Iterator[str]` → `Iterator[StreamEvent]` 是同一种演进：从单一值变成复合值


## 2026-11-5 Day10 开始Phase 3
### 做了
-建`src/yiagent/core/session_store.py`, 这个文件主要是承担建库的任务, 今天写了一部分, 首先是写出数据库的结构, session 和 message, 两个表。两个方法, 一个连接方法connect, 一个建库方法init_db。跑通了测试。

### 决策
- schema 写成py文件而不是sql, 因为py相比于sql规模小, 省去了打包配置。
- 加 `seq` 列表达会话内顺序，不复用 `id`(id 只是物理标识)

## 2O26-11-6 Day11 休息一天orz

## 2026-11-7 Day12 继续Phase 3
### 做了
- 写了`src/yiagent/core/session_store.py`的一个方法, create_session, 这个方法是创建一个会话, 并返回会话的id。参数化INSERT进入本地数据库。

## 2026-11-8 Day13 继续Phase 3
### 做了
- 写了`src/yiagent/core/session_store.py(append_message)`, `src/yiagent/core/session_store.py(load_session)`两个函数, 前者的作用是当一轮对话结束, 把这一轮的消息存入数据库做本地持久化保存。后者的作用是读取数据库的对话历史数据, 用seq顺序加载对话历史,是对话开始的初始化的最后一步(目前所写的内容)。

### 注意事项
- 长 SQL 超 100 字符（`line-length = 100`）分行写时，用 `+` 显式拼接，不要用相邻字符串的隐式拼接——隐式拼接会掩盖「少逗号」这类 bug（两个字符串被静默连成一个），basedpyright 也会报 `reportImplicitStringConcatenation`；另外拼接处的空格要自己补，`"…FROM messages"` + `" WHERE…"` 两边只留一个空格，都漏会拼成 `messagesWHERE`。`+` 拼接在编译期折叠成常量，运行时零开销

## 2026-11-9 Day14 完成Phase 3
### 做了
- 完善`src/yiagent/core/session_store.py`, 补全最后一个函数lastest_session, 用于调取最近一次的会话。
- 修改`src/yiagent/cli/main.py`, 新写函数save_new_messages, 用于本轮对话结束后将新增消息存入sql, 修改run_turn, 让在`src/yiagent/core/session_store.py`写的函数在cli中生效, 包括写入数据库, 读取数据库等。

## 2026-11-11 Day15 写测试文件
### 做了
- 写测试文件tests/test_session_store.py, 目前用于测试session_store.py的功能。也是后续做的本地测试用例。

## 2026-11-12 Day16 开始Phase 4
### 做了
- 写了`scripts/probe_embedding.py`, 用于测试embedding探针结果, 跑通embeddingAPI调用
