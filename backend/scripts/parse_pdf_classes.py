"""Parse SRD 5.1 classes from extracted PDF text (pages 8-55) into structured JSON."""
import re, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

with open(str(BASE / "temp_pdf_classes.txt"), "r", encoding="utf-8") as f:
    text = f.read()

# Remove page markers and legal blocks
text = re.sub(r'\n=== PAGE \d+ ===\n', '\n', text)
text = re.sub(
    r'Documento de referencia del sistema.*?(?:uso personal\.)',
    '',
    text,
    flags=re.DOTALL,
)

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

# Find class boundaries: class name line followed by "Rasgos de clase"
CLASS_NAMES = []  # list of (name, start_index)
for i in range(len(cleaned) - 1):
    cur = cleaned[i]
    nxt = cleaned[i + 1]
    if nxt == 'Rasgos de clase' and cur and not cur.startswith('===') and not cur.startswith('Documento'):
        if cur not in ('Puntos de golpe', 'Competencias', 'Equipo', 'Rasgos de clase'):
            CLASS_NAMES.append((cur, i))

# Also detect class by "El [class]" table headers
TABLE_CLASSES = []
for i, line in enumerate(cleaned):
    if line.startswith('El ') and len(line) < 25 and line not in ('El Cazador y la Presa',):
        TABLE_CLASSES.append((line[3:].strip(), i))  # Extract class name after "El "

sys.stderr.write(f'Found {len(CLASS_NAMES)} classes by heading\n')
for name, idx in CLASS_NAMES:
    sys.stderr.write(f'  {name} (line {idx})\n')

# Parse each class section
def extract_class_section(name, start_idx):
    """Extract all text from start_idx to the next class or end."""
    # Find end: next class heading or end of file
    end_idx = len(cleaned)
    for cn, ci in CLASS_NAMES:
        if ci > start_idx and cn != name:
            end_idx = ci
            break
    
    section = cleaned[start_idx:end_idx]
    
    # Extract hit dice
    dado_golpe = ""
    for line in section:
        m = re.search(r'Dados de Golpe:\s*(1d\d+)', line)
        if m:
            dado_golpe = m.group(1)
            break
    
    # Extract primary ability from "Tiradas de salvación" line
    habilidad_principal = ""
    for line in section:
        if line.startswith('Tiradas de salvación:'):
            habilidad_principal = line.split(':', 1)[1].strip()
            break
    
    # Extract armor/weapon proficiencies
    armadura = ""
    armas = ""
    for i, line in enumerate(section):
        if line.startswith('Armadura:'):
            armadura = line.split(':', 1)[1].strip()
        elif line.startswith('Armas:'):
            armas = line.split(':', 1)[1].strip()
    
    # Extract starting equipment
    equipo = []
    in_equipo = False
    for i, line in enumerate(section):
        if line == 'Equipo':
            in_equipo = True
            continue
        if in_equipo:
            if line in ('', 'Rasgos de clase') or line.startswith(('Puntos', 'Competencias', 'Armadura:', 'Armas:', 'Herramientas:', 'Tiradas')):
                continue
            if line.startswith('•') or line.startswith('-'):
                equipo.append(line)
            elif line.startswith('El ') and len(line) < 25:
                # Table header - end of equipment
                break
            elif line.startswith('Nivel') or line.startswith('Bon.'):
                break
            elif equipo and not line.startswith('•'):
                # Continuation of last equipment item
                equipo[-1] += ' ' + line
    
    # Extract features (including level table and descriptions)
    # Find where features start: after the equipment section and level table
    features_start = 0
    for i, line in enumerate(section):
        if line.startswith('El ') or line == name or line == 'Rasgos de clase':
            features_start = i
        if line.startswith('Nivel') and 'Bon.' in line:
            features_start = i
    
    # Collect all text before "Rasgos de clase" header info
    descripcion_parts = []
    in_header = False
    for line in section:
        if line == 'Rasgos de clase':
            in_header = True
            continue
        if in_header:
            if line.startswith(('Puntos de golpe', 'Dados de Golpe:', 'Competencias', 'Armadura:', 'Armas:', 'Herramientas:', 'Tiradas', 'Habilidades:', 'Equipo', '•', '-')):
                continue
            if line.startswith('El ') and len(line) < 25:
                # End of header info
                in_header = False
                continue
            if in_header and line and len(line) > 10 and not line.startswith('Nivel') and not line.startswith('Bon.'):
                descripcion_parts.append(line)
    
    # Build full description from the section
    descripcion = '\n'.join(line for line in section 
                           if line and line != name and line != 'Rasgos de clase' 
                           and not line.startswith('===') 
                           and not line.startswith('Documento')
                           and line not in ('Puntos de golpe', 'Competencias', 'Equipo'))
    
    entry = {
        'nombre': name,
        'tipo': 'clase',
        'dado_golpe': dado_golpe,
        'habilidad_principal': habilidad_principal,
        'descripcion': descripcion,
    }
    
    if armadura:
        entry['armadura'] = armadura
    if armas:
        entry['armas'] = armas
    if equipo:
        entry['equipo'] = equipo
    
    return entry

# Parse all classes
classes = []
for name, idx in CLASS_NAMES:
    entry = extract_class_section(name, idx)
    classes.append(entry)
    sys.stderr.write(f'  + {name} (DG: {entry.get("dado_golpe","?")})\n')

sys.stderr.write(f'Total classes: {len(classes)}\n')

# Save
output = BASE / 'data' / 'clases_razas.json'
output.write_text(json.dumps(classes, indent=2, ensure_ascii=False), encoding='utf-8')
sys.stderr.write(f'Saved to {output}\n')
