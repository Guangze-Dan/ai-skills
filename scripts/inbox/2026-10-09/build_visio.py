# -*- coding: utf-8 -*-
"""Reproduce the tunnel 3D-model schematic figure in Visio (COM automation)."""
import json
import math
import win32com.client as w

PX = 100.0          # image pixels per inch
IMG_H = 683.0       # source image height in px

# red crack polylines extracted from the source figure (see extract_red.py)
REDPATHS = json.load(open(r"D:\Zcode\.zcode\workspace\default\redpaths.json", encoding="utf-8"))


def W(px):
    return px / PX


def H(py):
    return (IMG_H - py) / PX


def rgb(c):
    return "RGB(%d,%d,%d)" % c


RED = (190, 20, 19)
PURPLE = (126, 100, 158)
BLACK = (0, 0, 0)
GRAY = (236, 236, 236)

app = w.Dispatch("Visio.Application")
app.Visible = 1
doc = app.ActiveDocument
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


def poly(pts, fill=None, line=BLACK, wt=1.0, dash=False, close=True):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    x1, y1 = max(xs), max(ys)
    s = rrect(x0, y0, x1, y1)
    nrow = 4 + (1 if close else 0)
    # rows: MoveTo + LineTo... ; set extra rows for close if needed
    allp = list(pts) + ([pts[0]] if close else [])
    for i in range(1, len(allp) + 1):
        s.CellsSRC(10, i, 0).Formula = "%.4f" % (W(allp[i - 1][0]) - W(x0))
        s.CellsSRC(10, i, 1).Formula = "%.4f" % (H(allp[i - 1][1]) - H(y1))
    # remove unused rows
    total = len(allp)
    while total < 5:
        try:
            s.DeleteRow(10, total + 1)
        except Exception:
            break
        break
    if fill:
        setfill(s, fill)
    else:
        nofill(s)
    setline(s, line, wt, dash)
    return s


def polyline(pts, color=RED, wt=1.4, dash=False):
    shapes = []
    for i in range(len(pts) - 1):
        ln = rline(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
        setline(ln, color, wt, dash)
        shapes.append(ln)
    return shapes


def text(cx, cy, txt, size=14, color=BLACK, font="Times New Roman",
         boxw=140, boxh=40, angle=None):
    s = rrect(cx - boxw / 2.0, cy - boxh / 2.0, cx + boxw / 2.0, cy + boxh / 2.0)
    nofill(s)
    noline(s)
    s.Text = txt
    s.Cells("Char.Font").Formula = '"%s"' % font
    s.Cells("Char.Size").Formula = "%.1f pt" % size
    s.Cells("Char.Color").Formula = rgb(color)
    s.Cells("VerticalAlign").Formula = "1"
    s.Cells("Para.HorzAlign").Formula = "1"
    if angle is not None:
        s.Cells("Angle").Formula = "%.1f deg" % angle
    return s


def arrow(x1, y1, x2, y2, color=PURPLE, wt=2.5):
    ln = rline(x1, y1, x2, y2)
    setline(ln, color, wt)
    ln.Cells("EndArrow").Formula = "13"
    ln.Cells("BeginArrow").Formula = "0"
    return ln


CIRCLES = {"p3": (206, 180), "p4": (206, 477), "p1": (1523, 186), "p2": (1522, 477)}
PANEL_R = 47


def _snap_circle(pts, cx, cy, r):
    """Push an endpoint that stops just short of a tunnel circle onto its rim, so the
    red line meets the black edge without crossing it."""
    for ei, ni in ((0, 1), (-1, -2)):
        ex, ey = pts[ei]
        nx, ny = pts[ni]
        if math.hypot(ex - cx, ey - cy) > r + 16:
            continue
        dx, dy = ex - nx, ey - ny
        n = math.hypot(dx, dy)
        if n < 1e-6:
            continue
        dx, dy = dx / n, dy / n
        for t in range(1, 40):
            qx, qy = ex + dx * t, ey + dy * t
            if math.hypot(qx - cx, qy - cy) <= r - 6:
                pts[ei] = [round(qx, 1), round(qy, 1)]
                break
    return pts


def draw_red(name, wt=1.0):
    circ = CIRCLES.get(name)
    for path in REDPATHS[name]:
        pts = [list(p) for p in path]
        if circ:
            pts = _snap_circle(pts, circ[0], circ[1], PANEL_R)
        polyline([(p[0], p[1]) for p in pts], RED, wt)


# ============================ PANELS ============================
GREEN_BG = (235, 241, 223)
BLUE_BG = (219, 238, 243)
M10 = (157, 187, 97)
M75 = (75, 172, 198)

# --- Cross-section 3 (top-left) ---
p = rrect(2, 58, 402, 312)
setfill(p, GREEN_BG)
setline(p, BLACK, 1.4)
draw_red("p3", 1.0)
c = roval(206, 180, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
fr = rrect(2, 58, 402, 312)
nofill(fr)
setline(fr, BLACK, 1.4)
b = rrect(291, 258, 397, 302)
setfill(b, M10)
noline(b)
text(344, 280, "M10", 19, BLACK, boxw=120, boxh=50)
text(202, 30, "Cross-section 3", 19, BLACK, boxw=380, boxh=44)

# --- Cross-section 4 (bottom-left) ---
p = rrect(2, 355, 402, 608)
setfill(p, GREEN_BG)
setline(p, BLACK, 1.4)
draw_red("p4", 1.0)
c = roval(206, 477, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
fr = rrect(2, 355, 402, 608)
nofill(fr)
setline(fr, BLACK, 1.4)
b = rrect(291, 554, 397, 598)
setfill(b, M10)
noline(b)
text(344, 576, "M10", 19, BLACK, boxw=120, boxh=50)
text(202, 640, "Cross-section 4", 19, BLACK, boxw=380, boxh=44)

# --- Cross-section 1 (top-right) ---
p = rrect(1319, 58, 1720, 318)
setfill(p, GREEN_BG)
setline(p, BLACK, 1.4)
draw_red("p1", 1.0)
c = roval(1523, 186, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
fr = rrect(1319, 58, 1720, 318)
nofill(fr)
setline(fr, BLACK, 1.4)
b = rrect(1608, 261, 1714, 305)
setfill(b, M10)
noline(b)
text(1661, 283, "M10", 19, BLACK, boxw=120, boxh=50)
text(1519, 30, "Cross-section 1", 19, BLACK, boxw=380, boxh=44)

# --- Cross-section 2 (bottom-right) ---
p = rrect(1319, 356, 1720, 608)
setfill(p, GREEN_BG)
setline(p, BLACK, 1.4)
draw_red("p2", 1.0)
c = roval(1522, 477, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
fr = rrect(1319, 356, 1720, 608)
nofill(fr)
setline(fr, BLACK, 1.4)
b = rrect(1608, 554, 1714, 598)
setfill(b, M10)
noline(b)
text(1661, 576, "M10", 19, BLACK, boxw=120, boxh=50)
text(1519, 640, "Cross-section 2", 19, BLACK, boxw=380, boxh=44)

# ============================ 3D BOX ============================
L, R, T, B = 442, 1130, 178, 612
DX, DY = 118, 118

# top face
poly([(L, T), (R, T), (R + DX, T - DY), (L + DX, T - DY)], fill=(243, 243, 243), wt=1.5)
# right face
poly([(R, T), (R + DX, T - DY), (R + DX, B - DY), (R, B)], fill=(233, 233, 233), wt=1.5)
# front face
f = rrect(L, T, R, B)
setfill(f, GRAY)
setline(f, BLACK, 1.5)
# color bands
gb = rrect(561, T, 796, B)
setfill(gb, (218, 223, 209))
noline(gb)
bb = rrect(796, T, 1035, B)
setfill(bb, (218, 223, 209))
noline(bb)

# borehole / bolt ellipses (drawn first; the crack runs over them, as in the original)
# (cx, rx, fill, outline, weight, dashed)  -- slender ovals, centre y=423
ELL = [(505, 18, (255, 255, 255), BLACK, 1.4, True),
       (627, 15, (235, 235, 235), (60, 60, 60), 1.0, True),
       (742, 15, (235, 235, 235), (60, 60, 60), 1.0, True),
       (858, 15, (235, 235, 235), (60, 60, 60), 1.0, True),
       (974, 15, (235, 235, 235), (60, 60, 60), 1.0, True),
       (1191, 15, (255, 255, 255), BLACK, 1.4, False)]
for cx, rx, fc, oc, wt, dash in ELL:
    e = roval(cx, 423, rx, 52)
    setfill(e, fc)
    setline(e, oc, wt, dash=dash)

# red crack (extracted from the original figure)
draw_red("box", 1.0)

# --- black grid lines are drawn ON TOP of the red crack, so red never crosses them ---
DIVS = [561, 678, 796, 914, 1035]
# vertical dashed divisions
for xd in DIVS:
    ln = rline(xd, T, xd, B)
    setline(ln, BLACK, 0.9, dash=True)
# top-face dashed depth lines
for xd in DIVS:
    ln = rline(xd, T, xd + DX, T - DY)
    setline(ln, BLACK, 0.9, dash=True)
# bottom "hidden" dashed depth lines (stop at the coloured band edge, as in original)
for xd in [442, 561, 678, 796, 914]:
    ln = rline(xd, B, xd + DX, B - DY)
    setline(ln, BLACK, 0.9, dash=True)
# horizontal reference dashed lines (four, full width, as in the original); the two
# that run through the ovals are broken around them so the ovals still hide the lines
HOLES = [(505, 20), (627, 17), (742, 17), (858, 17), (974, 17), (1191, 17)]


def hline(y, wt):
    xs = L
    for cx, rx in HOLES:
        a, b = cx - rx, cx + rx
        if a > xs:
            ln = rline(xs, y, a, y)
            setline(ln, BLACK, wt, dash=True)
        xs = max(xs, b)
    if xs < R + DX:
        ln = rline(xs, y, R + DX, y)
        setline(ln, BLACK, wt, dash=True)


for yy in (368, 420, 471):
    hline(yy, 0.9)
hline(493, 1.5)

# ============================ DIMENSIONS ============================
DIMY = 645
ln = rline(L, DIMY, R, DIMY)
setline(ln, BLACK, 1.0)
ticks = [442, 561, 678, 796, 914, 1130]
for xd in ticks:
    a = rline(xd - 15, DIMY, xd, DIMY)
    setline(a, BLACK, 1.0)
    a.Cells("EndArrow").Formula = "13"
    b2 = rline(xd + 15, DIMY, xd, DIMY)
    setline(b2, BLACK, 1.0)
    b2.Cells("EndArrow").Formula = "13"
for cx, lab in [(501, "500"), (619, "500"), (737, "500"), (855, "500"), (1022, "1000")]:
    text(cx, DIMY + 22, lab, 15, BLACK, boxw=110, boxh=36)

# 1800 vertical dimension
ln = rline(1262, 60, 1262, 494)
setline(ln, BLACK, 1.2)
ln.Cells("BeginArrow").Formula = "13"
ln.Cells("EndArrow").Formula = "13"
text(1300, 277, "1800", 15, BLACK, boxw=90, boxh=36, angle=90)

# 1600 diagonal dimension
ln = rline(1152, 634, 1272, 514)
setline(ln, BLACK, 1.2)
ln.Cells("BeginArrow").Formula = "13"
ln.Cells("EndArrow").Formula = "13"
text(1252, 578, "1600", 15, BLACK, boxw=90, boxh=36, angle=45)

text(1048, 578, "Unit: mm", 16, BLACK, boxw=200, boxh=40)

# ============================ PURPLE ARROWS ============================
arrow(724, 393, 420, 215)
arrow(579, 455, 410, 512)
arrow(1014, 405, 1300, 205)
arrow(880, 468, 1300, 460)

doc.Pages.Item(1).Export(r"D:\Zcode\.zcode\workspace\default\vimg\render.png")
doc.SaveAs(r"D:\Zcode\.zcode\workspace\default\tunnel_model.vsdx")
print("shapes:", pg.Shapes.Count, "-> saved tunnel_model.vsdx")
