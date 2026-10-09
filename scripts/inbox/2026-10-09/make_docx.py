# -*- coding: utf-8 -*-
"""Render scheme_figure_说明文档.md into a Word .docx (headings, tables, lists)."""
import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

SRC = r"D:\Zcode\.zcode\workspace\default\scheme_figure_说明文档.md"
DST = r"D:\Zcode\.zcode\workspace\default\scheme_figure_说明文档.docx"

CJK = "宋体"
CJK_H = "黑体"

doc = Document()
st = doc.styles["Normal"]
st.font.name = CJK
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), CJK)
for i in range(1, 5):
    h = doc.styles["Heading %d" % i]
    h.font.name = CJK_H
    h.font.color.rgb = RGBColor(0, 0, 0)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), CJK_H)


def add_runs(par, txt):
    """Handle **bold** and `code` inline markers."""
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", txt):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = par.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = par.add_run(part[1:-1])
            r.font.name = "Consolas"
        else:
            par.add_run(part)
    return par


lines = open(SRC, encoding="utf-8").read().split("\n")
i = 0
while i < len(lines):
    ln = lines[i].rstrip()

    if ln.startswith("```"):
        i += 1
        buf = []
        while i < len(lines) and not lines[i].startswith("```"):
            buf.append(lines[i])
            i += 1
        p = doc.add_paragraph()
        r = p.add_run("\n".join(buf))
        r.font.name = "Consolas"
        r.font.size = Pt(9)
        i += 1
        continue

    m = re.match(r"^(#{1,4})\s+(.*)$", ln)
    if m:
        doc.add_heading(re.sub(r"[*`]", "", m.group(2)), level=len(m.group(1)))
        i += 1
        continue

    if ln.strip().startswith("|"):
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not re.fullmatch(r"[-: ]+", "".join(cells)):
                rows.append(cells)
            i += 1
        n = max(len(r) for r in rows)
        t = doc.add_table(rows=0, cols=n)
        t.style = "Table Grid"
        for k, row in enumerate(rows):
            cells = t.add_row().cells
            for j in range(n):
                cells[j].text = ""
                par = cells[j].paragraphs[0]
                add_runs(par, row[j] if j < len(row) else "")
                for r in par.runs:
                    r.font.size = Pt(9)
                    if k == 0:
                        r.bold = True
        doc.add_paragraph()
        continue

    if ln.strip().startswith("- "):
        p = doc.add_paragraph(style="List Bullet")
        add_runs(p, ln.strip()[2:])
        i += 1
        continue

    if ln.strip() == "---":
        i += 1
        continue

    if ln.strip() == "":
        i += 1
        continue

    p = doc.add_paragraph()
    add_runs(p, ln)
    i += 1

doc.save(DST)
print("saved", DST)
