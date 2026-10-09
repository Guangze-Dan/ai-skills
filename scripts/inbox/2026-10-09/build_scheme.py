# -*- coding: utf-8 -*-
"""多尺度洞室非连续裂缝围岩循环内压物理模型试验方案 —— 综合示意图（Visio）。

Built on the existing tunnel-model base figure: a central 3D model box plus four
cross-section panels connected by leader arrows.  Content distilled from the test
scheme document: four unequal axial segments (0.90/1.10/0.50/0.50 m), a Φ400 mm
main cavern under cyclic internal water pressure, one non-continuous fracture band
per segment (2 parallel inclined plates + intact rock bridge), multi-scale square
silicone-rubber small caverns / defect blocks (30/40/50 mm), and the multi-source
monitoring layout of each segment.
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
RED = (200, 30, 30)
CJK = "SimHei"
LAT = "Times New Roman"

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
    elif fn.lower().endswith("scheme_figure.vsdx"):
        d.Saved = True
        d.Close()
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
    if fill:
        setfill(s, fill)
    else:
        nofill(s)
    setline(s, line, wt, dash)
    return s


def text(cx, cy, txt, size=14, color=BLACK, font=CJK, boxw=200, boxh=36, bg=None):
    s = rrect(cx - boxw / 2.0, cy - boxh / 2.0, cx + boxw / 2.0, cy + boxh / 2.0)
    if bg:
        setfill(s, bg)
    else:
        nofill(s)
    noline(s)
    s.Text = txt
    s.Cells("Char.Font").Formula = '"%s"' % font
    s.Cells("Char.Size").Formula = "%.1f pt" % size
    s.Cells("Char.Color").Formula = rgb(color)
    s.Cells("VerticalAlign").Formula = "1"
    s.Cells("Para.HorzAlign").Formula = "1"
    return s


def leader(x1, y1, x2, y2, wt=0.8, c=BLACK):
    ln = rline(x1, y1, x2, y2)
    setline(ln, c, wt)
    return ln


def arrow(x1, y1, x2, y2, color=(126, 100, 158), wt=2.5):
    ln = rline(x1, y1, x2, y2)
    setline(ln, color, wt)
    ln.Cells("EndArrow").Formula = "13"
    return ln


def band(cx, cy, ang=45.0, ln=100.0, gap=30.0, col=RED, wt=4.5):
    """Pair of parallel inclined fracture plates (one band)."""
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    for s in (-0.5, 0.5):
        x1 = cx - ux * ln / 2 + s * px * gap
        y1 = cy - uy * ln / 2 + s * py * gap
        x2 = cx + ux * ln / 2 + s * px * gap
        y2 = cy + uy * ln / 2 + s * py * gap
        setline(rline(x1, y1, x2, y2), col, wt)


def rosette(cx, cy, s=10.0):
    for ang in (0, 45, 90):
        a = math.radians(ang)
        setline(rline(cx - s * math.cos(a), cy + s * math.sin(a),
                      cx + s * math.cos(a), cy - s * math.sin(a)), (25, 25, 25), 1.0)


def dot(cx, cy, r, fill):
    e = roval(cx, cy, r, r)
    setfill(e, fill)
    noline(e)
    return e


def square(cx, cy, s, fill, edge):
    r = rrect(cx - s / 2.0, cy - s / 2.0, cx + s / 2.0, cy + s / 2.0)
    setfill(r, fill)
    setline(r, edge, 1.0)
    return r


# ============================ palette ============================
SEG_TINT = [(250, 236, 234), (240, 236, 248), (232, 246, 234), (230, 244, 248)]
SEG_EDGE = [(178, 45, 40), (104, 78, 160), (52, 124, 66), (40, 126, 146)]
BOXFACE = (236, 236, 236)

# ============================ centre 3D model box ============================
L, R, T, B = 442, 1130, 178, 612
DX, DY = 118, 118
SC = (R - L) / 3000.0                       # px per mm along the axis
BOUND = [L, 648, 901, 1015, R]              # 900 / 1100 / 500 / 500 mm
SEGC = [(BOUND[i] + BOUND[i + 1]) / 2.0 for i in range(4)]

poly([(L, T), (R, T), (R + DX, T - DY), (L + DX, T - DY)], fill=(243, 243, 243), wt=1.5)
poly([(R, T), (R + DX, T - DY), (R + DX, B - DY), (R, B)], fill=(233, 233, 233), wt=1.5)
f = rrect(L, T, R, B)
setfill(f, BOXFACE)
setline(f, BLACK, 1.5)

for i in range(4):
    rb = rrect(BOUND[i], T, BOUND[i + 1], B)
    setfill(rb, SEG_TINT[i])
    noline(rb)

for i in range(4):
    text(SEGC[i], 246, ("I", "II", "III", "IV")[i], 30, SEG_EDGE[i], boxw=140, boxh=52)

# tunnel (Φ400) cross-sections along the axis
TUNNEL_Y = 423
for cx, rx, fc, oc, wtt, dsh in [(505, 18, (255, 255, 255), BLACK, 1.4, True),
                                 (627, 15, (255, 255, 255), (70, 70, 70), 1.0, True),
                                 (742, 15, (255, 255, 255), (70, 70, 70), 1.0, True),
                                 (858, 15, (255, 255, 255), (70, 70, 70), 1.0, True),
                                 (974, 15, (255, 255, 255), (70, 70, 70), 1.0, True),
                                 (1191, 15, (255, 255, 255), BLACK, 1.4, False)]:
    e = roval(cx, TUNNEL_Y, rx, 52)
    setfill(e, fc)
    setline(e, oc, wtt, dash=dsh)

# one non-continuous fracture band per segment (2 parallel inclined plates)
for i in range(4):
    band(SEGC[i], 312, ang=45, ln=96, gap=28)
# multi-scale square silicone-rubber small caverns / defect blocks
BLK = (168, 204, 228)
for cx in (700, 930, 1050):
    square(cx, 386, 17, BLK, (48, 100, 140))
    square(cx, 462, 17, BLK, (48, 100, 140))

# black grid / hidden depth lines on top so nothing crosses them
for xd in BOUND[1:4]:
    setline(rline(xd, T, xd, B), BLACK, 0.9, dash=True)
    setline(rline(xd, T, xd + DX, T - DY), BLACK, 0.9, dash=True)
for xd in (L, 648, 901, 1015):
    setline(rline(xd, B, xd + DX, B - DY), BLACK, 0.9, dash=True)
setline(rline(L, 493, R + DX, 493), BLACK, 1.5, dash=True)

# box annotations
text(600, 556, "主洞室 Φ400", 15, BLACK, boxw=250, boxh=36, bg=(255, 255, 255))
leader(600, 538, 636, 466)
text(830, 556, "缺陷块 30~50 mm", 15, BLACK, boxw=250, boxh=36, bg=(255, 255, 255))
leader(830, 538, 880, 472)
text(1188, 292, "裂缝带", 15, BLACK, boxw=160, boxh=34, bg=(247, 247, 247))
leader(1152, 292, 1090, 303)
text(1188, 352, "循环内压 P", 15, BLACK, boxw=180, boxh=34, bg=(247, 247, 247))
leader(1188, 370, 1191, 396)

# dimensions
text(861, 20, "多尺度洞室非连续裂缝围岩循环内压物理模型试验方案", 20, BLACK, boxw=800, boxh=34)
text(861, 45, "洞轴四分段 0.90 / 1.10 / 0.50 / 0.50 m　|　围岩抗压强度统一 10 MPa　|　循环内压加载",
     13, BLACK, boxw=880, boxh=26)

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

# ============================ four research sections ============================
def panel(x0, y0, x1, y1, idx, title, cy):
    p = rrect(x0, y0, x1, y1)
    setfill(p, SEG_TINT[idx])
    setline(p, BLACK, 1.4)
    hb = rrect(x0, y0, x1, y0 + 34)
    setfill(hb, SEG_EDGE[idx])
    noline(hb)
    text((x0 + x1) / 2.0, y0 + 17, title, 17, (255, 255, 255), boxw=(x1 - x0) - 10, boxh=30)
    c = roval((x0 + x1) / 2.0, cy, 47, 47)
    setfill(c, (255, 255, 255))
    setline(c, BLACK, 1.4)
    fr = rrect(x0, y0, x1, y1)
    nofill(fr)
    setline(fr, BLACK, 1.4)


# --- 剖面 I : 裂缝带起裂 -----------------------------------------------------
panel(2, 58, 402, 312, 0, "剖面 I｜裂缝带起裂", 198)
band(140, 172, ang=45, ln=88, gap=28)
text(72, 130, "裂缝板", 16, BLACK, boxw=150, boxh=32)
leader(95, 146, 126, 160)
text(78, 254, "岩桥", 16, BLACK, boxw=130, boxh=32)
leader(100, 246, 140, 191)

# --- 剖面 II : 洞周应变花与光纤 ----------------------------------------------
panel(2, 355, 402, 608, 1, "剖面 II｜洞周应变与光纤", 494)
for rr in (62, 74, 86):
    e = roval(202, 494, rr, rr)
    nofill(e)
    setline(e, (48, 104, 176), 1.0, dash=True)
for ang in (45, 135, 225, 315):
    a = math.radians(ang)
    rosette(202 + 47 * math.cos(a), 494 - 47 * math.sin(a))
text(84, 585, "应变花 ×4", 16, BLACK, boxw=170, boxh=32)
leader(120, 572, 168, 524)
text(322, 585, "FBG 光纤环 ×3", 16, BLACK, boxw=210, boxh=32)
leader(300, 572, 250, 434)

# --- 剖面 III : 声发射监测 ---------------------------------------------------
panel(1319, 356, 1720, 608, 2, "剖面 III｜声发射监测", 494)
for ang, rr in ((30, 76), (120, 76), (210, 76), (300, 76),
                (75, 100), (165, 100), (255, 100), (345, 100)):
    a = math.radians(ang)
    dot(1520 + rr * math.cos(a), 494 - rr * math.sin(a), 6, (198, 58, 44))
text(1600, 578, "AE 传感器 ×8", 16, BLACK, boxw=220, boxh=32)
leader(1560, 570, 1548, 545)

# --- 剖面 IV : 缺陷块与岩桥 --------------------------------------------------
panel(1319, 58, 1720, 318, 3, "剖面 IV｜双缺陷块与岩桥", 198)
for base_x in (1412, 1588):
    square(base_x, 198, 26, BLK, (48, 100, 140))
    square(base_x + 36, 198, 26, BLK, (48, 100, 140))
text(1400, 108, "缺陷块 40 mm", 16, BLACK, boxw=230, boxh=32)
leader(1400, 124, 1412, 185)
text(1440, 286, "岩桥 40 mm", 16, BLACK, boxw=200, boxh=32)
leader(1455, 272, 1444, 214)

# ============================ leader arrows ============================
arrow(560, 385, 420, 215)
arrow(700, 455, 410, 512)
arrow(958, 455, 1300, 458)
arrow(1078, 395, 1300, 205)

doc.Pages.Item(1).Export(r"D:\Zcode\.zcode\workspace\default\vimg\render_scheme.png")
doc.SaveAs(r"D:\Zcode\.zcode\workspace\default\scheme_figure.vsdx")
print("shapes:", pg.Shapes.Count, "-> saved scheme_figure.vsdx")
