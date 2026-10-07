# HANDOFF — ai-skills 统一真源系统 · 交接文档

> 给接手的 AI：本文档自包含。读完即可继续维护、扩展、排障这套系统，无需向用户追问历史背景。
> 交接时间：2026-10-07 · 交接自：ZCode 会话（用户：但光泽，GitHub: **Guangze-Dan**）

---

## 一、背景与目标

用户要求：把本机所有个人 AI skills 和历史自动化脚本整理成 GitHub 上的**唯一真源**，让所有 AI agent（ZCode / Claude Code / Codex / AGENTS 标准）直接调用；并且**今后每次任务产生的新脚本自动进仓库**，不再重复手工收集。以上均已完成并验证。

## 二、核心资产与凭据

| 项 | 值 |
|---|---|
| 本地仓库 | `D:\Zcode\ai-skills`（branch `main`，与 origin 同步） |
| GitHub | https://github.com/Guangze-Dan/ai-skills （**私有**） |
| gh 登录 | 已登录 `Guangze-Dan`，token scopes: `gist, read:org, repo`（keyring 存储） |
| git | 2.55，`C:\Program Files\Git\cmd\git.exe`（本次会话刚装，旧 shell 的 PATH 可能没有它——用完整路径或刷新 PATH） |
| gh | `C:\Program Files\GitHub CLI\gh.exe`（同理，PATH 可能未刷新） |

## 三、仓库结构

```
D:\Zcode\ai-skills\
├── skills/                 # 37 个个人 skill（skills/<name>/SKILL.md），真源本体
├── scripts/                # 自动化脚本（按主题分类 + inbox 暂存区）
│   ├── android-mtp/        #   4 个：小米 MTP/USB 驱动修复 + APK 推送
│   ├── android-ui/         #   2 个：uiautomator dump 解析
│   ├── productivity/       #   3 个：ui_mockup.py / read_schedule.py / start_zcode.bat
│   ├── legacy/             #   3 个：一次性历史脚本
│   └── inbox/<日期>/       #   钩子自动归档的新任务脚本（暂存区）
├── tools/
│   ├── gen_registry.ps1        # 重建 registry.json
│   ├── sync_task_scripts.ps1   # ★ 钩子调用的自动同步脚本
│   ├── .sync-state.json        # 同步状态（gitignore，不入库）
│   └── sync.log                # 同步日志（gitignore）
├── registry.json           # 37 个 skill 的机器可读索引（name/dir/description）
├── AGENT.md                # 给任何 AI agent 的使用规则（含自动归档约定）
├── README.md               # 中文主文档：结构/快速开始/工作流
├── install.ps1             # 一键把 skills junction 到各 agent 目录（幂等）
├── collect.ps1             # 反向收集本地新增/修改的 skill 入库（-Push 自动推送）
└── setup.cmd               # 新机器一键安装入口
```

## 四、真源机制（junction）——关键

本机 4 个 agent 的 skills 目录里，**每个 skill 都是 NTFS junction**，指向 `D:\Zcode\ai-skills\skills\<name>`：

- `C:\Users\32204\.zcode\skills`（ZCode）
- `C:\Users\32204\.agents\skills`（AGENTS 标准）
- `C:\Users\32204\.claude\skills`（Claude Code）
- `C:\Users\32204\.codex\skills`（Codex）

即：**任何 agent 调用 skill 读的都是仓库文件**，改一处全部生效。此前这 4 个目录是彼此相同的副本（MD5 验证过），现已全部换成 junction。

`install.ps1` 行为：幂等；已是正确 junction → 跳过；真实目录与仓库内容一致 → 直接替换；不一致 → 先移入 `.backup/<时间戳>/` 再替换；被进程占用 → 跳过并提示重跑。`-Local` 面向项目级（当前目录 `.claude\skills`、`.agents\skills`），`-Remove` 只移除指向本仓库的 junction。

### ⚠️ 遗留事项 1
`nature-academic-search` 在 4 个目录里**仍是真实目录**（切换时它的 `mcp-server` 子目录被运行中的 MCP 进程占用，ZCode 全局 `~/.zcode/cli/config.json` 里的 academic-search MCP server 正是从那里启动的）。**内容与仓库完全一致，功能无影响**；在全新的会话里重跑一次 `powershell -ExecutionPolicy Bypass -File D:\Zcode\ai-skills\install.ps1` 即可补上。

## 五、任务脚本自动归档（钩子）——已生效机制

**ZCode 全局钩子**（`C:\Users\32204\.zcode\cli\config.json` 的 `hooks` 块，`enabled: true`）：事件 `UserPromptSubmit` + `Stop`，`type: "process"` 调用 `powershell -NoProfile -ExecutionPolicy Bypass -File D:\Zcode\ai-skills\tools\sync_task_scripts.ps1`，`timeoutMs: 90000`。**Claude Code** 同样钩子注册于 `C:\Users\32204\.claude\settings.json`。原有 mcp/plugins 配置未动。

`sync_task_scripts.ps1` 行为细则（已端到端验证：新增/修改/无变化/基线四条路径）：

- 监视 `D:\Zcode\.zcode\workspace\default` 和 `D:\Zcode` **根层**（非递归）的 `.ps1 .py .bat .cmd .sh .js .ts .ahk`（≤2MB）。扩范围：改脚本顶部 `$WatchRoots` 数组。
- **首次见到的文件** → 复制到 `scripts/inbox/<yyyy-MM-dd>/<名>`，`git add -A -- scripts` + commit（`auto-sync: N task script(s)`）+ push。
- **已见文件的修改** → 就地更新同一仓库目标（不产生副本）。此前手工收集的 11 个脚本在 `$SeedMap` 里建立了 源文件名→仓库路径 的映射，改工作区原件即自动更新分类目录里的版本。
- **无变化** → 毫秒级跳过；仓库有未推送提交时任何一次运行都会补推。
- 状态存 `tools/.sync-state.json`（源路径→hash→dest；**首次运行为基线模式，只记录不导入**，防止把旧脚本重复入库）。
- 崩溃恢复：目标已存在且内容 hash 相同 → 复用该目标（不会出现 -2 副本）。
- 日志：`tools/sync.log`（`tracked/imported/committed/pushed`）。脚本**永远 exit 0**（钩子安全）。

### ⚠️ 遗留事项 2
钩子是在 ZCode 会话**中途**注册的，配置在会话启动时读取——**从下一个新开的会话起才真正自动触发**（脚本本身已手动跑通全链路）。Codex 会话没有钩子，其产生的脚本会在下一次 ZCode 会话的 UserPromptSubmit 时被扫到。

### ⚠️ 遗留事项 3（设计使然，非 bug）
`scripts/inbox/` 是暂存区。把 inbox 文件挪进主题目录后，若其工作区原件再次被修改，state 里的旧 dest 会让 inbox 重新出现一份副本——届时删掉 inbox 副本即可（AGENT.md 已写明）。更好的做法是顺手更新 `.sync-state.json` 里对应条目的 dest。

## 六、12 个已收集脚本及来源

| 仓库位置 | 原始位置 |
|---|---|
| scripts/android-mtp/copy_apk.ps1 | D:\Zcode\.zcode\workspace\default\copy_apk.ps1 |
| scripts/android-mtp/fix_mtp_driver.ps1 | 同上目录 fix_mtp_driver.ps1 |
| scripts/android-mtp/reenumerate.ps1 | 同上目录 reenumerate.ps1 |
| scripts/android-mtp/update_driver.ps1 | 同上目录 update_driver.ps1 |
| scripts/productivity/read_schedule.py | 同上目录 read_schedule.py |
| scripts/productivity/ui_mockup.py | 同上目录 ui_mockup.py（22KB matplotlib UI 仿真） |
| scripts/android-ui/dump481.ps1 | D:\Zcode\dump481.ps1 |
| scripts/android-ui/parse_ui.ps1 | D:\Zcode\tools\parse_ui.ps1（注意：tools\ 子目录不在钩子监视范围内） |
| scripts/productivity/start_zcode.bat | D:\Zcode\启动ZCode.bat（入库时改名 ASCII） |
| scripts/legacy/check_files.py | D:\Zcode\_check.py |
| scripts/legacy/explore_tree.py | D:\Zcode\_explore.py |
| scripts/legacy/c_drive_cleanup.bat | D:\Zcode\_C盘收尾_关闭ZCode后运行.bat |

## 七、常用命令速查

```powershell
# 手动触发一次脚本自动同步（等价于钩子做的事）
powershell -NoProfile -ExecutionPolicy Bypass -File D:\Zcode\ai-skills\tools\sync_task_scripts.ps1

# 新机器接入
git clone https://github.com/Guangze-Dan/ai-skills.git D:\ai-skills ; cd D:\ai-skills ; setup.cmd

# 新项目嵌套（多仓）
cd <项目> ; git submodule add https://github.com/Guangze-Dan/ai-skills.git .ai-skills
cd .ai-skills ; powershell -ExecutionPolicy Bypass -File install.ps1 -Local

# skills 反向收集（本地新建 skill 忘了入库时）
powershell -ExecutionPolicy Bypass -File D:\Zcode\ai-skills\collect.ps1 -Push

# 重建 skill 索引
powershell -ExecutionPolicy Bypass -File D:\Zcode\ai-skills\tools\gen_registry.ps1

# 仓库公开（当前私有）
gh repo edit ai-skills --visibility public --accept-visibility-change-consequences
```

## 八、本机环境坑（重要，未来排障省时间）

1. **PowerShell 5.1 + 中文 .ps1 必须带 UTF-8 BOM**，否则按 GBK 误读导致解析错误（install.ps1 曾因此挂掉；现 install.ps1 已改为纯 ASCII，collect.ps1 / gen_registry.ps1 / sync_task_scripts.ps1 均已加 BOM）。
2. **PS 5.1 下 `$ErrorActionPreference='Stop'` 时原生命令的 stderr 输出会抛 NativeCommandError**（git 的 CRLF 警告就触发过）。sync 脚本里用 `Invoke-Git`（临时切 Continue + `2>&1` 合并）规避——不要改成裸 `2>$null`。
3. cmd 里 `echo x=2>>file` 会把 `2>>` 当 stderr 重定向解析。
4. `~/.zcode/skills/.system`（及 `.claude`/`.codex` 同名目录）是 **Codex 自动管理的系统技能**（含 `.codex-system-skills.marker`），不属于个人资产，已排除出仓库，勿动。
5. `nature-proposal-writer` 文件夹的 frontmatter `name` 是 `researchwrite`（名字与目录不一致，registry.json 两者都记录了）。
6. 仓库 `.gitattributes` 对 `.ps1/.bat` 强制 CRLF、`.py` 强制 LF，git 会打 CRLF 警告——无害，勿因警告改行尾。
7. GitHub 推送偶发 `Empty reply from server`（瞬时网络），重试即可。
8. 本仓库私有、无 LICENSE、无 CI；junction 只在本机有效，换机器靠 clone + install.ps1 重建。

## 九、建议的下一步（按优先级）

1. 新会话重跑 `install.ps1`，补齐 `nature-academic-search` 的 4 个 junction（见遗留 1）。
2. 新会话里在工作区根目录建个测试脚本，确认钩子自动入库（见遗留 2），然后清理。
3. 隔段时间整理 `scripts/inbox/` 进主题目录（见遗留 3）。
4. 可选：给仓库加 LICENSE / CI（push 后自动跑 gen_registry 校验 registry.json 一致性）。
