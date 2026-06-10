import json

with open('data/enemigos.json', 'r', encoding='utf-8') as f:
    enemigos = json.load(f)

print(f'Total entries in enemigos.json: {len(enemigos)}')
for e in enemigos:
    print(f'  - {e["nombre"]}')
