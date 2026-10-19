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

## 硬约束（两条通用铁律）

1. **中文字体宋体，西文/数字 Times New Roman（罗马字体），变量斜体**。任何一张图都不得出现其它字体族。
   变量（如 σ、t、T、R）必须斜体，单位（MPa、d、mm）保持正体。
2. **只用黑白灰 + 一个强调色**。示意/曲线一律黑色；需要突出对比时用红色一类亮色，
   绝不使用 Origin/Visio 默认的多彩配色。

## ⚠️ 前置条件：自动化导出的图带 "demo" 水印（已定位到导出环节）

用 `originpro` 脚本导出 Origin 图，PNG 会被平铺的青色 "demo" 水印覆盖，**不能用于投稿**。
**关键事实**：同一张图**显示在 Origin 窗口里是干净的**，水印是"导出"这一动作经由自动化接口时加上的。
已排除授权、导出 API、窗口可见性、数据来源、导出参数、实例来源六种假设。
**在结论明确前**：Origin 路线产出的图必须逐张肉眼确认无水印；推荐折中做法 ——
**自动化只建图并存 OPJU，最终导出由用户在 GUI 里完成**；或改走 matplotlib/SVG 出图。
完整证据链与应对见 [automation-stack.md](references/automation-stack.md)。

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

- 数据图（Origin）：[references/origin-format.md](references/origin-format.md)
- 示意图（Visio）：[references/visio-format.md](references/visio-format.md)
- **自动化工具链与依赖**：[references/automation-stack.md](references/automation-stack.md) —— 要真自动出图（而不是只给清单）时读它
- 原始规范截图（用户 docx 内的实例）：`assets/origin-*.png`、`assets/visio-*.png`
