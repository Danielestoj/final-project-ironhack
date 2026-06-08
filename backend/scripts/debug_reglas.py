import json
data = json.load(open("data/reglas_basicas.json", encoding="utf-8"))
print(f"Total entries: {len(data)}")
for e in data[:3]:
    cat = e.get("categoria", "")
    cont = e.get("contenido", "")
    nombre = e.get("nombre", "") or e.get("categoria", "") or ""
    print(f"  nombre='{nombre}' len={len(nombre)}  contenido_len={len(cont)}")
    print(f"    nombre[0]={repr(nombre[0]) if nombre else 'EMPTY'}")
