# -*- coding: utf-8 -*-
"""Reproduce the tunnel 3D-model schematic figure in Visio (COM automation)."""
import win32com.client as w

PX = 100.0          # image pixels per inch
IMG_H = 683.0       # source image height in px


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


# ============================ PANELS ============================
GREEN_BG = (235, 241, 223)
BLUE_BG = (219, 238, 243)
M10 = (157, 187, 97)
M75 = (75, 172, 198)

# --- Cross-section 3 (top-left) ---
p = rrect(2, 58, 402, 312)
setfill(p, GREEN_BG)
setline(p, BLACK, 1.4)
polyline([(3, 150), (28, 157), (50, 156), (72, 168), (92, 180), (112, 188)], RED, 1.5)
polyline([(75, 225), (95, 238), (115, 250), (140, 252), (165, 244), (192, 228)], RED, 1.5)
polyline([(252, 206), (262, 196), (268, 178), (264, 160), (252, 150)], RED, 1.5)
polyline([(252, 206), (280, 205), (310, 200), (345, 196), (375, 199), (400, 208)], RED, 1.5)
c = roval(206, 180, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
b = rrect(291, 258, 397, 302)
setfill(b, M10)
noline(b)
text(344, 280, "M10", 19, BLACK, boxw=120, boxh=50)
text(202, 30, "Cross-section 3", 19, BLACK, boxw=380, boxh=44)

# --- Cross-section 4 (bottom-left) ---
p = rrect(2, 355, 402, 608)
setfill(p, GREEN_BG)
setline(p, BLACK, 1.4)
polyline([(75, 455), (100, 468), (125, 482), (150, 496), (160, 500)], RED, 1.5)
polyline([(252, 498), (285, 505), (315, 515), (345, 528), (362, 538)], RED, 1.5)
c = roval(206, 477, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
b = rrect(291, 554, 397, 598)
setfill(b, M10)
noline(b)
text(344, 576, "M10", 19, BLACK, boxw=120, boxh=50)
text(202, 640, "Cross-section 4", 19, BLACK, boxw=380, boxh=44)

# --- Cross-section 1 (top-right) ---
p = rrect(1319, 58, 1720, 318)
setfill(p, BLUE_BG)
setline(p, BLACK, 1.4)
polyline([(1322, 100), (1345, 118), (1365, 132), (1390, 140), (1420, 150), (1455, 165), (1476, 172)], RED, 1.5)
polyline([(1352, 120), (1375, 128), (1400, 140), (1430, 152), (1460, 168), (1476, 178)], RED, 1.5)
polyline([(1570, 168), (1600, 175), (1630, 180), (1660, 182), (1690, 180), (1718, 185)], RED, 1.5)
c = roval(1523, 186, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
b = rrect(1608, 261, 1714, 305)
setfill(b, M75)
noline(b)
text(1661, 283, "M7.5", 19, BLACK, boxw=120, boxh=50)
text(1519, 30, "Cross-section 1", 19, BLACK, boxw=380, boxh=44)

# --- Cross-section 2 (bottom-right) ---
p = rrect(1319, 356, 1720, 608)
setfill(p, BLUE_BG)
setline(p, BLACK, 1.4)
polyline([(1322, 392), (1350, 400), (1380, 415), (1410, 430), (1440, 445), (1470, 455)], RED, 1.5)
polyline([(1372, 428), (1400, 442), (1430, 455), (1458, 462)], RED, 1.5)
polyline([(1570, 478), (1610, 480), (1660, 476), (1718, 480)], RED, 1.5)
c = roval(1522, 477, 47, 47)
setfill(c, (255, 255, 255))
setline(c, BLACK, 1.4)
b = rrect(1608, 554, 1714, 598)
setfill(b, M75)
noline(b)
text(1661, 576, "M7.5", 19, BLACK, boxw=120, boxh=50)
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
setfill(bb, (205, 221, 224))
noline(bb)

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
# horizontal reference dashed lines
for yy in (363, 440):
    ln = rline(L, yy, R + DX, yy)
    setline(ln, BLACK, 0.9, dash=True)
ln = rline(561, 475, 1035, 475)
setline(ln, BLACK, 1.5, dash=True)

# crack (red wavy)
CRACK = [(553, 406), (566, 400), (578, 410), (590, 404), (602, 396), (614, 402),
         (626, 412), (638, 416), (650, 408), (662, 400), (674, 403), (686, 414),
         (698, 409), (710, 400), (722, 403), (734, 412), (746, 416), (758, 407),
         (770, 399), (782, 404), (794, 413), (806, 409), (818, 400), (830, 404),
         (842, 413), (854, 407), (866, 399), (878, 404), (890, 412), (902, 406),
         (914, 399), (926, 404), (938, 411), (950, 405), (962, 400), (975, 405)]
polyline(CRACK, RED, 1.3)

# borehole / bolt ellipses
ELL = [(498, "dash", 1.4), (600, "solid", 1.0), (700, "dash", 1.4),
       (803, "solid", 1.0), (897, "dash", 1.4), (1073, "solid", 1.0),
       (1197, "solid", 1.5)]
for cx, style, wt in ELL:
    e = roval(cx, 408, 21, 52)
    setfill(e, (255, 255, 255))
    if style == "dash":
        setline(e, BLACK, wt, dash=True)
    else:
        setline(e, (120, 120, 120) if wt < 1.4 else BLACK, wt)

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

text(1042, 578, "Unit: mm", 15, BLACK, boxw=200, boxh=40)

# ============================ PURPLE ARROWS ============================
arrow(724, 393, 420, 215)
arrow(579, 455, 410, 512)
arrow(1014, 405, 1300, 205)
arrow(880, 468, 1300, 460)

doc.Pages.Item(1).Export(r"D:\Zcode\.zcode\workspace\default\vimg\render.png")
doc.SaveAs(r"D:\Zcode\.zcode\workspace\default\tunnel_model.vsdx")
print("shapes:", pg.Shapes.Count, "-> saved tunnel_model.vsdx")
