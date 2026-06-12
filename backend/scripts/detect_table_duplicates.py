import json

with open('data/clases_razas.json', encoding='utf-8') as f:
    data = json.load(f)

for i, item in enumerate(data):
    desc = item['descripcion']
    nombre = item['nombre']
    lines = desc.split('\n')
    has_el = f'El {nombre}' in desc
    table_rows = [l for l in lines if l.strip() and l.strip()[0].isdigit() and '+' in l]
    print(f'{i}: {nombre:12s} lines={len(lines):3d} table_rows={len(table_rows):2d} has_el={has_el}')
