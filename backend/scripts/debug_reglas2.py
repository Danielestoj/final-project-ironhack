from pathlib import Path
import sys
sys.path.insert(0, ".")
from scripts.sync_to_db import parsear_reglas

texto = Path("docs/reglas_basicas.txt").read_text(encoding="utf-8")
parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
total_antes = sum(1 for p in parrafos if len(p) > 50)
despues = parsear_reglas(texto, "reglas_basicas")
print(f"Paragraphs with len>50: {total_antes}")
print(f"After parsear_reglas: {len(despues)}")
if despues:
    print(f"First: {despues[0]['contenido'][:80]}")
if len(despues) > 1:
    print(f"Second: {despues[1]['contenido'][:80]}")
