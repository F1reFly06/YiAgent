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