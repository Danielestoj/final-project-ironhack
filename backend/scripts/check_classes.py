import json

with open('data/clases_razas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total: {len(data)} entries')
for e in data:
    desc = e.get('descripcion', '')
    print(f'\n=== {e["nombre"]} ===')
    print(f'  DG: {e.get("dado_golpe", "?")}')
    print(f'  HP: {e.get("habilidad_principal", "?")}')
    print(f'  Desc length: {len(desc)} chars')
    print(f'  Desc (first 200): {desc[:200]}')
    # Check for key features
    for kw in ['Furia', 'Inspiración', 'Magia', 'Conjuros', 'Ataque', 'Sigilo', 'Milagros']:
        if kw.lower() in desc.lower():
            print(f'  Has: {kw}')
