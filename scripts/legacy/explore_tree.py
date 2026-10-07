import os, sys

p = r'D:\Zcode'
lines = []
for root, dirs, files in os.walk(p):
    depth = root[len(p):].count(os.sep)
    lines.append('  ' * depth + os.path.basename(root) + '/')
    for f in files:
        lines.append('  ' * (depth + 1) + f)

with open(r'D:\Zcode\_tree.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))

from pypdf import PdfReader
r = PdfReader(r'D:\wechat\chat\xwechat_files\wxid_2h5nsnaq7tgc21_041e\msg\file\2026-08\MultiDIC_v_1_1_0_instruction_manual.pdf')
out = ['pages: %d' % len(r.pages)]
for i, pg in enumerate(r.pages):
    out.append('=== PAGE %d ===' % (i + 1))
    out.append(pg.extract_text() or '')

with open(r'D:\Zcode\multidic_manual.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out))

print('tree lines:', len(lines))
print('pdf pages:', len(r.pages))
