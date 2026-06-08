import json
data = json.load(open("data/hechizos.json", encoding="utf-8"))
count = 0
for e in data:
    comp = e.get("componentes", "")
    last_open = comp.rfind("(")
    last_close = comp.rfind(")")
    if last_open > last_close and last_open >= 0:
        count += 1
        if count <= 5:
            desc = e.get("descripcion", "")
            print(f"  {e['nombre']}: comp ends ...{comp[-30:]}")
            print(f"    desc starts: {desc[:80]}")
print(f"Total: {count} of {len(data)}")
