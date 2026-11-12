# -*- coding: utf-8 -*-
"""Extract red crack polylines from the source figure and dump them as JSON."""
import json
import os
import numpy as np
from PIL import Image, ImageDraw

SRC = os.path.expandvars(r"%USERPROFILE%\.zcode\cli\image-cache\sess_9bc10f54-6a4b-4ab2-b20e-0772c627edee\image-4994f8eea1e453ae51416d6f1e4043ba.png")
WORKSPACE = r"D:\Zcode\.zcode\workspace\default"


OUT_NAME = "redpaths.json"
PREVIEW_NAME = os.path.join("vimg", "redpaths.png")


def workspace_path(name):
    """Resolve `name` relative to WORKSPACE and refuse anything outside it.

    The name must be relative; absolute names and `..` segments that walk out of
    WORKSPACE are rejected. Returns the real (symlink-resolved) absolute path.
    """
    if os.path.isabs(name):
        raise ValueError("expected a relative name, got: %s" % name)
    base = os.path.realpath(WORKSPACE)
    p = os.path.realpath(os.path.join(base, name))
    if os.path.commonpath([base, p]) != base:
        raise ValueError("path escapes workspace: %s" % p)
    return p


OUT = workspace_path(OUT_NAME)
PREVIEW = workspace_path(PREVIEW_NAME)

im = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
R, G, B = im[:, :, 0], im[:, :, 1], im[:, :, 2]
RED = (R > 120) & (G < 110) & (B < 110) & (R - G > 50) & (R - B > 50)

REGIONS = {
    "box": (540, 990, 335, 475, 26, 14),
    "p3": (2, 402, 95, 285, 20, 12),
    "p4": (2, 402, 415, 575, 20, 12),
    "p1": (1320, 1720, 85, 225, 20, 12),
    "p2": (1320, 1720, 375, 505, 20, 12),
}


def clusters(col, y0):
    out = []
    for v in col:
        if out and v - out[-1][-1] <= 2:
            out[-1].append(v)
        else:
            out.append([v])
    return [(float(np.mean(g)) + y0) for g in out]


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    dmax, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / n
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        left = rdp(pts[:idx + 1], eps)
        right = rdp(pts[idx:], eps)
        return left[:-1] + right
    return [pts[0], pts[-1]]


def trace(x0, x1, y0, y1, maxgap, ytol):
    strands = []          # each: dict(pts=[(x,y)], last=(x,y), gap=0, alive=True)
    for x in range(x0, x1 + 1):
        col = np.where(RED[y0:y1, x])[0]
        cs = clusters(col, y0) if len(col) else []
        used = [False] * len(cs)
        for st in strands:
            if not st["alive"]:
                continue
            best, bd = -1, ytol
            for i, cy in enumerate(cs):
                if used[i]:
                    continue
                d = abs(cy - st["last"][1])
                if d < bd:
                    best, bd = i, d
            if best >= 0:
                used[best] = True
                st["pts"].append((x, cs[best]))
                st["last"] = (x, cs[best])
                st["gap"] = 0
            else:
                st["gap"] += 1
                if st["gap"] > maxgap:
                    st["alive"] = False
        for i, cy in enumerate(cs):
            if not used[i]:
                strands.append({"pts": [(x, cy)], "last": (x, cy), "gap": 0, "alive": True})
    paths = []
    for st in strands:
        if len(st["pts"]) >= 4:
            sm = rdp(st["pts"], 0.5)
            paths.append([[round(a, 1), round(b, 1)] for a, b in sm])
    return paths


result = {}
for name, (x0, x1, y0, y1, mg, yt) in REGIONS.items():
    paths = trace(x0, x1, y0, y1, mg, yt)
    result[name] = paths
    print(name, "paths:", len(paths), "pts:", [len(p) for p in paths])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f)
print("written", OUT)

# preview
prev = Image.new("RGB", (im.shape[1], im.shape[0]), (255, 255, 255))
d = ImageDraw.Draw(prev)
for name, paths in result.items():
    for p in paths:
        d.line([tuple(q) for q in p], fill=(200, 0, 0), width=2)
prev.save(PREVIEW)
print("preview", PREVIEW)
