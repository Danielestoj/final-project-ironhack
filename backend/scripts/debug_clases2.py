import sys
import re
sys.path.insert(0, ".")
from scripts.sync_to_db import parsear_clases_razas, leer_txt, limpiar_linea, es_nombre_valido

texto = leer_txt("clases_y_razas.txt")
lines = texto.split("\n")

# Manual trace
count_valid = 0
count_skipped = 0
for linea in lines:
    l = linea.strip()
    if not l or l.startswith("#"):
        continue
    l = limpiar_linea(l)
    if not l:
        count_skipped += 1
        continue
    if ":" not in l:
        continue
    nombre, _, desc = l.partition(":")
    nombre = nombre.strip()
    desc = desc.strip()
    if not nombre or not desc:
        count_skipped += 1
        continue
    if not es_nombre_valido(nombre):
        count_skipped += 1
        continue
    if len(nombre) > 40 or len(desc) < 10:
        count_skipped += 1
        continue
    count_valid += 1
    if count_valid <= 3:
        print(f"  VALID: {repr(nombre)} -> {repr(desc[:60])}")

print(f"\nValid: {count_valid}, Skipped: {count_skipped}")
