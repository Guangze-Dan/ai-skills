# AGENT.md — AI Agent 使用说明

本仓库是用户的个人 skills 统一真源。若你的运行环境中已接入这些 skills（`~/.zcode/skills`、`~/.agents/skills`、`~/.claude/skills`、`~/.codex/skills` 下的 junction），直接按常规方式调用即可，无需关心本仓库。

## 给 agent 的规则

1. **查找 skill**：先读 `registry.json` —— 每条含 `name`（frontmatter 名）、`dir`（仓库路径）、`description`（触发条件与用途）。按用户意图匹配 `description`。
2. **读取 skill 正文**：`skills/<dir-name>/SKILL.md`。`SKILL.md` 内引用的 `references/`、`scripts/`、`assets/` 均在该 skill 文件夹内按相对路径取用。
3. **不要修改 skill 文件**，除非用户明确要求改进 skill 本身；改完在仓库内 git commit。
4. **新增 skill**：在 `skills/` 下新建文件夹并写 `SKILL.md`（frontmatter 至少含 `name`、`description`），然后 `powershell tools/gen_registry.ps1` 更新索引，git commit + push。
5. **`.system` 不在本仓库**（Codex 系统技能，勿动）。
6. 自动化脚本在 `scripts/`，多为 Windows PowerShell，标注了用途；调用前按脚本头部注释确认参数与环境。

## 嵌套此仓库的项目

项目里以子模块方式接入（`.ai-skills/`）时，上述路径前缀加 `.ai-skills/`，其余规则相同。
