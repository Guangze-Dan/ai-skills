import docx

doc = docx.Document('Z:/StudentKb.docx')
print('=== PARAGRAPHS ===')
for p in doc.paragraphs:
    if p.text.strip():
        print(f'[{p.style.name}] {p.text}')

print()
print('=== TABLES ===')
for i, t in enumerate(doc.tables):
    print(f'--- Table {i+1} ({len(t.rows)} rows x {len(t.columns)} cols) ---')
    for j, r in enumerate(t.rows):
        cells = [c.text.strip() for c in r.cells]
        print(f'  Row {j}: {cells}')