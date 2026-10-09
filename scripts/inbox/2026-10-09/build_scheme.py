# -*- coding: utf-8 -*-
"""多尺度洞室非连续裂缝围岩循环内压物理模型试验方案 —— 综合示意图（Visio）。

Base layout: a central 3D model box + four cross-section panels joined by leader
arrows.  Every detail follows the test-scheme document (text + its figures):

  * box   : 3.0 x 1.6 x 1.8 m, four unequal axial casts 0.90 / 1.10 / 0.50 / 0.50 m,
            Φ400 mm main cavern (UPVC, cyclic internal water pressure) running along
            the axis, one non-continuous fracture band per segment (2 parallel
            inclined HDPE plates + intact rock bridge), multi-scale square silicone
            rubber small caverns (30/40/50 mm) on both flanks of the cavern.
  * panels: the document's section template -- ±30° fracture-band sector on top
            (defect blocks keep clear of it), Φ400 cavern with concentric measuring
            rings, inclined plate pair with the rock-bridge gauge array, square
            defect blocks on the flanks, and the "400 mm below the cavern bottom"
            boundary-effect exclusion strip.
"""
import math
import win32com.client as w

PX = 100.0
IMG_H = 683.0


def W(px):
    return px / PX


def H(py):
    return (IMG_H - py) / PX


def rgb(c):
    return "RGB(%d,%d,%d)" % c


BLACK = (0, 0, 0)
RED = (205, 35, 30)
CJK = "SimHei"
LAT = "Times New Roman"
TUN = (30, 78, 136)          # cavern ring
TUN_L = (126, 184, 222)      # outer cavern ring
GRN_F = (198, 228, 198)      # defect block fill
GRN_E = (56, 138, 72)

TARGET = r"D:\Zcode\.zcode\workspace\default\scheme_figure.vsdx"

app = w.Dispatch("Visio.Application")
app.Visible = 1
doc = None
blanks = []
for d in list(app.Documents):
    try:
        fn = d.FullName
    except Exception:
        continue
    if fn.lower() == TARGET.lower():
        doc = d
    elif fn == "":
        blanks.append(d)
if doc is None:
    doc = blanks.pop(0) if blanks else app.Documents.Add("")
for d in blanks:
    try:
        d.Saved = True
        d.Close()
    except Exception:
        pass

pg = doc.Pages.Item(1)
pg.PageSheet.Cells("PageWidth").Formula = "17.23 in"
pg.PageSheet.Cells("PageHeight").Formula = "6.83 in"
while pg.Shapes.Count > 0:
    pg.Shapes.Item(1).Delete()


def rline(x1, y1, x2, y2):
    return pg.DrawLine(W(x1), H(y1), W(x2), H(y2))


def rrect(x1, y1, x2, y2):
    return pg.DrawRectangle(W(x1), H(y1), W(x2), H(y2))


def roval(cx, cy, rx, ry):
    return pg.DrawOval(W(cx - rx), H(cy + ry), W(cx + rx), H(cy - ry))


def setfill(s, c):
    s.Cells("FillPattern").Formula = "1"
    s.Cells("FillForegnd").Formula = rgb(c)


def setline(s, c, wt=1.0, dash=False):
    s.Cells("LineColor").Formula = rgb(c)
    s.Cells("LineWeight").Formula = "%.2f pt" % wt
    s.Cells("LinePattern").Formula = "2" if dash else "1"


def noline(s):
    s.Cells("LinePattern").Formula = "0"


def nofill(s):
    s.Cells("FillPattern").Formula = "0"


def poly(pts, fill=None, line=BLACK, wt=1.0, dash=False):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    s = rrect(x0, y0, x1, y1)
    allp = list(pts) + [pts[0]]
    for i in range(1, len(allp) + 1):
        s.CellsSRC(10, i, 0).Formula = "%.4f" % (W(allp[i - 1][0]) - W(x0))
        s.CellsSRC(10, i, 1).Formula = "%.4f" % (H(allp[i - 1][1]) - H(y1))
    cur = s.RowCount(10)
    while cur > len(allp):
        try:
            s.DeleteRow(10, cur)
        except Exception:
            break
        cur -= 1
    setfill(s, fill) if fill else nofill(s)
    setline(s, line, wt, dash)
    return s


def text(cx, cy, txt, size=14, color=BLACK, font=CJK, boxw=200, boxh=36, bg=None):
    s = rrect(cx - boxw / 2.0, cy - boxh / 2.0, cx + boxw / 2.0, cy + boxh / 2.0)
    setfill(s, bg) if bg else nofill(s)
    noline(s)
    s.Text = txt
    s.Cells("Char.Font").Formula = '"%s"' % font
    s.Cells("Char.Size").Formula = "%.1f pt" % size
    s.Cells("Char.Color").Formula = rgb(color)
    s.Cells("VerticalAlign").Formula = "1"
    s.Cells("Para.HorzAlign").Formula = "1"
    return s


def leader(x1, y1, x2, y2, wt=0.8, c=BLACK, dash=False):
    ln = rline(x1, y1, x2, y2)
    setline(ln, c, wt, dash)
    return ln


def arrow(x1, y1, x2, y2, color=(126, 100, 158), wt=2.5):
    ln = rline(x1, y1, x2, y2)
    setline(ln, color, wt)
    ln.Cells("EndArrow").Formula = "13"
    return ln


def band(cx, cy, ang=32.0, ln=58.0, gap=24.0, col=RED, wt=4.0):
    """Two parallel inclined fracture plates; returns the perpendicular unit vector."""
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    for s in (-0.5, 0.5):
        setline(rline(cx - ux * ln / 2 + s * px * gap, cy - uy * ln / 2 + s * py * gap,
                      cx + ux * ln / 2 + s * px * gap, cy + uy * ln / 2 + s * py * gap), col, wt)
    return (px, py)


def dot(cx, cy, r, fill, edge=None):
    e = roval(cx, cy, r, r)
    setfill(e, fill)
    noline(e) if edge is None else setline(e, edge, 0.8)
    return e


SZ = {"30": 26.0, "40": 33.0, "50": 40.0}   # block size classes (30/40/50 mm)


def blk(cx, cy, lab):
    """Square silicone-rubber defect block, drawn at its real size class."""
    s = SZ[lab]
    r = rrect(cx - s / 2.0, cy - s / 2.0, cx + s / 2.0, cy + s / 2.0)
    setfill(r, GRN_F)
    setline(r, GRN_E, 2.0)
    text(cx, cy, lab, 10.5 + (s - 26) * 0.2, (26, 84, 40), boxw=s + 6, boxh=s * 0.8)


# ============================ palette ============================
SEG_TINT = [(252, 238, 238), (240, 236, 248), (232, 246, 234), (230, 244, 248)]
SEG_EDGE = [(178, 45, 40), (104, 78, 160), (52, 124, 66), (40, 126, 146)]
BOXFACE = (236, 236, 236)

# ============================ centre 3D model box ============================
L, R, T, B = 442, 1130, 178, 612
DX, DY = 118, 118
BOUND = [L, 648, 901, 1015, R]                  # 900 / 1100 / 500 / 500 mm
SEGC = [(BOUND[i] + BOUND[i + 1]) / 2.0 for i in range(4)]
NUM = ("I", "II", "III", "IV")
TUBE_Y = 423

poly([(L, T), (R, T), (R + DX, T - DY), (L + DX, T - DY)], fill=(243, 243, 243), wt=1.5)
poly([(R, T), (R + DX, T - DY), (R + DX, B - DY), (R, B)], fill=(233, 233, 233), wt=1.5)
f = rrect(L, T, R, B)
setfill(f, BOXFACE)
setline(f, BLACK, 1.5)
for i in range(4):
    rb = rrect(BOUND[i], T, BOUND[i + 1], B)
    setfill(rb, SEG_TINT[i])
    noline(rb)

# one inclined fracture-plate pair per segment
for i in range(4):
    band(SEGC[i], 308, ang=32, ln=62, gap=26, wt=4.0)

# main cavern Φ400 (P): tube along the axis + end openings
tb = rrect(505, TUBE_Y - 52, 1191, TUBE_Y + 52)
setfill(tb, (223, 239, 250))
noline(tb)
for yy in (TUBE_Y - 52, TUBE_Y + 52):
    setline(rline(505, yy, 1191, yy), (58, 112, 172), 1.1, dash=True)
for cx in (505, 1191):
    e = roval(cx, TUBE_Y, 18, 52)
    setfill(e, (196, 224, 244))
    setline(e, TUN, 1.6)
text(700, 515, "Φ400 (P)", 16, TUN, boxw=190, boxh=34)
leader(700, 498, 700, 478)

# one identical dashed cross-section ellipse per segment (four in total)
for i in range(4):
    e = roval(SEGC[i], TUBE_Y, 16, 52)
    setfill(e, (255, 255, 255))
    setline(e, (62, 62, 62), 1.1, dash=True)

for i in range(4):
    text(SEGC[i], 250, NUM[i], 30, SEG_EDGE[i], boxw=140, boxh=52)

# black grid lines on top so nothing crosses them
for xd in BOUND[1:4]:
    setline(rline(xd, T, xd, B), BLACK, 0.9, dash=True)
    setline(rline(xd, T, xd + DX, T - DY), BLACK, 0.9, dash=True)

# box annotations
text(1188, 288, "裂缝带", 15, BLACK, boxw=150, boxh=34)
leader(1152, 294, 1112, 310)
text(1188, 352, "循环内压 P", 15, BLACK, boxw=170, boxh=34)
leader(1188, 372, 1191, 400)

# ============================ titles ============================
text(861, 20, "多尺度洞室非连续裂缝围岩循环内压物理模型试验方案", 20, BLACK, boxw=860, boxh=34)
text(861, 45, "洞轴四分段 0.90 / 1.10 / 0.50 / 0.50 m　|　围岩抗压强度统一 10 MPa　|　循环内压加载",
     13, BLACK, boxw=900, boxh=26)

# dimensions
DIMY = 645
setline(rline(L, DIMY, R, DIMY), BLACK, 1.0)
for xd in BOUND:
    a = rline(xd - 15, DIMY, xd, DIMY)
    setline(a, BLACK, 1.0)
    a.Cells("EndArrow").Formula = "13"
    b2 = rline(xd + 15, DIMY, xd, DIMY)
    setline(b2, BLACK, 1.0)
    b2.Cells("EndArrow").Formula = "13"
for i, lab in enumerate(("900", "1100", "500", "500")):
    text(SEGC[i], DIMY + 22, lab, 15, BLACK, LAT, boxw=140, boxh=36)
text(1200, 668, "Unit: mm", 14, BLACK, boxw=180, boxh=32)

ln = rline(1262, 60, 1262, 494)
setline(ln, BLACK, 1.2)
ln.Cells("BeginArrow").Formula = "13"
ln.Cells("EndArrow").Formula = "13"
text(1300, 277, "1800", 15, BLACK, LAT, boxw=90, boxh=36)
ln = rline(1152, 634, 1272, 514)
setline(ln, BLACK, 1.2)
ln.Cells("BeginArrow").Formula = "13"
ln.Cells("EndArrow").Formula = "13"
text(1252, 578, "1600", 15, BLACK, LAT, boxw=90, boxh=36)


# ============================ section template ============================
def panel(x0, y0, x1, y1, idx, title, cx, cy, band_top, lab_x=None):
    cxm = (x0 + x1) / 2.0
    p = rrect(x0, y0, x1, y1)
    setfill(p, SEG_TINT[idx])
    setline(p, BLACK, 1.2)

    # ±30° fracture-band sector (defect blocks keep clear of it)
    top = y0 + 40
    dxs = (cy - top) * math.tan(math.radians(30))
    poly([(cx, cy), (cx - dxs, top), (cx + dxs, top)],
         fill=(252, 236, 236), line=(226, 138, 138), wt=0.9, dash=True)
    lx = lab_x if lab_x is not None else cx - dxs + 62
    text(lx, top + 15, "裂缝带 ±30°", 13, (176, 46, 40), boxw=140, boxh=26)

    # boundary-effect exclusion strip below the cavern
    r = rrect(x0 + 3, band_top, x1 - 3, y1 - 3)
    setfill(r, (228, 228, 228))
    noline(r)
    text(cxm, (band_top + y1) / 2.0, "洞底以下 400 mm", 12.5, (72, 72, 72),
         boxw=(x1 - x0) - 20, boxh=26)

    # concentric measuring rings + Φ400 cavern
    for rr in (66, 82):
        e = roval(cx, cy, rr, rr)
        nofill(e)
        setline(e, (152, 152, 152), 1.0, dash=True)
    e = roval(cx, cy, 54, 54)
    nofill(e)
    setline(e, TUN_L, 1.6)
    e = roval(cx, cy, 47, 47)
    setfill(e, (255, 255, 255))
    setline(e, TUN, 2.4)
    text(cx, cy, "Φ400", 15, TUN, boxw=110, boxh=30)

    # inclined plate pair + rock-bridge gauge array
    px, py = band(cx - 30, cy - 64, ang=32, ln=58, gap=24, wt=4.0)
    for k in range(5):
        off = -9 + 4.5 * k
        dot(cx - 30 + px * off, cy - 64 + py * off, 2.4, (128, 62, 152))

    # header + frame on top
    hb = rrect(x0, y0, x1, y0 + 34)
    setfill(hb, SEG_EDGE[idx])
    noline(hb)
    text(cxm, y0 + 17, title, 17, (255, 255, 255), boxw=(x1 - x0) - 10, boxh=30)
    fr = rrect(x0, y0, x1, y1)
    nofill(fr)
    setline(fr, SEG_EDGE[idx], 2.0)


# --- 剖面 I : 裂缝带起裂 -----------------------------------------------------
panel(2, 58, 402, 312, 0, "剖面 I｜裂缝带起裂", 202, 232, 279)
blk(202 - 76, 232 - 76, "30")
blk(202 - 102, 232, "50")
blk(202 + 102, 232, "40")
text(306, 152, "板 80×2 mm", 14, RED, boxw=170, boxh=28)
leader(306, 166, 218, 182)

# --- 剖面 II : 洞周应变花与光纤 ----------------------------------------------
panel(2, 355, 402, 608, 1, "剖面 II｜洞周应变与光纤", 202, 528, 575)
for rr in (56, 68, 80):
    e = roval(202, 528, rr, rr)
    nofill(e)
    setline(e, (232, 152, 40), 1.1, dash=True)
for ang in (40, 140, 220, 320):
    a = math.radians(ang)
    rx, ry = 202 + 47 * math.cos(a), 528 - 47 * math.sin(a)
    for d in (0, 45, 90):
        b = math.radians(d)
        setline(rline(rx - 8 * math.cos(b), ry + 8 * math.sin(b),
                      rx + 8 * math.cos(b), ry - 8 * math.sin(b)), (240, 140, 30), 1.0)
blk(202 - 102, 528, "40")
blk(202 + 102, 528, "40")
blk(202 + 76, 528 - 76, "40")
text(330, 418, "FBG ×3", 13, (196, 118, 20), boxw=130, boxh=26)
text(322, 470, "应变花", 14, (196, 118, 20), boxw=150, boxh=26)
leader(292, 478, 246, 502)

# --- 剖面 III : 声发射监测 ---------------------------------------------------
panel(1319, 356, 1720, 608, 2, "剖面 III｜声发射监测", 1520, 528, 575, lab_x=1388)
AE = [(1400, 590), (1640, 590), (1398, 480), (1642, 480),
      (1475, 432), (1518, 432), (1561, 432), (1604, 432)]
for (ax, ay) in AE:
    leader(ax, ay, 1490, 462, 0.7, (120, 172, 214), True)
for i, (ax, ay) in enumerate(AE, 1):
    sq = rrect(ax - 15, ay - 13, ax + 15, ay + 13)
    setfill(sq, (255, 255, 255))
    setline(sq, (40, 96, 152), 1.6)
    text(ax, ay, "#%d" % i, 11.5, (30, 78, 132), boxw=34, boxh=24)
dot(1490, 462, 9, (238, 96, 60), (176, 40, 24))
e = roval(1490, 462, 17, 17)
nofill(e)
setline(e, (214, 96, 60), 1.2, dash=True)
blk(1596, 462, "30")
blk(1418, 528, "40")
blk(1622, 528, "50")
text(1450, 562, "AE ×8", 14, (40, 96, 152), boxw=130, boxh=26)

# --- 剖面 IV : 双缺陷块与岩桥 ------------------------------------------------
panel(1319, 58, 1720, 318, 3, "剖面 IV｜双缺陷块与岩桥", 1520, 238, 285)
blk(1520 - 100, 238, "40")
blk(1520 - 148, 238, "40")
text(1396, 180, "岩桥 40 mm", 14, GRN_E, boxw=190, boxh=28)
leader(1396, 194, 1396, 220)
blk(1520 + 100, 238, "40")

# ============================ leader arrows ============================
arrow(560, 385, 420, 215)
arrow(700, 455, 410, 512)
arrow(958, 455, 1300, 458)
arrow(1078, 395, 1300, 205)

doc.Pages.Item(1).Export(r"D:\Zcode\.zcode\workspace\default\vimg\render_scheme.png")
doc.SaveAs(TARGET)
print("shapes:", pg.Shapes.Count, "-> saved scheme_figure.vsdx")
