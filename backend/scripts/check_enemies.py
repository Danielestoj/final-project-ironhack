import json

with open('data/enemigos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total: {len(data)} entries')

# Check Ankheg
ankheg = [e for e in data if e['nombre'] == 'Ankheg']
if ankheg:
    a = ankheg[0]
    print('=== Ankheg ===')
    print(f'  CA: {a.get("clase_de_armadura", "")}')
    print(f'  PG: {a.get("puntos_de_golpe", "")}')
    acc = a.get("acciones", "")
    print(f'  Acciones (first 200): {acc[:200]}')
    text = json.dumps(a, ensure_ascii=False)
    if 'Ángeles' in text or 'Angeles' in text:
        print('  WARNING: Angeles found!')
    else:
        print('  OK: No Angeles')

# Check Deva, Planetar, Solar (under Ángeles)
for name in ['Deva', 'Planetar', 'Solar']:
    match = [e for e in data if e['nombre'] == name]
    if match:
        m = match[0]
        print(f'\n=== {name} ===')
        print(f'  Tipo: {m.get("tipo", "")}')
        print(f'  Desafio: {m.get("desafio", "")}')
    else:
        print(f'\nMISSING: {name}')

# Check some stats
print(f'\n=== Stats ===')
for cat in ['Aboleth', 'Acechador invisible', 'Ankheg', 'Broza movediza', 'Centauro']:
    match = [e for e in data if e['nombre'] == cat]
    if match:
        m = match[0]
        print(f'{m["nombre"]}: CA={m.get("clase_de_armadura","?")}, PG={m.get("puntos_de_golpe","?")}, Vel={m.get("velocidad","?")}')
    else:
        print(f'MISSING: {cat}')
