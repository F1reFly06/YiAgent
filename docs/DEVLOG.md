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