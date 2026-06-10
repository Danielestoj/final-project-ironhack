import json

with open('data/enemigos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total entries: {len(data)}')

# Show all creature names
for e in data:
    ca = e.get('clase_de_armadura', '?')
    pg = e.get('puntos_de_golpe', '?')
    des = e.get('desafio', '?')
    print(f'  {e["nombre"]:35s} CA: {ca:30s} PG: {pg:20s} Des: {des}')
