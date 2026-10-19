# 自动化工具链（Origin / Visio 出图）

在**本机**（Windows）用代码复现规范里两类图。本文件记录依赖、已验证的 API 写法、以及**已知阻塞**。

## 依赖

| 包 | 版本 | 作用 | 来源 |
|---|---|---|---|
| `pywin32` | 312 | COM 桥，驱动 Visio（`Visio.Application`） | PyPI |
| `originpro` | 1.1.15 | Origin 官方 Python 封装 | PyPI，OriginLab 官方 |
| `OriginExt` | 1.2.6 | `originpro` 底层扩展，随其自动安装 | PyPI，OriginLab 官方 |
| `ezdxf` | 1.4.5 | 代码生成 dxf，**替代 CAD 画图那一步** | PyPI，GitHub `mozman/ezdxf`（MIT，月下载约 490 万） |
| `Pillow` | 12.3.0 | 导出校验、位图后处理 | 已装 |
| `numpy` | 2.4.6 | 几何/数据计算 | 已装 |

本机软件：Origin 2025b（10.25）、Visio LTSC 专业版 2024（16.0.17932）、**无任何 CAD**。

## ⚠️ 头号待查：自动化导出的图带 "demo" 水印（原因未定）

用 `originpro` 脚本导出时，图会被平铺的青色 **"demo"** 文字覆盖（实测青色像素约占画面 2.16%），
**不能用于投稿**。证据图样本：`D:\Zcode\.zcode\workspace\default\origin_watermark_check.png`。

**已经排除的两条**（都实测过，不要再往这两个方向查）：

1. **不是授权问题。** 早先"Origin 未激活"的说法是**错的**，已推翻。实际证据：
   - 安装是 **OriginPro** 2025b（10.25.212），窗口标题为 `OriginPro 2025b - UNTITLED`，无 Demo 标记；
   - `Origin.ini` 与 `InstallInfo.ini` 里都是 `[Registration] UserType=PR`；
   - 用户明确表示自己的 Origin 从不提示激活，且**手工导出一直正常**；
   - `C:\ProgramData\OriginLab\osn.dat` 就是旧版 `olicense.lic` 改名来的授权容器，**它存在**
     （`System/oc_sys.h` 里有官方注释说明），之前误判是因为只看到 `License\` 目录为空。
2. **不是导出 API 的问题。** 已读 `originpro/graph.py` 源码：`save_fig()` 内部拼的就是
   `expgraph -sw type:=... filename:=... path:=...`，**与 GUI 菜单里的"导出图形"是同一个 X-Function**。
   所以"用 save_fig 才带水印、用 GUI 导出就干净"这种解释不成立。

**尚未排除、需要继续验证的两条**：

1. 图形是**由脚本创建**的（`op.new_sheet` + `from_list` + `plotxy iy:=(1,2) plot:=200;`），
   而用户手工画图走的是另一条路径。
2. 自动化会话把 Origin **隐藏**了 —— 所有带水印的导出都发生在 `op.set_show(False)`（即 LabTalk `@VIS=0`）之后。

**待跑的对照实验**（各导出一次、比较青色像素占比）：
- A：隐藏模式 + `save_fig`（已知带水印，作基线）
- B：**可见模式** + `save_fig` ← 关键变量
- C：可见模式下手工建图，再由脚本导出

最快的判别办法其实是让用户**自己手工导出一张图**：若手工导出干净、脚本导出带水印，
则原因锁定在自动化会话上；若手工导出也带水印，则回到安装状态。

**注意**：Origin 是 GUI 程序，**Windows 会话锁屏时无法创建窗口，自动化会直接挂住**
（`op.lt_exec("type -a $(@V)")` 之后卡死）。跑这类实验前先确认会话处于解锁状态，
并用 `taskkill /F /IM Origin64.exe` 清理残留进程。

## Origin：已验证的属性与写法

### 页面尺寸（关键，曾长期卡住）

`page.width` / `page.height` 的单位是**像素**，不是英寸 —— 直接写 `page.width=7` 会把页面压成 7 像素。
正确写法是乘上页面分辨率：

```python
gp.activate()
op.lt_exec("page.updatetoprinter=0;page.kar=0;")          # 解锁尺寸、关掉保持比例
gp.obj.LT_execute("page.width=(7)*page.resx;page.height=(5)*page.resy;doc -uw;")
w_in = float(gp.obj.GetWidth())                            # 回读单位是英寸
h_in = float(gp.obj.GetHeight())
```

实测回读 `7.000 x 5.000` 英寸；`save_fig(..., width=600)` 导出 600×428 像素（宽高比 1.402 ≈ 7/5）。✅

### 属性速查

| 目标 | 写法 |
|---|---|
| 页面尺寸 | `page.width=(<英寸>)*page.resx`、`page.height=(<英寸>)*page.resy` |
| 回读页面 | `graph.obj.GetWidth()` / `GetHeight()`（英寸） |
| 轴线粗细 | `gl.set_float("x.tickthickness", 0.2)` |
| 刻度朝向 | `gl.set_float("x.tickstyle", <0-3>)`（数值含义见下"未解决"） |
| 刻度数量 | `gl.set_float("x.ticks", n)`、`gl.set_float("x.minorTicks", n)` |
| 刻度标签字号 | `gl.set_float("x.label.pt", 22)` |
| 对侧也显示轴 | `gl.set_int("x.opposite", 1)`（官方样例写法） |
| 字体 | `code = int(round(float(op.lt_float("font(Times New Roman)"))))` → `gl.set_int("x.label.font", code)`；实测 Times New Roman = **414** |
| 曲线颜色 | `plot.color = <op.ocolor(...)>` |
| 曲线线宽 | `plot.set_cmd(f"-w {int(round(pt*500))}")` —— LabTalk `set -w` 单位是 **1/500 pt** |
| 符号 | `plot.symbol_kind` / `symbol_interior` / `symbol_size` |
| 图例 | `lg = gl.label('Legend')`；`lg.set_int('showframe', 0)`；`legend.font` / `legend.color` |
| 图层几何 | `gl.set_int("unit",1)` + `set_float("left"/"top"/"width"/"height")`（百分比）+ `set_int("fixed",1)` |
| 坐标范围 | `layer.axis("y").set_limits(lo, hi, increment)` |
| 导出位图 | `gp.save_fig(path, type="png", width=<像素宽>)`（`type` 也可 `tif`） |
| 导出 PDF | `expGraph type:=pdf export:=page filename:=... path:=... tr2.PDF.Fonts.Embed:=1`，导出后校验文件含 `/FontFile`（字体已嵌入） |

来源：`originlab/Python-Samples`（官方，`4. Graphing`）+ `hang-jin/editaplot`（Apache-2.0）实机代码，均已在本地复现关键项。

### 未解决：刻度朝向的数值映射

`x.tickstyle` / `y.tickstyle` 接受 0–3，且实测 1 与 2 会给出不同朝向，但**具体哪个是"朝内"没能确认**：
导出图上 0.2 pt 刻度只有几像素，加上 demo 水印干扰，无法可靠判读。
OriginC 头文件 `OC_const.h` 里的枚举是 `TICK_IN_OUT=0, TICK_IN=1, TICK_OUT=2, TICK_NONE=3`，
但这与我在导出图上的一次目视读法相反，所以**没有采信**。
→ 激活 Origin 后，在 GUI 里点一次刻度样式并回读 `gl.get_float("x.tickstyle")` 即可定论。

### 稳定性坑

每次运行都会拉起一个 Origin 实例，**`op.exit()` 不一定收干净**。实测残留 10 个无窗口的
`Origin64` 进程时，后续连接会报 `无效指针 / invalid pointer` 且无法自愈。跑批前先清进程：

```powershell
Get-Process -Name Origin64 -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Origin 2025b 的默认值变化

OriginLab 官方说明：2025b 调整了**图页比例、边距、字体呈现、轴框、线宽、刻度标签自动旋转**的默认值。
规范原文档可能基于更早版本，在 2025b 上要重新核对一遍视觉结果。

## Visio：已验证的属性与写法

`Visio.Application` 可用（16.0）。`win32com` 直接驱动：

- 画形状：`pg.DrawLine(x1,y1,x2,y2)`、`DrawRectangle`、`DrawOval`
- 线宽 / 线型 / 颜色：`shape.Cells("LineWeight").Formula = "0.50 pt"`、`Cells("LinePattern").Formula = "2"`（虚线）、`Cells("LineColor").Formula = "RGB(r,g,b)"`
- 后台：`app.Visible = 0`
- 导出：`Page.Export(...)`，或按规范框选区域后导出 600×600 jpg

参考现成实现：本机归档 `ai-skills/scripts/inbox/2026-10-09/build_visio.py`、`build_scheme.py`。

## ezdxf：已验证

建 R2000 图纸 + 按线宽分级建图层，线宽正确写入（辅助 25 / 一般 50 / 重要 100 / 特别重要 200，
单位 1/100 mm），实体走 BYLAYER，回读校验通过。✅

⚠️ 图层名用**英文/ASCII**：中文名会被转义成 `\U+8f85\U+52a9` 形式，合法但难维护。

## 现成轮子评估

### `hang-jin/editaplot`（958★，Apache-2.0，2026-10 活跃）—— **推荐作参考实现，不建议整体替换**

它做的是"丢进一个 CSV/XLSX → 理解每一列 → 推荐图型 → 在专用 Origin 实例里出图 → 导出可编辑
OPJU + PNG/PDF/TIF → 反读对象并人工复核"的完整对话式工作流。工程完成度很高（锁文件、
项目内 venv、Origin 版本兼容门、反读校验）。本次页面尺寸的解法就是从它的代码里拿到的。

**但没有直接采用为主引擎**，理由：

1. **目标不一致**。它有自己的风格契约（自有配色、字号、模板），不认识用户 docx 里那套 house style
   （宋体+Times New Roman、轴线 0.2、标题 26/其余 22、线宽四级制）。而用户的诉求恰恰是
   "一说学术绘图风格就按我的规范来、不要反问"；editaplot 的流程则是反复向用户确认列义与图形元素。
2. **只覆盖 Origin，不覆盖 Visio**。ezdxf + Visio 那条线它完全没有。
3. **版本基线是 Origin 2024b**，2025b 只是"目标范围、按本机证据判断"。
4. 它是面向 **Codex** 的技能包，且要求**完整仓库**（不能只放 `skill/editaplot`），
   会自建 `.editaplot-venv` 并按 3.10 基线铺依赖（本机是 3.11.9）。

**建议**：需要"从零拿到一批陌生实验数据、要它推荐图型"时，再单独把 editaplot 装成一个平行技能；
做用户自己论文的图，走本技能（house style + ezdxf/Visio + 上面这套 Origin API）。

其它参考：`Ge-Shun/origin-mcp`（128★，把 Origin 自动化封成 MCP server）、
`deliuou/originplot-skill`（73★）、`Gerry2024-hub/...-python-origin-plotting-skill`（78★）。

⚠️ `2202alejandro/OriginLab-OriginPro-workflow-templates` 描述为"2026 Full Version"，疑似破解软件分发仓库，**不要使用**。
