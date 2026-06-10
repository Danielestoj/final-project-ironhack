"""Parse SRD 5.1 races from extracted PDF text (pages 2-7) into structured JSON."""
import re, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

with open(str(BASE / "temp_pdf_races.txt"), "r", encoding="utf-8") as f:
    text = f.read()

# Remove page markers and legal blocks
text = re.sub(r'\n=== PAGE \d+ ===\n', '\n', text)
text = re.sub(
    r'Documento de referencia del sistema.*?(?:uso personal\.)',
    '',
    text,
    flags=re.DOTALL,
)

# Remove the intro section (before first race)
# First race is "Elfo" - find it
first_race = text.find('\nElfo\n')
intro_text = text[:first_race] if first_race > 0 else ""
text = text[first_race:] if first_race > 0 else text

# Normalize whitespace
lines = []
for line in text.split('\n'):
    line = line.strip()
    if not line:
        lines.append('')
        continue
    if re.match(r'^\d+$', line):
        continue
    lines.append(line)

# Remove consecutive empty lines
cleaned = []
prev = False
for line in lines:
    if line == '':
        if not prev:
            cleaned.append(line)
        prev = True
    else:
        cleaned.append(line)
        prev = False

# Find race and subrace names: a line followed by "Atributos de los ..."
race_starts = []  # (name, index, is_subrace)
for i in range(len(cleaned) - 1):
    cur = cleaned[i]
    nxt = cleaned[i + 1]
    if nxt.startswith('Atributos de los') and cur and not cur.startswith('==='):
        if i > 0 and cleaned[i-1] and not cleaned[i-1].startswith('Razas'):
            race_starts.append((cur, i, False))

# Also find subraces: lines that are NOT race names but appear between race sections
# (e.g., "Alto elfo" nested under Elfo)
# We'll detect these by looking for lines that start a new section within a race
for i in range(len(cleaned) - 1):
    cur = cleaned[i]
    nxt = cleaned[i + 1]
    if cur and not nxt.startswith('Atributos de los') and not nxt:
        # Check if cur looks like a subrace name (uppercase start, short, no colon)
        pass  # Handled differently below

sys.stderr.write(f'Found {len(race_starts)} races\n')
for name, idx, _ in race_starts:
    sys.stderr.write(f'  {name} (line {idx})\n')

# Parse each race section
def extract_race_section(name, start_idx):
    end_idx = len(cleaned)
    for nr, ni, _ in race_starts:
        if ni > start_idx and nr != name:
            end_idx = ni
            break
    
    section = cleaned[start_idx:end_idx]
    
    # Extract attributes: parse bullet-pointed fields
    # Format: "Attribute. Description text..."
    attributes = []
    for line in section:
        if line == name or line.startswith('Atributos de los') or line == '':
            continue
        if line.startswith('Alto elfo') or line.startswith('Elfo de los bosques') or line.startswith('Elfo oscuro (drow)'):
            continue  # Skip subrace headers (handled separately)
        
        # Check if line starts an attribute (bold header ending with period)
        m = re.match(r'^([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ ]+)\.\s*(.*)', line)
        if m:
            attr_name = m.group(1).strip()
            attr_desc = m.group(2).strip()
            # Collect continuation lines
            idx = cleaned.index(line) if line in cleaned else -1
            if idx >= 0:
                j = idx + 1
                while j < len(cleaned):
                    nxt = cleaned[j]
                    if not nxt or re.match(r'^[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ ]+\.', nxt) or nxt.startswith('Alto elfo'):
                        break
                    if nxt != '':
                        attr_desc += ' ' + nxt
                    j += 1
            attributes.append({'nombre': attr_name, 'descripcion': attr_desc})
    
    # Build full description
    desc_lines = []
    for line in section:
        if line and line != name and not line.startswith('Atributos de los') and not line.startswith('Alto elfo'):
            desc_lines.append(line)
    descripcion = '\n'.join(desc_lines)
    
    entry = {
        'nombre': name,
        'tipo': 'raza',
        'descripcion': descripcion if len(descripcion) > 50 else '',
        'atributos': attributes,
    }
    
    return entry

# Parse all races
races = []
for name, idx, _ in race_starts:
    entry = extract_race_section(name, idx)
    races.append(entry)
    sys.stderr.write(f'  + {name} ({len(entry["atributos"])} atributos)\n')

sys.stderr.write(f'Total races: {len(races)}\n')

# Save
output = BASE / 'data' / 'razas.json'
output.write_text(json.dumps(races, indent=2, ensure_ascii=False), encoding='utf-8')
sys.stderr.write(f'Saved to {output}\n')

# Also show race names
for r in races:
    sys.stderr.write(f'  - {r["nombre"]}\n')
