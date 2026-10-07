# HANDOFF — ai-skills 统一真源系统 · 交接文档

> 给接手的 AI：本文档自包含。读完即可继续维护、扩展、排障这套系统，无需向用户追问历史背景。
> 交接时间：2026-10-07 · 最近更新：2026-10-07（同日第二场：**新机器迁移已完成并验证**；第三场：旧机器侧已对齐；第四场：windows-mcp 补齐两台机器）· 用户：但光泽，GitHub: **Guangze-Dan**
>
> **2026-10-07 第三场（旧机器侧，`C:\Users\32204`）**：旧机器仍在服役并与 origin 对齐：补齐了 10 个新 skill 的 junction；`tools/sync_task_scripts.ps1` 的 `$WatchRoots` 已改为**多机器列表**（不存在的路径自动跳过），两台机器共用同一脚本；`nature-paper-trans` 的技能修订已从旧机器工作区入库（含 Windows 版 `pages.py`）。

---

## 一、背景与目标

用户要求：把本机所有个人 AI skills 和历史自动化脚本整理成 GitHub 上的**唯一真源**，让所有 AI agent（ZCode / Claude Code / Codex / AGENTS 标准）直接调用；并且**今后每次任务产生的新脚本自动进仓库**，不再重复手工收集。

第一场会话在旧机器（`C:\Users\32204`，仓库在 `D:\Zcode\ai-skills`）完成全部搭建。第二场会话把整套系统**迁移到新机器**：仓库重新 clone、junction 重建、钩子重新注册、同步链路重新验证，并顺带收集了新机器上 codex 目录独有的 10 个 skill 入库（37 → **47** 个）。

## 二、当前机器与核心资产（2026-10-07 迁移后）

| 项 | 值 |
|---|---|
| 本地仓库 | `E:\Zcode数据\ai-skills`（branch `main`，与 origin 同步） |
| GitHub | https://github.com/Guangze-Dan/ai-skills （**私有**） |
| 用户目录 | `C:\Users\Dan`（旧机器 `C:\Users\32204` 已不存在，历史记录里见到别困惑） |
| 磁盘 | **本机无 D: 盘**。旧文档/脚本里的 `D:\Zcode\...` 路径全部作废；`E:\Zcode` 只是 ZCode 应用安装目录，数据根是 `E:\Zcode数据` |
| gh 登录 | 已登录 `Guangze-Dan`，scopes: `gist, read:org, repo, workflow`（keyring 存储） |
| git / gh | 2.55 / 2.97，`C:\Program Files\Git\cmd\git.exe`，均在 PATH |
| ZCode 工作区 | `E:\Zcode数据\.zcode\workspace\default` |

## 三、仓库结构

```
E:\Zcode数据\ai-skills\
├── skills/                 # 47 个个人 skill（skills/<name>/SKILL.md），真源本体
├── scripts/                # 自动化脚本（按主题分类 + inbox 暂存区）
│   ├── android-mtp/        #   4 个：小米 MTP/USB 驱动修复 + APK 推送
│   ├── android-ui/         #   2 个：uiautomator dump 解析
│   ├── productivity/       #   3 个：ui_mockup.py / read_schedule.py / start_zcode.bat
│   ├── legacy/             #   3 个：一次性历史脚本
│   └── inbox/<日期>/       #   钩子自动归档的新任务脚本（暂存区）
├── tools/
│   ├── gen_registry.ps1        # 重建 registry.json
│   ├── sync_task_scripts.ps1   # ★ 钩子调用的自动同步脚本（$Repo 已自定位，$WatchRoots 按机器维护）
│   ├── .sync-state.json        # 同步状态（gitignore，不入库；含 baselined 标志）
│   └── sync.log                # 同步日志（gitignore）
├── .backup/20261007-100232/codex/  # 迁移时备份：19 个与仓库同名但签名不一致的 codex 旧副本（多为 mtime 差异；排查旧版内容看这里）
├── registry.json           # 47 个 skill 的机器可读索引
├── AGENT.md                # 给任何 AI agent 的使用规则（含自动归档约定）
├── README.md               # 中文主文档：结构/快速开始/工作流
├── install.ps1             # 一键把 skills junction 到各 agent 目录（幂等，$PSScriptRoot 自定位）
├── collect.ps1             # 反向收集本地新增/修改的 skill 入库（-Push 自动推送）
└── setup.cmd               # 新机器一键安装入口
```

## 四、真源机制（junction）——关键

本机 4 个 agent 的 skills 目录里，**每个 skill 都是 NTFS junction**，指向 `E:\Zcode数据\ai-skills\skills\<name>`：

- `C:\Users\Dan\.zcode\skills`（47 junction）
- `C:\Users\Dan\.agents\skills`（47 junction）
- `C:\Users\Dan\.claude\skills`（47 junction）
- `C:\Users\Dan\.codex\skills`（47 junction + 1 个真实目录 `.system`——Codex 自动管理的系统技能，**勿动、勿入库**）

即：**任何 agent 调用 skill 读的都是仓库文件**，改一处全部生效。迁移时旧机器的"遗留事项 1"（nature-academic-search 因 MCP 占用没换成 junction）已随全新链接自然解决。

`install.ps1` 行为：幂等；`$PSScriptRoot` 自定位（仓库挪位置不用改脚本）；已是正确 junction → 跳过；真实目录与仓库内容一致 → 直接替换；不一致 → 先移入 `.backup/<时间戳>/` 再替换；被进程占用 → 跳过并提示重跑。`-Local` 面向项目级，`-Remove` 只移除指向本仓库的 junction。

`collect.ps1`：扫 4 个 agent 目录里的**真实目录**（跳过 `.system` 与指向本仓库的 junction），仓库没有的复制入库并转成 junction（added），内容不同的以本地为准覆盖仓库（updated）。2026-10-07 用它收集了新机器 codex 目录独有的 10 个 skill：academic-paper、academic-paper-reviewer、academic-pipeline、citation-check-skill、deep-research、humanizer、image-to-editable-ppt、literature-reviewer-skill、zo-read-paper、zotero-connector。

## 五、任务脚本自动归档（钩子）——已在本机重新注册

**ZCode**：`C:\Users\Dan\.zcode\cli\config.json`（迁移时新建）的 `hooks` 块，`enabled: true`，事件 `UserPromptSubmit` + `Stop`，`type: "process"`（powershell.exe + args 向量，`timeoutMs: 90000`）。**Claude Code**：`C:\Users\Dan\.claude\settings.json` 同钩子（`type: "command"`，`timeout: 90` 秒）。

⚠️ 钩子注册于会话中途，配置在会话启动时读取——**从下一个新开的会话起才自动触发**（脚本本身已手动跑通全链路）。Codex 无钩子机制，其产生的脚本会在下一次 ZCode/Claude 会话的 UserPromptSubmit 时被扫到。

`sync_task_scripts.ps1` 行为（2026-10-07 在新机器端到端验证过：干净基线 → 新脚本入 inbox + commit + push → 修改后就地更新同一目标）：

- `$Repo` 已改为自定位（脚本父目录的父目录），**迁移免改**；`$WatchRoots` 仍是机器相关的：当前为 `E:\Zcode数据\.zcode\workspace\default` 和 `E:\Zcode数据` 根层（非递归），扩展名 `.ps1 .py .bat .cmd .sh .js .ts .ahk`，≤2MB。换机器改这一处即可。
- **首跑基线**：state 里没有 `baselined: true` 时只记录不导入（防止旧脚本重复入库）；跑过一次后 `baselined` 持久化，之后新文件正常导入。~~早年按"files 为空"判断基线~~——那是 bug：监视目录为空时基线永不结束、新脚本永不导入，已修（提交 929d292）。
- **已见文件的修改** → 就地更新同一仓库目标（不产生副本）。`$SeedMap` 是旧机器手工收集的 11 个脚本的 源文件名→仓库路径 映射，作为历史兼容保留。
- **无变化** → 毫秒级跳过；仓库有未推送提交时任何一次运行都会补推。
- 崩溃恢复：目标已存在且内容 hash 相同 → 复用该目标（不会出现 -2 副本）。
- 日志：`tools/sync.log`。脚本**永远 exit 0**（钩子安全）。
- inbox 是暂存区：把 inbox 文件挪进主题目录后，若工作区原件再被修改，state 里的旧 dest 会让 inbox 重新出现副本——顺手更新 `.sync-state.json` 里对应条目的 dest 即可（AGENT.md 已写明）。

## 六、历史收集记录（旧机器路径，仅供追溯，文件已不在）

| 仓库位置 | 当年原始位置 |
|---|---|
| scripts/android-mtp/copy_apk.ps1 | D:\Zcode\.zcode\workspace\default\copy_apk.ps1 |
| scripts/android-mtp/fix_mtp_driver.ps1 | 同上目录 fix_mtp_driver.ps1 |
| scripts/android-mtp/reenumerate.ps1 | 同上目录 reenumerate.ps1 |
| scripts/android-mtp/update_driver.ps1 | 同上目录 update_driver.ps1 |
| scripts/productivity/read_schedule.py | 同上目录 read_schedule.py |
| scripts/productivity/ui_mockup.py | 同上目录 ui_mockup.py（22KB matplotlib UI 仿真） |
| scripts/android-ui/dump481.ps1 | D:\Zcode\dump481.ps1 |
| scripts/android-ui/parse_ui.ps1 | D:\Zcode\tools\parse_ui.ps1 |
| scripts/productivity/start_zcode.bat | D:\Zcode\启动ZCode.bat |
| scripts/legacy/check_files.py | D:\Zcode\_check.py |
| scripts/legacy/explore_tree.py | D:\Zcode\_explore.py |
| scripts/legacy/c_drive_cleanup.bat | D:\Zcode\_C盘收尾_关闭ZCode后运行.bat |

## 七、常用命令速查（新机器路径）

```powershell
# 手动触发一次脚本自动同步（等价于钩子做的事）
powershell -NoProfile -ExecutionPolicy Bypass -File E:\Zcode数据\ai-skills\tools\sync_task_scripts.ps1

# 又换新机器时：clone + setup（setup.cmd 内部会调 install.ps1）
git clone https://github.com/Guangze-Dan/ai-skills.git <某盘>\ai-skills ; cd <某盘>\ai-skills ; setup.cmd
# 然后必须做两件事：① 改 tools\sync_task_scripts.ps1 顶部 $WatchRoots 为新机器工作区路径；
#                   ② 按上面 config.json / settings.json 的样子在新机器注册钩子。

# 新项目嵌套（多仓）
cd <项目> ; git submodule add https://github.com/Guangze-Dan/ai-skills.git .ai-skills
cd .ai-skills ; powershell -ExecutionPolicy Bypass -File install.ps1 -Local

# skills 反向收集（本地新建 skill 忘了入库时）
powershell -ExecutionPolicy Bypass -File E:\Zcode数据\ai-skills\collect.ps1 -Push

# 重建 skill 索引
powershell -ExecutionPolicy Bypass -File E:\Zcode数据\ai-skills\tools\gen_registry.ps1

# 仓库公开（当前私有）
gh repo edit ai-skills --visibility public --accept-visibility-change-consequences
```

## 八、本机环境坑（重要，未来排障省时间）

1. **PowerShell 5.1 + 中文 .ps1 必须带 UTF-8 BOM**，否则按 GBK 误读导致解析错误（改含中文的 .ps1 后务必确认 BOM：文件头 `EF BB BF`）。
2. **PS 5.1 下 `$ErrorActionPreference='Stop'` 时原生命令的 stderr 会抛 NativeCommandError**（git 的 CRLF 警告就触发过）。sync 脚本里用 `Invoke-Git` 规避——不要改成裸 `2>$null`。
3. **PS 5.1 的 `DirectoryInfo.Delete()` 是非递归删除**，目录非空必抛"目录不是空的"——collect.ps1 三个分支曾全部中招，已改 `Remove-Item -LiteralPath ... -Recurse -Force`（提交 622db74）。
4. **Git Bash 里给 powershell.exe 传内联命令**：`$`、反引号、`\` 都会被 bash 吞掉——复杂命令写成 .ps1 临时文件再 `-File` 执行（注意临时文件别放钩子监视目录里，或用完即删）。
5. cmd 里 `echo x=2>>file` 会把 `2>>` 当 stderr 重定向解析。
6. `~/.zcode/skills/.system`（及 `.claude`/`.codex` 同名目录）是 **Codex 自动管理的系统技能**，不属于个人资产，已排除出仓库，勿动。
7. `nature-proposal-writer` 文件夹的 frontmatter `name` 是 `researchwrite`（名字与目录不一致，registry.json 两者都记录了）。
8. 仓库 `.gitattributes` 对 `.ps1/.bat` 强制 CRLF、`.py` 强制 LF，git 会打 CRLF 警告——无害，勿因警告改行尾。
9. GitHub 推送偶发 `Empty reply from server`（瞬时网络），重试即可。
10. 仓库私有、无 LICENSE、无 CI；junction 只在本机有效，换机器靠 clone + install.ps1 + 手动注册钩子重建。
11. **windows-mcp 已装**（2026-10-07）：uv tool 装于 `C:\Users\Dan\.local\bin\windows-mcp.exe`（该目录已加入用户 PATH），`C:\Users\Dan\.local\bin`；已在 ZCode `config.json` / Claude Code `.claude.json` / Codex `config.toml` 三处注册同一 stdio 服务器（`windows-mcp serve`，env 关闭匿名遥测，超时 60s/120s）。uv 经 pip 装于 `C:\Users\Dan\AppData\Roaming\Python\Python314\Scripts\uv.exe`（该 Scripts 目录不在 PATH）。`.claude.json` 改动前备份在 `~/.claude.json.bak-windowsmcp`。**旧机器（`C:\Users\32204`）同日第四场也已装好**：uv 经 pip 入 Python311、`uv tool install windows-mcp`（0.8.7）→ `C:\Users\32204\.local\bin\windows-mcp.exe`（已 `uv tool update-shell` 加入用户 PATH）；ZCode `config.json` / Codex `config.toml` / 新建 `~/.claude.json`（该机未装 claude CLI）三处注册，改动前均备份 `.bak-windowsmcp`；验证：`codex mcp list` 显示 enabled、mcporter 实测连通（20 tools）。

## 九、建议的下一步（按优先级）

1. 新开一个 ZCode 会话，在工作区根目录建个测试脚本，确认钩子**自动**触发入库（本会话只验证了手动链路），然后清理。
2. 隔段时间整理 `scripts/inbox/` 进主题目录，并同步更新 `.sync-state.json` 对应条目的 dest。
3. 可选：给仓库加 LICENSE / CI（push 后自动跑 gen_registry 校验 registry.json 一致性）。
4. 若需要 `nature-academic-search` 的 MCP server（旧机器曾配置），需在新机器 `~/.zcode/cli/config.json` 手动补 mcp 配置——迁移时未搬，只保留了 hooks。
