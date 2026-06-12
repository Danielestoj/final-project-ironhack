"""Remove embedded progression table text from descripcion in clases_razas.json
for all classes except Bárbaro (already cleaned)."""

import json

FIRST_FEATURES = {
    "Bardo": "Lanzamiento de Conjuros",
    "Brujo": "Patrón Sobrenatural",
    "Clérigo": "Lanzamiento de Conjuros",
    "Druida": "Druídico",
    "Explorador": "Enemigo Predilecto",
    "Guerrero": "Estilo de Combate",
    "Hechicero": "Lanzamiento de Conjuros",
    "Mago": "Lanzamiento de Conjuros",
    "Monje": "Defensa sin Armadura",
    "Paladín": "Sentidos Divinos",
    "Pícaro": "Pericia",
}

path = "data/clases_razas.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

removed = 0
for item in data:
    nombre = item["nombre"]
    if nombre == "Bárbaro":
        continue
    lines = item["descripcion"].split("\n")
    el_line = next(
        (i for i, l in enumerate(lines) if l.strip() == f"El {nombre.lower()}"), None
    )
    first_feat = FIRST_FEATURES.get(nombre)
    feat_line = (
        next(
            (i for i, l in enumerate(lines) if l.strip() == first_feat), None
        )
        if first_feat
        else None
    )
    if el_line is not None and feat_line is not None:
        kept = lines[:el_line] + lines[feat_line:]
        item["descripcion"] = "\n".join(kept)
        print(f"  {nombre}: removed {feat_line - el_line} lines")
        removed += 1
    else:
        print(f"  {nombre}: SKIPPED (el={el_line}, feat={feat_line})")

with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nDone. {removed} classes cleaned.")
