# HANDOFF — ai-skills 统一真源系统 · 交接文档

> 给接手的 AI：本文档自包含。读完即可继续维护、扩展、排障这套系统，无需向用户追问历史背景。
> 首建：2026-10-07 · 最近更新：2026-11-12 · GitHub: **Guangze-Dan**
>
> 会话史速览：①旧机器搭建全系统 → ②新机器迁移+收集至 47 skills → ③旧机器对齐（多机 WatchRoots、nature-paper-trans 修订）→ ④windows-mcp 补齐两台机器 → ⑤hyperframes 族升 v0.8.140、钩子自动触发实证 → ⑥2026-10-08 新装 11 skills（→58）+ yt-dlp / cli-anything-wps 工具 → ⑦2026-10-08 旧机器同步：pull 5 提交、11 新 skill 已链接（58×4）、补装 cli-anything-wps 1.0.0（本机有 WPS Office 2023）。

---

## 一、背景与目标

用户要求：把所有个人 AI skills 和历史自动化脚本整理成 GitHub 上的**唯一真源**，让所有 AI agent（ZCode / Claude Code / Codex / AGENTS 标准）直接调用；并且**今后每次任务产生的新脚本自动进仓库**，不再重复手工收集。以上均已实现并持续运行。

⚠️ **双机共用本仓库**（这是当前最重要的运行事实）：

| 机器 | 用户目录 | 仓库路径 | 状态 |
|---|---|---|---|
| 新机器 | `%USERPROFILE%`（无 D: 盘，数据根 `E:\Zcode数据`） | `<repo>` | 日常主力 |
| 旧机器 | `%USERPROFILE%`（`D:\Zcode` 仍存在） | `<repo>` | 仍在服役、会推送 |

两台机器各自跑钩子、各自 push。**推送被拒（non-fast-forward）时 = 对端机器有新提交，`git pull --rebase` 再推**（已发生过一次，rebase 干净无冲突）。`tools/sync_task_scripts.ps1` 的 `$WatchRoots` 是**多机列表**，不存在的路径自动跳过，两台机器共用同一脚本。

## 二、核心资产与凭据（以新机器为准）

| 项 | 值 |
|---|---|
| GitHub | https://github.com/Guangze-Dan/ai-skills （**公开**） |
| gh 登录 | `Guangze-Dan`，scopes: `gist, read:org, repo, workflow`（keyring） |
| git / gh | 2.55 / 2.97，`C:\Program Files\Git\cmd\git.exe`，均在 PATH |
| ZCode 工作区 | `E:\Zcode数据\.zcode\workspace\default`（`E:\Zcode` 只是应用安装目录） |
| Python | 3.14.6（`C:\Python314`）；用户级 Scripts：`%APPDATA%\Python\Python314\Scripts`（**已入用户 PATH**，uv/yt-dlp/cli-anything-wps 都在这） |
| uv 工具目录 | `%USERPROFILE%\.local\bin`（已入用户 PATH，windows-mcp 在此） |

## 三、仓库结构（skills 共 **63** 个）

```
<仓库根>\
├── skills/                 # 63 个个人 skill（skills/<name>/SKILL.md），真源本体
├── scripts/                # 自动化脚本（主题分类 + inbox/ 暂存区）
│   ├── android-mtp/  android-ui/  productivity/  legacy/
│   └── inbox/<日期>/       #   钩子自动归档的新任务脚本
├── tools/
│   ├── gen_registry.ps1        # 重建 registry.json
│   ├── sync_task_scripts.ps1   # ★ 钩子调用的自动同步（$Repo 自定位；$WatchRoots 多机列表）
│   ├── .sync-state.json        # 同步状态（gitignore；含 baselined 标志）
│   └── sync.log                # 同步日志（gitignore）
├── .backup/                     # install.ps1 的自动备份（迁移时 19 个 codex 旧副本在 20261007-100232/）
├── registry.json / AGENT.md / README.md / HANDOFF.md
├── install.ps1             # skills → 各 agent 目录 junction（幂等、自定位）
├── collect.ps1             # 反向收集本地新增/修改的 skill 入库（-Push 自动推送）
└── setup.cmd               # 新机器一键安装入口
```

## 四、真源机制（junction）

两台机器的 4 个 agent skills 目录（`.zcode` / `.agents` / `.claude` / `.codex`）里每个 skill 都是 NTFS junction，指向**各自机器的仓库副本** `skills\<name>`。新机器当前 **63 junction × 4**（`.codex` 多一个真实目录 `.system`——Codex 系统技能，勿动勿入库）。**任何 agent 调 skill 读的都是仓库文件，改一处（push 后另一台 pull）全部生效。**

`install.ps1`：幂等、`$PSScriptRoot` 自定位；正确 junction→跳过；真实目录内容一致→直接替换，不一致→先备份到 `.backup/<时间戳>/` 再替换；被占用→跳过待重跑。`-Local` 项目级、`-Remove` 只删指向本仓库的 junction。**新 skill 入库后必须跑一次 install.ps1 才会链接到各 agent**（junction 不会凭空出现）。

`collect.ps1`：扫 4 个 agent 目录的真实目录（跳过 `.system` 和指回仓库的 junction），仓库没有的复制入库（added），不同的以本地覆盖仓库（updated），然后重建 registry。

## 五、任务脚本自动归档（钩子）——已运行中，两台机器均实证

- **ZCode**：`~/.zcode/cli/config.json` 的 `hooks` 块（`enabled:true`，事件 `UserPromptSubmit`+`Stop`，`type:"process"`，`timeoutMs:90000`）。
- **Claude Code**：`~/.claude/settings.json` 同钩子（`type:"command"`，`timeout:90` 秒）。
- **已实证自动触发**（2026-10-07 22:26 演示脚本被自动入库，sync.log 有连续自动运行记录），不再是"待验证"状态。
- Codex 无钩子机制，其脚本在下次 ZCode/Claude 会话 UserPromptSubmit 时被补扫。
- 配置在会话启动时读取：中途改钩子/MCP 配置，**下一个新会话**才生效。

`sync_task_scripts.ps1` 行为要点：`$Repo` 自定位免迁移；`$WatchRoots` 双机列表（新机 `E:\Zcode数据\.zcode\workspace\default` + `E:\Zcode数据` 根层，旧机 `D:\Zcode` 对应两处；非递归，扩展名 `.ps1 .py .bat .cmd .sh .js .ts .ahk`，≤2MB）；首跑基线只记录不导入（`baselined` 标志持久化，此前的"files 为空判断"bug 已修，提交 929d292）；已见文件修改→就地更新同一目标；无变化毫秒级跳过并补推未推送提交；崩溃恢复按内容 hash 复用目标；永远 exit 0。inbox 挪入主题目录后记得同步改 `.sync-state.json` 对应条目的 dest。

## 六、skills 来源档案（63 个；按入库批次）

| 批次 | 内容 |
|---|---|
| 初始 37（旧机器手工整理） | nature 全家桶、hyperframes 族、productivity 等 |
| +10（新机器 collect，codex 独有） | academic-paper(-reviewer/-pipeline)、citation-check-skill、deep-research、humanizer、image-to-editable-ppt、literature-reviewer-skill、zo-read-paper、zotero-connector |
| hyperframes 族 10 个升版（2026-10-07，提交 8af4d58） | 上游 [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) release **v0.8.140**；agent-reach 顺带补 SKILL_en.md（[Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)，内容与本地一致）；**impeccable 本地即上游最新 4.5.0 未动**（[pbakaus/impeccable](https://github.com/pbakaus/impeccable)；本地多的 `scripts/bin/windows-x64/impeccable.exe` 被 `impeccable.cmd` 引用，保留） |
| +11（2026-10-08，提交 be3c62f） | **cli-anything-wps / -zotero / -photoshop**（[yb2460/harness-anything](https://github.com/yb2460/harness-anything)）；**uiux-pro-max 7 件套**（ui-ux-pro-max、design、design-system、ui-styling、brand、banner-design、slides，[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)——搜索到的低星仓库都是它的 fork）；**open-design**（[sugarforever/open-design-skill](https://github.com/sugarforever/open-design-skill)） |
| paper-spine（刻意未动） | 本地 0.4.0-alpha.3 **已内置 humanize 组件**（references/humanize*.md + 脚本），且带本地定制痕迹（比上游 dist 多 2 文件、约 59 文件有差异）。除非用户明确要求，勿用上游覆盖 |

## 七、常用命令速查（新机器路径；旧机器把仓库根换成自己的克隆目录）

```powershell
# 手动触发一次脚本自动同步（等价于钩子）
powershell -NoProfile -ExecutionPolicy Bypass -File <repo>\tools\sync_task_scripts.ps1

# 新 skill 入库后：链接到 4 个 agent + 重建索引 + 提交
powershell -ExecutionPolicy Bypass -File <repo>\install.ps1
powershell -ExecutionPolicy Bypass -File <repo>\tools\gen_registry.ps1
git -C <repo> add -A ; git -C <repo> commit -m "..." ; git -C <repo> push
# push 被拒 = 另一台机器有新提交：git -C <repo> pull --rebase 后再 push

# skills 反向收集 / 重建索引 / 新机器接入（clone + setup.cmd 后补 WatchRoots 和钩子）
powershell -ExecutionPolicy Bypass -File <repo>\collect.ps1 -Push
powershell -ExecutionPolicy Bypass -File <repo>\tools\gen_registry.ps1

# hyperframes 技能族升级（需代理，见坑 13）
$env:NODE_OPTIONS="--use-env-proxy" ; $env:HTTPS_PROXY="http://127.0.0.1:7897" ; npx -y hyperframes@latest skills update
```

## 八、环境坑与已装工具（重要，排障省时间）

**坑：**
1. **PS 5.1 + 中文 .ps1 必须 UTF-8 BOM**（文件头 `EF BB BF`），否则按 GBK 误读解析错。
2. **PS 5.1 Stop 偏好下原生命令 stderr 抛 NativeCommandError**（git CRLF 警告即触发）；sync 脚本用 `Invoke-Git` 规避，勿改裸 `2>$null`。
3. **PS 5.1 `DirectoryInfo.Delete()` 非递归**，非空必抛错；删目录用 `Remove-Item -Recurse -Force`（collect.ps1 三处曾全中招，提交 622db74）。
4. **Git Bash 传内联 PowerShell**：`$`、反引号、`\` 会被 bash 吞——写 .ps1 临时文件再 `-File` 执行（别放钩子监视目录，或用完即删）。
5. cmd 里 `echo x=2>>file` 的 `2>>` 是 stderr 重定向。
6. `~/.zcode/skills/.system` 等是 Codex 系统技能，勿动勿入库。
7. `nature-proposal-writer` 目录的 frontmatter name 是 `researchwrite`（registry 两者都记）。
8. `.gitattributes` 强制 CRLF/LF，git 打行尾警告——无害勿理。
9. GitHub 推送偶发 `Empty reply from server`——瞬时网络，重试。
10. **双机共用仓库**：push 前最好先 `git pull --rebase`（见第一节）。
11. **网络（新机器实测）**：`raw.githubusercontent.com`、`codeload.github.com` 直连不通；`api.github.com` 和 github.com 的 git clone 直连正常。Clash Verge 代理在 `127.0.0.1:7897`：curl 加 `--proxy` 可用；Node fetch 需 `NODE_OPTIONS=--use-env-proxy` + HTTPS_PROXY；**git 走该代理反而 schannel 握手失败**——大文件下载用 `curl --proxy` 拉 GitHub API tarball 再解压，别让 git 挂代理。
12. `gh repo clone` 的输出会静默吞掉部分行，长克隆放后台任务跑并另开窗口 `du` 查进度。
13. pip 用户级安装的 exe 落在 `AppData\Roaming\Python\Python314\Scripts`——**该目录已入用户 PATH**（装 yt-dlp 时加的），但已开着的 shell 要重开才有。

**已装工具（新机器，均在 PATH）：**
- **windows-mcp**（uv tool，`%USERPROFILE%\.local\bin\windows-mcp.exe`；AI 操控 Windows 桌面）。ZCode `config.json` mcp.servers / Claude `.claude.json` mcpServers / Codex `config.toml` mcp_servers 三处注册，env 关匿名遥测；`.claude.json` 备份 `~/.claude.json.bak-windowsmcp`。旧机器同日也已装（Python311 + uv，`%USERPROFILE%\.local\bin\`）。
- **yt-dlp** 2026.08.19（pip 用户级；即用户说的 "yt-dip"，GitHub 上 yt-dIp 只是 yt-dlp 的 fork）。
- **cli-anything-wps** 1.0.0（pip，来自 harness-anything monorepo；COM 控制 WPS 文字/表格/演示，47 命令，需装 WPS Office 才能实际干活，Windows 专属）。photoshop/zotero harness 技能已入库，装对应软件即可用。**旧机器 2026-10-08 已同样安装**：PyPI 无此包，可用装法 `pip install git+https://github.com/yb2460/cli-anything-wps.git`（独立仓库）；旧机器有 WPS Office 2023（雨糖科技特别版），装后实测正常。

## 九、建议的下一步（按优先级）

1. ~~验证钩子自动触发~~ ✅ 2026-10-07 已实证。剩余例行：隔段时间整理 `scripts/inbox/` 进主题目录并更新 `.sync-state.json` 的 dest。
2. `nature-academic-search` 的 MCP server 仍只在旧机器配置过，新机器如需要要在 `~/.zcode/cli/config.json` 补 mcp 配置。
3. paper-spine 与上游的 59 文件差异待用户拍板：保留本地定制 or 对齐上游（覆盖前先备份）。
4. 已于 2026-11-12 切换为公开仓库；可选：补 LICENSE / CI（push 后自动 gen_registry 校验一致性）。
