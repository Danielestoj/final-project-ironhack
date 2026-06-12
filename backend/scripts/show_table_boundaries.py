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

with open("data/clases_razas.json", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    nombre = item["nombre"]
    if nombre == "Bárbaro":
        continue
    lines = item["descripcion"].split("\n")
    first_feat = FIRST_FEATURES.get(nombre)
    el_line = next(
        (i for i, l in enumerate(lines) if l.strip() == f"El {nombre.lower()}"), None
    )
    feat_line = (
        next(
            (i for i, l in enumerate(lines) if l.strip() == first_feat), None
        )
        if first_feat
        else None
    )
    if el_line is not None and feat_line is not None:
        print(f"{nombre}: el={el_line} feat={feat_line} lines={feat_line - el_line}")
    else:
        print(f"{nombre}: el={el_line} feat={feat_line}")
