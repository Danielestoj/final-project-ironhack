"""
Cleanup Data
=============
Corrige problemas de calidad en los archivos JSON de backend/data/:

1. Hechizos: componentes rotos (parentesis sin cerrar cuyo contenido
   se filtró a descripcion)
2. Todos los JSON: elimina líneas "Documento de referencia del sistema 5.1"
   y otros textos legales duplicados
3. Todos los JSON: elimina entradas fragmentadas (nombres muy cortos,
   descripciones triviales)

Uso:
    python scripts/cleanup_data.py          # corrige y sobreescribe
    python scripts/cleanup_data.py --check  # solo muestra estadísticas
"""

import sys
import json
import re
from pathlib import Path

# Forzar UTF-8 para output en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ── Patrones a eliminar ──────────────────────────────────────────────

PATRONES_LEGALES = [
    r"Documento de referencia del sistema 5\.1.*",
    r"Prohibida la reventa\..*",
    r"Tienes permiso para imprimir.*",
    r"o fotocopiar este documento.*",
]

# ── Helpers ──────────────────────────────────────────────────────────

def limpiar_texto(texto: str) -> str:
    """Elimina líneas con texto legal de una cadena."""
    if not texto:
        return texto
    lineas = texto.split("\n")
    filtradas = []
    for ln in lineas:
        omitir = False
        for pat in PATRONES_LEGALES:
            if re.search(pat, ln.strip()):
                omitir = True
                break
        if not omitir:
            filtradas.append(ln)
    result = "\n".join(filtradas).strip()
    # Limpiar multiples saltos de línea
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def es_entrada_valida(entry: dict) -> bool:
    """Filtra entradas fragmentadas o sin sentido."""
    nombre = entry.get("nombre", "") or entry.get("categoria", "") or ""
    nombre = nombre.strip()
    desc = entry.get("descripcion", "") or entry.get("contenido", "") or ""
    desc = desc.strip()

    # Nombres demasiado cortos o que son claramente fragmentos
    if len(nombre) < 3:
        return False
    if nombre[0].islower() and nombre not in ("d100", "d20", "d12", "d10", "d8", "d6", "d4") and not nombre.startswith(("reglas_", "trasfondo_")):
        return False
    if nombre.lower() in ("título", "titulo", "por ejemplo", "ejemplo"):
        return False

    # Descripciones triviales
    if len(desc) < 5:
        return False
    if desc in ("—", "-", "", "— (0 PX)"):
        return False

    return True


def capitalizar(texto: str) -> str:
    """Asegura que el texto empiece con mayúscula."""
    if not texto:
        return texto
    return texto[0].upper() + texto[1:]


# ── Fix específico para hechizos ─────────────────────────────────────

def fix_hechizos(data: list[dict]) -> tuple[list[dict], dict]:
    stats = {"split_componentes_fixed": 0, "legal_lines_removed": 0, "entries_removed": 0}
    limpios = []

    for entry in data:
        if not es_entrada_valida(entry):
            stats["entries_removed"] += 1
            continue

        comp = entry.get("componentes", "")
        desc = entry.get("descripcion", "")

        # Fix 1: Componentes rotos (tiene "(" pero no cierra con ")")
        if "(" in comp and ")" not in comp:
            idx_paren = desc.find(")")
            if idx_paren >= 0:
                resto_comp = desc[:idx_paren + 1]
                comp_completo = comp + " " + resto_comp
                entry["componentes"] = comp_completo
                desc = desc[idx_paren + 1:].strip()
                stats["split_componentes_fixed"] += 1

        # Fix 2: Si descripción empieza con minúscula, capitalizar
        desc = capitalizar(desc)

        # Fix 3: Eliminar texto legal de descripcion
        desc_limpia = limpiar_texto(desc)
        if desc_limpia != desc:
            stats["legal_lines_removed"] += 1
        desc = desc_limpia

        # Si descripción quedó vacía, remover la entrada
        if not desc:
            stats["entries_removed"] += 1
            continue

        entry["descripcion"] = desc
        limpios.append(entry)

    return limpios, stats


# ── Fix genérico para listas de dicts ────────────────────────────────

def fix_generico(data: list[dict]) -> tuple[list[dict], dict]:
    stats = {"legal_lines_removed": 0, "entries_removed": 0}
    limpios = []

    for entry in data:
        if not es_entrada_valida(entry):
            stats["entries_removed"] += 1
            continue

        # Limpiar texto legal de todos los campos de texto
        for campo in ("descripcion", "contenido"):
            if campo in entry and entry[campo]:
                limpio = limpiar_texto(entry[campo])
                if limpio != entry[campo]:
                    stats["legal_lines_removed"] += 1
                entry[campo] = limpio

        # Remover entrada si el contenido quedó vacío
        if not entry.get("descripcion", "") and not entry.get("contenido", ""):
            stats["entries_removed"] += 1
            continue

        limpios.append(entry)

    return limpios, stats


# ── Main ─────────────────────────────────────────────────────────────

def main():
    check_only = "--check" in sys.argv
    stats_totales = {}

    for fpath in sorted(DATA_DIR.glob("*.json")):
        nombre = fpath.name
        data = json.loads(fpath.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue

        original_count = len(data)

        if nombre == "hechizos.json":
            limpios, stats = fix_hechizos(data)
        else:
            limpios, stats = fix_generico(data)

        stats["original"] = original_count
        stats["final"] = len(limpios)
        stats_totales[nombre] = stats

        if check_only:
            print(f"{nombre}: {original_count} → {len(limpios)} entries, "
                  f"removed {stats['entries_removed']}, "
                  f"legal cleaned {stats.get('legal_lines_removed', 0)}, "
                  f"componentes fixed {stats.get('split_componentes_fixed', 0)}")
        else:
            fpath.write_text(json.dumps(limpios, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"✓ {nombre}: {original_count} → {len(limpios)} ("
                  f"removed {stats['entries_removed']}, "
                  f"legal {stats.get('legal_lines_removed', 0)}, "
                  f"componentes {stats.get('split_componentes_fixed', 0)})")

    total_original = sum(s["original"] for s in stats_totales.values())
    total_final = sum(s["final"] for s in stats_totales.values())
    print(f"\nTotal: {total_original} → {total_final} entradas")
    print("Modo CHECK — no se modificaron archivos" if check_only else "Archivos actualizados.")

if __name__ == "__main__":
    main()
