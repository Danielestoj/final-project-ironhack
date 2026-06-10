import re

with open('temp_pdf_enemies.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the word Ángeles (with or without accent)
for term in ['Ángeles', 'Angeles']:
    idx = text.find(term)
    if idx >= 0:
        print(f'=== FOUND "{term}" at position {idx} ===')
        start = max(0, idx - 300)
        end = min(len(text), idx + 800)
        print(text[start:end])
        print('=== END ===')
        break
else:
    print('Not found')

# Also list all creature names by finding patterns like:\n\nNombre\n
# Look for the pattern: typically a creature entry starts with its name on a line
# preceded by stat numbers or blank lines
lines = text.split('\n')
creature_names = []
for i, line in enumerate(lines):
    line_stripped = line.strip()
    if line_stripped and len(line_stripped) < 50 and not line_stripped.startswith('===') and not line_stripped.startswith(('Página', 'CAPÍTULO', 'www')):
        # Check if previous lines look like blank/separator
        if i > 0 and (lines[i-1].strip() == '' or lines[i-1].strip().startswith('===')):
            # Check if this could be a creature name (starts with uppercase)
            if line_stripped[0].isupper() and not any(c.isdigit() for c in line_stripped):
                creature_names.append(line_stripped)

print('\n\n=== POTENTIAL CREATURE NAMES ===')
for name in creature_names:
    print(name)
