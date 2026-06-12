import json
data = json.load(open("data/clases_razas.json", encoding="utf-8"))
for item in data:
    if item.get("tipo") == "clase":
        desc = item["descripcion"]
        lines = desc.split("\n")
        print(f"=== {item['nombre']} ===")
        for i, line in enumerate(lines):
            if "Nivel" in line:
                start = max(0, i - 2)
                end = min(len(lines), i + 25)
                for j in range(start, end):
                    marker = ">" if j == i else " "
                    print(f"{marker} {lines[j][:150]}")
                print()
                break
        print()
