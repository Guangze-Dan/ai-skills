# 安装与环境要求

本 skill 分两部分：**规范文档**（纯文本，装了就能用）和**自动化脚本**（要额外装依赖，且依赖本机
装有 Origin / Visio）。只用规范、不跑脚本的话，什么都不用装。

---

## 一、Python 环境

- **64 位 CPython 3.10 / 3.11 / 3.12**（实测基线 3.11.9）
- 不支持 32 位 Python；`originpro`、`OriginExt`、`pywin32` 都只有 Windows 64 位轮子

```bash
python -m pip install -r requirements.txt
```

### requirements.txt 内容

| 包 | 版本 | 用途 | 不装会怎样 |
|---|---|---|---|
| `pywin32` | 312 | COM 桥，驱动 Visio | Visio 自动化不可用 |
| `originpro` | 1.1.15 | Origin 官方 Python 封装 | Origin 自动化不可用 |
| `OriginExt` | 1.2.6 | `originpro` 的底层扩展（会被自动带上） | 同上 |
| `ezdxf` | 1.4.5 | 用代码生成 dxf，**替代 CAD 画图那一步** | 没有 CAD 就画不了示意图 |
| `Pillow` | 12.3.0 | 导出校验、位图后处理 | 校验脚本不可用 |
| `numpy` | 2.4.6 | 几何/数据计算 | 部分脚本不可用 |

纯数据图若走 matplotlib 兜底路线（绕开 Origin），另需 `matplotlib`。

**不需要**：`comtypes`（pywin32 已覆盖）、`pyautogui` / `pywinauto`（有 COM 就不必模拟键鼠）。

---

## 二、第三方软件（非 Python 包）

| 软件 | 版本要求 | 是否必需 | 说明 |
|---|---|---|---|
| **Origin / OriginPro** | 2021 或更高（实测 2025b / 10.25） | 只有走 Origin 出图才需要 | 必须有**正式授权**，见下方"已知阻塞" |
| **Microsoft Visio** | 桌面版（实测 LTSC 专业版 2024 / 16.0） | 只有走 Visio 示意图才需要 | **Visio 网页版不行**，必须有 COM 自动化能力 |
| **AutoCAD 等 CAD** | — | **不需要** | 示意图的 dxf 用 `ezdxf` 代码生成，规范里"Cad 画图另存 dxf"那一步可以完全跳过 |

---

## 三、环境自检

装完跑一下：

```bash
python scripts/check_env.py
```

它会检查 Python 位数/版本、各依赖是否可导入、Origin 与 Visio 的 COM 接口是否可用，
并打印本机遇到过的坑（会话锁屏、残留进程等）。

---

## 四、⚠️ 已知阻塞：Origin 导出的 "demo" 水印

**在作者机器上实测到一个无法绕开的问题**：该安装的 Origin **任何导出**（脚本导出、GUI 菜单导出，
甚至用 Origin 自己新建的空图导出）都会被打上平铺的青色 **"demo"** 水印，不能用于投稿。
屏幕上的图是干净的，只有导出被加水印。已排除"自动化导致"这个方向。

**换一台机器可能没有这个问题**（作者的另一套环境导出正常）。请先自测一次：
Origin 里 `File → New → Graph` 建张空图 → `File → Export Graph...` → 导出 PNG → 打开看有没有
青色 "demo"。有就是授权状态问题，与本 skill 的脚本无关。

详见 [references/automation-stack.md](references/automation-stack.md)。

---

## 五、把 skill 装到各个 agent

本 skill 就是 `academic-figure-style/` 这个目录。把整个目录放到对应 agent 的 skills 目录下即可：

| Agent | 目标目录 |
|---|---|
| ZCode | `%USERPROFILE%\.zcode\skills\` |
| Codex | `%USERPROFILE%\.codex\skills\` |
| Claude Code | `%USERPROFILE%\.claude\skills\` |
| 通用 | `%USERPROFILE%\.agents\skills\` |

目录名保持 `academic-figure-style`，里面必须有 `SKILL.md`（agent 靠 frontmatter 的 `name` /
`description` 识别与触发）。放好之后**新开一个会话**才会生效。

---

## 六、按需要改的地方

- `scripts/export_graphs.ogs` 里的输出目录写的是示例路径，改成你自己的。
- `scripts/build_origin_figure.py` 顶部的 `STYLE` 字典是全部样式参数，想调字号/线宽改这里。
- 本 skill 的规范来自作者的《Origin/Visio 论文出图格式》，如果你有自己的期刊模板，
  改 `references/origin-format.md` 与 `references/visio-format.md` 里的数值即可，脚本不用动。
