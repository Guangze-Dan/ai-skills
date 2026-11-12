# ai-skills — 个人 AI Agent 技能与脚本 · 统一真源

所有个人 AI skills 和自动化脚本的**唯一真源（Single Source of Truth）**。
本机各 AI agent（ZCode / Claude Code / Codex / AGENTS 标准）的 skills 目录通过 **NTFS junction** 指向本仓库，
任何 agent 的调用读到的都是同一份文件；其他仓库可以以子模块方式嵌套接入。

## 结构

```
ai-skills/
├── skills/                 # 63 个个人 skill，每个一个文件夹（skills/<name>/SKILL.md）
├── scripts/                # 历史自动化脚本（已分类）
│   ├── android-mtp/        #   小米手机 MTP/USB 驱动修复 + APK 推送
│   ├── android-ui/         #   Android 屏幕 UI dump 解析
│   ├── productivity/       #   UI 造图 / 课表读取 / 启动器
│   ├── legacy/             #   一次性脚本存档
│   └── inbox/<日期>/       #   钩子自动归档的新任务脚本（暂存区）
├── tools/                  # 仓库维护工具（gen_registry.ps1、sync_task_scripts.ps1）
├── registry.json           # 全部 skill 的机器可读索引（name / dir / description）
├── AGENT.md                # 给 AI agent 看的入口说明
├── install.ps1             # 一键接入：把本仓库 junction 到各 agent 的 skills 目录
├── collect.ps1             # 反向收集：把本地新增/修改的 skill 收进仓库
└── setup.cmd               # Windows 一键安装入口
```

## 快速开始

### 新机器接入（Windows）

```powershell
git clone https://github.com/Guangze-Dan/ai-skills.git $HOME\ai-skills
cd $HOME\ai-skills
setup.cmd          # 或: powershell -ExecutionPolicy Bypass -File install.ps1
```

执行后，以下目录里的每个 skill 都变成指向本仓库的 junction（不复制文件）：

| Agent | 目录 |
|---|---|
| ZCode | `%USERPROFILE%\.zcode\skills` |
| AGENTS 标准 | `%USERPROFILE%\.agents\skills` |
| Claude Code | `%USERPROFILE%\.claude\skills` |
| Codex | `%USERPROFILE%\.codex\skills` |

### DeepSeek Harness（DSH / dsh 桌面版）

DeepSeek Harness **无需 junction，天然接入**：其核心插件 `@deepseek-ai/dsh-skill-filesystem`
默认扫描 `%USERPROFILE%\.agents\skills`（`agentsHome` 默认 `~/.agents`，可被 `DSH_AGENTS_HOME`
环境变量覆盖；`includeDefaultRoots` 默认开启，且默认跟随符号链接）。由于 AGENTS 标准目录本身就是
指向本仓库的 junction 农场，**仓库里的 skill 更新后 dsh 重开会话即生效，无需任何同步动作**。

- 已验证（v0.2.x 桌面版，`dsh-skill-filesystem` 源码确认）：扫描根为
  项目 `.dsh/skills`、项目 `.agents/skills`、`customSkillDirs`、`~/.dsh/skills`、`~/.agents/skills`、内置目录。
- **不要**往 `install.ps1` 的 targets 里加 `~/.dsh/skills`：那会让 dsh 经 user-agents 和 user-dsh
  两个根重复看到同一批 skill。
- 在 dsh 里新建的 skill（`~/.dsh/skills/<name>/SKILL.md`）由 `collect.ps1` 负责回收
  （该路径已加入其 `$Sources`），收进仓库后自动换成 junction。
- 桌面版里可用 Skill Explorer（社区插件 `@linxin666/dsh-client-ui-skill-explorer`，已安装）直接查看。

### 嵌入其他仓库（多仓嵌套）

方式 A — 子模块（推荐，仓库内固定版本）：

```powershell
cd <你的项目>
git submodule add https://github.com/Guangze-Dan/ai-skills.git .ai-skills
cd .ai-skills && powershell -ExecutionPolicy Bypass -File install.ps1 -Local
```

这会把 skills junction 到该项目的 `.claude\skills` 和 `.agents\skills`，项目内 agent 直接可用。
克隆带子模块的仓库时：`git clone --recurse-submodules <url>`。

方式 B — 只挂部分 skill：手动对需要的 skill 建 junction：

```powershell
New-Item -ItemType Junction -Path ".claude\skills\nature-writing" -Target "$HOME\ai-skills\skills\nature-writing"
```

## 日常工作流

- **新增 skill**：直接在 `skills/` 下建 `<name>/SKILL.md`（含 `name` / `description` frontmatter），然后 `git push`。所有 agent 立即可见（junction 实时生效），无需再复制到各目录。
- **修改 skill**：随便在哪个 agent 目录改（都是同一个文件），或在仓库里改，然后 `git add -A && git commit -m "..." && git push`。
- **本地新建了 skill 忘了进仓库**：跑 `powershell -ExecutionPolicy Bypass -File collect.ps1 -Push`，自动收进仓库并推送。
- **更新到最新**：`git pull` 即可（junction 指向仓库目录，pull 完所有 agent 立即生效）。

## 任务脚本自动归档（已生效，无需手动操作）

已注册 ZCode 全局钩子（`~/.zcode/cli/config.json`，事件 `UserPromptSubmit` + `Stop`，Claude Code 同步注册于 `~/.claude/settings.json`），每次提交新任务/回合结束时自动运行 `tools/sync_task_scripts.ps1`：

- **监视范围**：`D:\Zcode\.zcode\workspace\default` 和 `D:\Zcode` 根目录的脚本文件（`.ps1 .py .bat .cmd .sh .js .ts .ahk`，仅根层、非递归，≤2MB）。要扩大范围就往脚本顶部 `$WatchRoots` 数组加路径。
- **新脚本** → 自动复制到 `scripts/inbox/<日期>/`，自动 commit + push 到 GitHub。
- **脚本被修改** → 就地更新同一仓库文件（此前收集的 11 个脚本已建立映射，改原件即可）。
- **无变化** → 快速跳过（毫秒级）。
- 运行日志：`tools/sync.log`；状态：`tools/.sync-state.json`（两者均不入库）。

`scripts/inbox/` 是自动归档的暂存区，隔段时间把里面的文件挪进合适的主题目录即可（挪动后若工作区原件再被修改，inbox 会重新出现副本，删掉即可）。agent 也可以在任务中直接把脚本放进 `scripts/<主题>/` 自己提交，两种方式不冲突。


## Skills 概览（63 个，完整清单见 [registry.json](registry.json)）

完整描述见 [registry.json](registry.json)（含每个 skill 的触发条件），各分类：

| 分类 | Skills |
|---|---|
| 科研写作流水线（nature 系列） | nature-academic-search, nature-citation, nature-data, nature-downloader, nature-experiment-log, nature-figure, nature-image2ppt, nature-literature-pipeline, nature-paper-card, nature-paper-to-patent, nature-paper-trans, nature-paper2ppt, nature-polishing, nature-reader, nature-ref-verifier, nature-response, nature-reviewer, nature-shared, nature-statistics, nature-writing |
| 科研综合 | researchwrite（文件夹 nature-proposal-writer，基金/开题报告撰写）, paper-spine（端到端证据绑定论文） |
| 视频/动画（HyperFrames 系列） | hyperframes, hyperframes-animation, hyperframes-audio, hyperframes-cli, hyperframes-core, hyperframes-creative, hyperframes-keyframes, hyperframes-registry, hyperframes-studio, media-use |
| 浏览器/全网调研 | agent-reach（16 平台内容获取）, lightpanda（WSL2 无头浏览器） |
| 工具/其他 | hatch-pet（Codex 动态宠物）, hindsight-coding-agent（记忆插件）, impeccable（设计/打磨 UI） |

## 自动化脚本（scripts/）

| 脚本 | 用途 |
|---|---|
| `android-mtp/copy_apk.ps1` | 通过 MTP 把 APK 推送到小米手机 |
| `android-mtp/fix_mtp_driver.ps1` | 用 Windows 内置驱动修复 MTP 设备 |
| `android-mtp/reenumerate.ps1` | 强制重新枚举小米 USB 设备 |
| `android-mtp/update_driver.ps1` | 给 ADB 接口装 Google USB 驱动 |
| `android-ui/parse_ui.ps1` | 解析 uiautomator dump 的 UI XML（id/坐标/文本） |
| `android-ui/dump481.ps1` | 从 UI dump 中提取指定控件子树 |
| `productivity/ui_mockup.py` | matplotlib 生成 App UI 仿真图 |
| `productivity/read_schedule.py` | 读取课表 docx 内容 |
| `productivity/start_zcode.bat` | 启动 ZCode（带路径回退） |
| `legacy/` | 一次性历史脚本存档 |

## 说明

- 本仓库为**公开**仓库，可自由下载、按原样使用；junction 只在本机有效，换机器用 `git clone + install.ps1` 重建。
- `.system` 目录（Codex 自动管理的系统 skill）不属于本仓库，由各 agent 自行维护。
- 已装 git 的机器上，`install.ps1` 会备份内容不一致的旧目录到 `.backup/`（已 gitignore），可随时人工回收。

## 版权与使用

本仓库中由作者原创的内容版权归 **Guangze-Dan** 所有，保留所有权利。

- **允许**：克隆、下载、阅读，并按原样在自己的 AI agent 中使用。
- **不允许**：修改后重新发布、再分发、商业使用，或以自己的名义发布衍生版本；转载须注明出处。
- **例外**：`skills/` 中来自第三方的 skill 归其各自作者所有，遵循其原始许可（见各 skill 目录内的说明与上游链接）。
- 如需合作或授权，请通过 GitHub 联系作者。

