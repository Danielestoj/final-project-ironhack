import sys
sys.path.insert(0, ".")
from scripts.sync_to_db import parsear_clases_razas, leer_txt
import re

texto = leer_txt("clases_y_razas.txt")
lines = texto.split("\n")

print(f"Total lines: {len(lines)}")
print(f"\nFirst 30 non-empty, non-# lines:")
count = 0
for ln in lines:
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    if count < 30:
        print(f"  {repr(ln[:80])}")
    count += 1

print(f"\n--- Checking section headers ---")
count = 0
for ln in lines:
    l = ln.strip()
    if not l:
        continue
    if l.upper() == l and l.endswith(":"):
        print(f"  UPPER header: {repr(l)}")
        count += 1
        if count > 10:
            print("  ...")
            break
