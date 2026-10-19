# scripts —— Origin 出图脚本

> ⛔ **先说结论：这台机器上的 Origin，任何导出都带 "demo" 水印，包括纯 GUI 手工导出。**
> 已实测：用 Origin 自己新建的空图（`File → New → Graph`）+ GUI 菜单导出，照样满屏水印。
> 所以**本目录的脚本产出的图同样不能直接投稿**，问题不在脚本。
> 详见 `../references/automation-stack.md`。
>
> 这些脚本仍然有用：它们能把"按规范建图"这一步自动化（页面 7×5 英寸、轴线 0.2、字体字号等），
> 省掉手工调参数的功夫。**导出环节得等 Origin 授权恢复正常后才有意义。**

## build_origin_figure.py

```bash
# 用示例数据
python build_origin_figure.py --demo out/figure.opju

# 用真实数据：第 0 列作 X、第 1 列作 Y
python build_origin_figure.py data.csv out/figure.opju --x 0 --y 1
```

- 数据支持 CSV/TXT（走 Origin 的 `from_file`）。
- 样式参数集中在脚本顶部的 `STYLE` 字典里，数值来自用户规范原文。
- 运行前确认 Origin 未被占用；跑完可清掉残留进程：

```powershell
Get-Process -Name Origin64 -ErrorAction SilentlyContinue | Stop-Process -Force
```

**已验证**：能建图、页面回读 7.000 × 5.000 英寸（GUI 导出对话框里显示 Graph Size = 177.80 × 127.00 mm，
对得上）、OPJU 保存后可重新打开。
**未验证**：字体/字号/刻度朝向/布局只按规范写入属性，**没有逐项肉眼核对过**。

## export_graphs.ogs

在 Origin 的 **Script Window** 里粘贴执行（或直接用菜单 `File → Export Graph...`）。
**注意**：本机 Origin 无论哪种导出都会带水印，这一步现在拿不到可投稿的图。

**已验证**：单张图、指定 `filename` 与 `path`（**路径结尾不带反斜杠**）的 expGraph 命令可用。
**未验证**：`doc -e G` 批量循环写法。第一次用请先拿一张图试。

## 已知环境坑

1. **路径结尾不要带反斜杠** —— Origin 的 `expGraph` 处理带尾反斜杠的路径会失败
   （`originpro` 源码里有注释专门提到这点）。
2. **LabTalk 逐行执行** —— 一条语句写在一行内，不要换行断开。
3. **Script Window 是文本模式** —— 实测回车不执行、Ctrl+Enter 是"插入换行"，
   本机没找到执行入口；需要跑脚本时改用菜单导出，或把脚本存成文件用别的方式执行。
4. **会话锁屏时自动化会挂住** —— Origin 是 GUI 程序，锁屏/非交互会话里创建不了窗口，
   `op.lt_exec("type -a $(@V)")` 打印完就卡死。
5. **打开只读工程后导出会卡住** —— `op.open(path, readonly=True)` 之后调 `expGraph` 在本机实测会挂起。
