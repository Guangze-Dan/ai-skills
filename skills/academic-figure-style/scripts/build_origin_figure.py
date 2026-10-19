"""按《origin论文出图格式》把数据画成图，并保存为 OPJU 工程。

为什么只存 OPJU、不在这里导出图片
----------------------------------
见 references/automation-stack.md：经由自动化接口（originpro / OriginExt / COM）触发的
Origin 导出会被加上 "demo" 水印，而手工在 GUI 里导出不受影响。
所以本脚本只负责"建图 + 存工程"，导出交给 scripts/export_graphs.ogs 在 Origin 的
Script Window 里执行（或在 GUI 菜单里点"导出图形"）。

用法
----
    python build_origin_figure.py <数据文件.csv> <输出.opju> [--x 0] [--y 1]
    python build_origin_figure.py --demo <输出.opju>

    --x / --y 指定用作 X/Y 的列号（0 起）。

样式常量见下方 STYLE —— 数值全部来自用户规范原文，不要"取个大概"。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import originpro as op

# --------------------------------------------------------------------------
# 规范参数（源自 origin论文出图格式.docx）
# --------------------------------------------------------------------------
STYLE = {
    # 1. 图纸尺寸 7cm x 5cm 的点线图；对话框里填的是宽度 7 / 高度 5 / 单位英寸
    "page_w_in": 7.0,
    "page_h_in": 5.0,
    # 2. 轴线 0.2，主/次刻度样式都朝内
    "axis_width_pt": 0.2,
    #    x.tickstyle / y.tickstyle 的取值含义尚未最终确认（见 automation-stack.md），
    #    导出后请肉眼核对刻度是朝内。0/1/2/3 四个值都合法。
    "tick_style": 2,
    # 3. 中文宋体、西文 Times New Roman、变量斜体；标题 26、其余 22
    "latin_font": "Times New Roman",
    "cjk_font": "SimSun",          # 宋体
    "label_pt": 22,                 # 刻度数字等"其余"
    "title_pt": 26,                 # 轴标题
    # 6. 线条突出重点 —— 重要曲线用强调色
    "emphasis_rgb": (205, 35, 30),  # 红
    "normal_rgb": (0, 0, 0),
}


def apply_page_size(gp) -> tuple[float, float]:
    """把图窗页面设成规范尺寸。

    坑：LabTalk 的 page.width / page.height 单位是**像素**，不是英寸，
    直接写 page.width=7 会把页面压成 7 像素。必须乘上页面分辨率 page.resx / page.resy。
    """
    gp.activate()
    op.lt_exec("page.updatetoprinter=0;page.kar=0;")   # 解锁尺寸、关掉保持比例
    gp.obj.LT_execute(
        f"page.width=({STYLE['page_w_in']:g})*page.resx;"
        f"page.height=({STYLE['page_h_in']:g})*page.resy;doc -uw;"
    )
    return float(gp.obj.GetWidth()), float(gp.obj.GetHeight())   # 回读单位是英寸


def apply_axis_style(gl) -> None:
    """轴线粗细、刻度、字号、西文字体。"""
    font_code = int(round(float(op.lt_float(f"font({STYLE['latin_font']})"))))

    for axis in ("x", "y"):
        gl.set_float(f"{axis}.tickthickness", STYLE["axis_width_pt"])
        gl.set_float(f"{axis}.tickstyle", STYLE["tick_style"])
        gl.set_float(f"{axis}.label.pt", STYLE["label_pt"])
        gl.set_int(f"{axis}.label.font", font_code)
        # 4. 坐标轴两端都要有刻度数字（对侧也显示轴与刻度）
        gl.set_int(f"{axis}.opposite", 1)
    op.lt_exec("doc -uw;")


def build(csv_path: Path | None, out_opju: Path, xcol: int, ycol: int,
          demo: bool) -> None:
    op.set_show(False)

    ws = op.new_sheet("w", lname="data")
    if demo:
        ws.from_list(0, [1.0, 1.5, 2.0, 2.5, 3.0], lname="time")
        ws.from_list(1, [1.0, 1.5, 2.0, 2.5, 3.0], lname="stress")
    else:
        if not csv_path or not csv_path.exists():
            raise SystemExit(f"数据文件不存在: {csv_path}")
        ws.from_file(str(csv_path))

    ws.activate()
    op.lt_exec(f"plotxy iy:=({xcol + 1},{ycol + 1}) plot:=200;")   # LabTalk 列号从 1 起
    gp = op.find_graph("Graph1")
    gl = gp[0]
    gl.rescale()

    # 5. 布局尽量布满图纸
    op.lt_exec("layer -a;")      # 调整图层至页面大小

    w_in, h_in = apply_page_size(gp)
    apply_axis_style(gl)

    out_opju.parent.mkdir(parents=True, exist_ok=True)
    op.save(str(out_opju))
    print(f"页面回读: {w_in:.3f} x {h_in:.3f} 英寸（目标 {STYLE['page_w_in']} x {STYLE['page_h_in']}）")
    print(f"已保存: {out_opju}")
    print("下一步：在 Origin 里打开该 OPJU，用 scripts/export_graphs.ogs 导出（别用脚本导出，会带水印）")


def main() -> int:
    ap = argparse.ArgumentParser(description="按规范建 Origin 图并存 OPJU")
    ap.add_argument("csv", nargs="?", help="数据文件（CSV/TXT）")
    ap.add_argument("out", help="输出的 .opju 路径")
    ap.add_argument("--x", type=int, default=0, help="X 列号（0 起）")
    ap.add_argument("--y", type=int, default=1, help="Y 列号（0 起）")
    ap.add_argument("--demo", action="store_true", help="用内置示例数据，忽略 csv")
    a = ap.parse_args()

    build(Path(a.csv) if a.csv else None, Path(a.out), a.x, a.y, a.demo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
