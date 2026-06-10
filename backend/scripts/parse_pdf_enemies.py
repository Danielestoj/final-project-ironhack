"""Parse SRD 5.1 bestiary from extracted PDF text into structured JSON."""
import re, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

with open(str(BASE / "temp_pdf_enemies.txt"), "r", encoding="utf-8") as f:
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

# Size keywords (masculine and feminine forms)
SIZES = ['Diminuto', 'Diminuta', 'Pequeño', 'Pequeña', 'Mediano', 'Mediana', 'Grande', 'Enorme', 'Gargantuesco']

def is_type_line(line):
    """Check if line matches pattern: TYPE SIZE, alignment"""
    if ',' not in line:
        return False
    before, after = line.split(',', 1)
    before = before.strip()
    # Before comma should end with a size word
    parts = before.split()
    if parts and parts[-1] in SIZES:
        return True
    return False

def is_section_header(line):
    """Check if line is a section header like 'Monstruos (A)', 'Ángeles', etc."""
    if line.startswith('Monstruos') or line.startswith('Ángeles'):
        return True
    if line in ('Demonios', 'Diablos', 'Dinosaurios', 'Elementales',
                 'Esqueletos', 'Gigantes', 'Gólems', 'Gules', 'Hongos',
                 'Licántropos', 'Mephits', 'Nagas', 'Sagas', 'Vampiros',
                 'Zombis', 'Cienos', 'Dragones', 'Dragón',
                 'Deidades celtas', 'Deidades egipcias', 'Deidades griegas',
                 'Deidades nórdicas', 'Objetos animados'):
        return True
    if re.match(r'^Dragones? (cromáticos|metálicos)$', line):
        return True
    if re.match(r'^(Cría de )?Dragón (de )?\w+ (anciano|adulto|joven)$', line):
        return True
    return False

def is_name_line(line, next_line):
    """Check if line looks like a creature name."""
    if not line or not next_line:
        return False
    if ':' in line or ',' in line:
        return False
    if len(line) < 2 or len(line) > 40:
        return False
    if not line[0].isupper():
        return False
    if re.match(r'^\d', line):
        return False
    if is_section_header(line):
        return False
    if is_type_line(line):
        return False
    if not is_type_line(next_line):
        return False
    return True

# Parse monster stat fields
STAT_PREFIXES = {
    'Clase de Armadura:': 'clase_de_armadura',
    'Puntos de golpe:': 'puntos_de_golpe',
    'Velocidad:': 'velocidad',
    'Tiradas de salvación:': 'tiradas_de_salvación',
    'Habilidades:': 'habilidades',
    'Resistencia a daño:': 'resistencia_a_daño',
    'Resistencia a daños:': 'resistencia_a_daño',
    'Inmunidad a daño:': 'inmunidad_a_daño',
    'Inmunidad a daños:': 'inmunidad_a_daño',
    'Inmunidad a estados:': 'inmunidad_a_estados',
    'Inmunidad a condición:': 'inmunidad_a_estados',
    'Sentidos:': 'sentidos',
    'Idiomas:': 'idiomas',
    'Desafío:': 'desafio',
    'Vulnerabilidad a daño:': 'vulnerabilidad_a_daño',
    'Vulnerabilidad a daños:': 'vulnerabilidad_a_daño',
}

def has_stat_prefix(line):
    for p in STAT_PREFIXES:
        if line.startswith(p):
            return p
    return None

# Stats header
STATS_HEADER = re.compile(r'^FUE\s+DES\s+CON\s+INT\s+SAB\s+CAR')
STATS_VALUES = re.compile(r'^\d+\s*\([^)]+\)')

# Build monster entries
monsters = []
i = 0
while i < len(cleaned):
    line = cleaned[i]
    if not line:
        i += 1
        continue
    
    if is_section_header(line):
        i += 1
        continue
    
    # Check if current line + next line forms a creature name + type
    if i + 1 < len(cleaned):
        next_line = cleaned[i + 1]
        if is_name_line(line, next_line):
            name = line
            tipo = next_line
            i += 2
            
            stat_block = {}
            abilities_text = []
            acciones_text = []
            in_acciones = False
            skip_rest = False
            
            while i < len(cleaned):
                cur = cleaned[i]
                
                if not cur:
                    i += 1
                    if not in_acciones:
                        continue
                    else:
                        continue
                
                # Skip stats header/values lines
                if STATS_HEADER.match(cur) or STATS_VALUES.match(cur):
                    i += 1
                    continue
                
                # Check if we've hit the next creature
                if i + 1 < len(cleaned):
                    nxt = cleaned[i + 1]
                    if is_name_line(cur, nxt) and not has_stat_prefix(cur):
                        break
                
                # Check for section headers
                if is_section_header(cur):
                    i += 1
                    break
                
                # Check if this is a stat line
                prefix = has_stat_prefix(cur)
                if prefix:
                    in_acciones = False
                    key = STAT_PREFIXES[prefix]
                    val = cur.split(':', 1)[1].strip()
                    # Collect continuation lines (lowercase continuations only)
                    while i + 1 < len(cleaned):
                        nxt_line = cleaned[i + 1]
                        if (not nxt_line or has_stat_prefix(nxt_line)
                                or STATS_HEADER.match(nxt_line)
                                or STATS_VALUES.match(nxt_line)
                                or (i + 2 < len(cleaned) and is_name_line(nxt_line, cleaned[i + 2]))
                                or is_section_header(nxt_line)
                                or (nxt_line[0].isupper() and ':' not in nxt_line)):
                            break
                        val += ' ' + nxt_line
                        i += 1
                    stat_block[key] = val.strip()
                elif cur == 'Acciones' or cur.startswith('Acciones '):
                    in_acciones = True
                    # "Acciones" itself might be the start of the actions description
                    # or "Acciones legendarias" etc.
                    acc_text = cur
                    while i + 1 < len(cleaned):
                        nxt_line = cleaned[i + 1]
                        if (not nxt_line or nxt_line.startswith('Variante:')
                                or has_stat_prefix(nxt_line)
                                or (i + 2 < len(cleaned) and is_name_line(nxt_line, cleaned[i + 2]))
                                or is_section_header(nxt_line)
                                or cur.startswith('Acciones legendarias')):
                            break
                        if not STATS_HEADER.match(nxt_line) and not STATS_VALUES.match(nxt_line):
                            acc_text += ' ' + nxt_line
                        i += 1
                    acciones_text.append(acc_text)
                elif cur.startswith('Variante:'):
                    in_acciones = False
                    # Skip variant lines
                    while i + 1 < len(cleaned):
                        nxt_line = cleaned[i + 1]
                        if (not nxt_line or has_stat_prefix(nxt_line)
                                or (i + 3 < len(cleaned) and is_name_line(nxt_line, cleaned[i + 2]))
                                or is_section_header(nxt_line)):
                            break
                        i += 1
                elif cur:
                    # Ability or description text (before Actions)
                    if not in_acciones:
                        abilities_text.append(cur)
                    else:
                        if not cur.startswith('Acciones'):
                            acciones_text.append(cur)
                
                i += 1
            
            # Build entry
            entry = {'nombre': name, 'tipo': tipo}
            for k in ['clase_de_armadura', 'puntos_de_golpe', 'velocidad',
                       'tiradas_de_salvación', 'habilidades', 'resistencia_a_daño',
                       'inmunidad_a_daño', 'inmunidad_a_estados', 'sentidos',
                       'idiomas', 'desafio', 'vulnerabilidad_a_daño']:
                if k in stat_block:
                    entry[k] = stat_block[k]
            
            if abilities_text:
                entry['habilidades_especiales'] = '\n'.join(abilities_text)
            if acciones_text:
                entry['acciones'] = '\n'.join(acciones_text)
            
            if 'clase_de_armadura' in entry:
                monsters.append(entry)
                sys.stderr.write(f'  + {name}\n')
            else:
                sys.stderr.write(f'  ? {name} (no CA)\n')
            
            continue
    
    i += 1

sys.stderr.write(f'Total monsters: {len(monsters)}\n')

# Save
output = BASE / 'data' / 'enemigos.json'
output.write_text(json.dumps(monsters, indent=2, ensure_ascii=False), encoding='utf-8')
sys.stderr.write(f'Saved to {output}\n')

# Also print some stats
sys.stderr.write(f'\nSample entries:\n')
for m in monsters[:5]:
    sys.stderr.write(f'  {m["nombre"]} - {m.get("desafio", "?")}\n')
