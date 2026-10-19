# scripts —— 自动化出图（两段式）

本目录的脚本按用户的《Origin 论文出图格式》出图。因为**经由自动化接口触发的 Origin 导出会被加上
"demo" 水印**（详见 `../references/automation-stack.md`），流程被拆成两段：

```
┌─ 第一段：脚本（本目录）────────────────────────────┐
│ build_origin_figure.py                            │
│   读数据 → 按规范建图（7x5 英寸 / 轴线 0.2 / 字体 /  │
│   刻度 / 布局）→ 保存 .opju                        │
│   ★ 不导出图片                                     │
└───────────────────────────────────────────────────┘
                        ↓ 打开 OPJU
┌─ 第二段：你在 Origin 里做（导出干净，无水印）────────┐
│ 菜单 File → Export → Graphs...                     │
│   或 Script Window 里跑 export_graphs.ogs          │
└───────────────────────────────────────────────────┘
```

## build_origin_figure.py

```bash
# 用示例数据
python build_origin_figure.py --demo out/figure.opju

# 用真实数据：第 0 列作 X、第 1 列作 Y
python build_origin_figure.py data.csv out/figure.opju --x 0 --y 1
```

- 数据支持 CSV/TXT（走 Origin 的 `from_file`）。
- 样式参数集中在脚本顶部的 `STYLE` 字典里，数值来自用户规范原文。
- 运行前请确认 Origin 未被占用；跑完可清掉残留进程：

```powershell
Get-Process -Name Origin64 -ErrorAction SilentlyContinue | Stop-Process -Force
```

**已验证**：能建图、页面回读 7.000 × 5.000 英寸、OPJU 保存后可重新打开。
**未验证**：字体/字号/刻度朝向/布局这几项只按规范写入属性，**没有逐项肉眼核对过**，
交付前请在 Origin 里看一眼。

## export_graphs.ogs

在 Origin 的 **Script Window** 里粘贴执行，导出位图 PNG 与矢量 PDF。
更省事的等价做法是直接用菜单 `File → Export → Graphs...`。

**已验证**：单张图、指定 `filename` 与 `path`（**路径结尾不带反斜杠**）的 expGraph 命令可用。
**未验证**：`doc -e G` 批量循环写法。第一次用请先拿一张图试。

## 已知环境坑

1. **路径结尾不要带反斜杠** —— Origin 的 `expGraph` 处理带尾反斜杠的路径会失败
   （`originpro` 源码里有注释专门提到这点）。
2. **LabTalk 逐行执行** —— 一条语句写在一行内，不要换行断开。
3. **会话锁屏时自动化会挂住** —— Origin 是 GUI 程序，锁屏/非交互会话里创建不了窗口，
   `op.lt_exec("type -a $(@V)")` 打印完就卡死。
4. **打开只读工程后导出会卡住** —— `op.open(path, readonly=True)` 之后调 `expGraph` 在本机实测会挂起，
   所以导出这一步才放到 GUI 里做。
