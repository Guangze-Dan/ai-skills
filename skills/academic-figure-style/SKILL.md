---
name: academic-figure-style
description: >-
  用户自己的论文出图house style（Origin 数据图 + Visio 示意图）。当用户说「学术绘图风格」「按我的出图规范」
  「论文出图格式」「出图」「照之前那样画」或提交图表/数据要求按期刊风格绘制时使用。覆盖 Origin 点线图的
  尺寸/轴线/字体/刻度/布局/线条/导出，以及 Visio 示意图的 CAD→dxf→Visio 流程、图幅、线宽线型层级、文字与
  公式字号、600×600 jpg 导出。不用于统计建模、数据清洗或交互式看板。
---

# 学术绘图风格（Academic Figure Style）

这是用户自有的论文插图规范。**当用户只说「学术绘图风格」时，不要反问格式细节** —— 按本 skill 的规范直接执行，
并把下面的参数清单作为交付的一部分给出，方便用户在自己机器上核对。

## 第一件事：判定出图路线

先判断要画的是哪一类，再读对应 reference：

| 图类型 | 路线 | 规范文件 |
|---|---|---|
| 数据图：点线图、曲线、散点、柱状、误差棒等有真实数据的图 | **Origin** | [references/origin-format.md](references/origin-format.md) |
| 示意图：结构/剖面/装置/流程/机理图，CAD 画的线框示意图 | **Visio**（CAD 出图 → dxf → Visio） | [references/visio-format.md](references/visio-format.md) |
| 两者都要（论文里图1是示意图、图2~5是数据图） | 分别按上表处理 | 两个都读 |

判定不了就问一句：**「这张是数据图（Origin）还是示意图（Visio）？」** 不要猜。

## 硬约束（四条通用铁律）

1. **中文字体宋体，西文/数字 Times New Roman（罗马字体）**。任何一张图都不得出现其它字体族 ——
   逐张确认，不要相信默认设置。
2. **物理量斜体、单位正体**：变量与希腊字母（*σ*、*ε*、*η*、*t*）斜体；单位（MPa、℃、%）、
   数字、函数名、说明性下标（*p*<sub>max</sub>）正体。完整对照表见
   [references/typography-rules.md](references/typography-rules.md)。
3. **坐标轴标题的量与单位用斜杠 `/` 分隔，不用括号**（`贮室温升 / ℃`，不是 `贮室温升（℃）`），
   **全文统一**；坐标轴文字在最终印刷尺寸下必须清晰可读。
4. **只用黑白灰 + 一个强调色**。示意/曲线一律黑色；需要突出对比时用红色一类亮色，
   绝不使用 Origin/Visio 默认的多彩配色。

## 图的规矩（容易被忽略，逐条对照）

- **图中不放"注：…"** —— 测点位置、参数口径、定义这类解释性内容**全部移到正文**；
  物理量首次出现时在正文里解释一次即可。
- **同一物理量全文只能有一种写法**，尤其上下标：若规范上用 Δ*T*<sub>eff</sub>（带下标），
  全文所有图、公式、正文都必须带下标，不能一处有一处没有。
- **MathType 公式的字号要与正文一致**（在 `大小 → 定义尺寸` 里设），不能沿用旧模板的默认值。
- **修改过的公式要标红**，与其它修改一致，便于审稿人比对。
- **图与图题之间不留大空白**（通常是图片自带白边或段落间距不一致造成）。
- 交付前过一遍 [references/typography-rules.md](references/typography-rules.md) 末尾的自检清单。

## ⛔ 前置条件：这台 Origin 的**任何导出**都带 "demo" 水印

从这台机器上的 Origin 导出的图，**一律**带平铺的青色 "demo" 水印，**不能用于投稿**。
已实测到无可辩驳：用 Origin **自己的 GUI** 新建一张空图（`File → New → Graph`，默认模板、无数据、
不涉及任何脚本），再用 **GUI 菜单**导出，照样满屏水印。屏幕上的图是干净的，只有导出会被加水印。

**这不是本 skill 脚本的问题，也不是"自动化"的问题，任何脚本都绕不过去。**
早先设想的"自动化建图 + GUI 导出"两段式方案**已作废** —— GUI 导出同样带水印。
唯一出路是让 Origin 恢复授权，或改用别的工具链（matplotlib/SVG）出图。

完整证据链见 [automation-stack.md](references/automation-stack.md)。Visio 那条线（COM）不受影响。

## 交付形态

按用户要的东西给，默认给「参数清单 + 可执行产物」：

- **要自己动手画** → 输出逐步操作清单，逐步对齐 reference 里的参数（尺寸、线宽、字号取具体数值，不要写"适中"）。
- **要代码出图** → 生成 matplotlib / SVG 脚本，把本规范的具体数值写进代码：
  - 画布：7 cm × 5 cm（Origin 数据图）或 8 cm 图幅（Visio 示意图）
  - 字体：`font.family` 用 Times New Roman，中文回退 SimSun；标题与正文字号按 reference
  - 轴线 0.2 pt，刻度朝内，坐标轴两端都有刻度数字
  - 线条按「辅助 / 一般 / 重要 / 特别重要」= 0.25 / 0.5 / 1 / 2 分级
  - 导出 ≥ 600×600，曲线图导出矢量（PDF/SVG/EMF）或 600 dpi 以上位图
- **只想核对** → 按两份 reference 的条目逐条打勾，指出不符项。

产物落地后建议用渲染出的 PNG 走一次视觉检查再交付。

## 参考

- **安装与环境要求（分享给他人时先看这个）**：[INSTALL.md](INSTALL.md)
- **正斜体与排版细则（硬约束，优先于下面两份）**：[references/typography-rules.md](references/typography-rules.md)
- 数据图（Origin）：[references/origin-format.md](references/origin-format.md)
- 示意图（Visio）：[references/visio-format.md](references/visio-format.md)
- **自动化工具链与依赖**：[references/automation-stack.md](references/automation-stack.md) —— 要真自动出图（而不是只给清单）时读它
- **可执行脚本**：[scripts/README.md](scripts/README.md) —— 建图脚本、导出脚本、环境自检
- 原始规范截图（用户 docx 内的实例）：`assets/origin-*.png`、`assets/visio-*.png`
