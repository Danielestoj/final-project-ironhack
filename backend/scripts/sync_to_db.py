"""
Sync To DB
===========
Lee los archivos .txt de backend/docs/, extrae datos estructurados
(hechizos, clases, razas, enemigos, etc.) y los guarda como JSON
en backend/data/ para que los endpoints los sirvan.

Uso:
    python scripts/sync_to_db.py                  # sincroniza todo
    python scripts/sync_to_db.py --check           # muestra estadísticas
"""

import sys
import os
import json
import re
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"
LLM_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-vl-3b-instruct")

TEXTOS_LEGALES = [
    "Documento de referencia del sistema",
    "Prohibida la reventa",
    "Tienes permiso para imprimir",
    "o fotocopiar este documento",
]


def es_nombre_valido(nombre: str) -> bool:
    """Filtra nombres fragmentados o que son claramente texto legal."""
    n = nombre.strip()
    if len(n) < 3:
        return False
    if n[0].islower() and n not in ("d100", "d20", "d12", "d10", "d8", "d6", "d4"):
        return False
    for t in TEXTOS_LEGALES:
        if t in n:
            return False
    return True


def limpiar_linea(linea: str) -> str:
    """Elimina texto legal incrustado."""
    result = linea
    for t in TEXTOS_LEGALES:
        idx = result.find(t)
        while idx >= 0:
            # Find end of line containing this text
            eol = result.find("\n", idx)
            if eol < 0:
                eol = len(result)
            # Remove the entire line containing legal text
            result = result[:idx] + result[eol:]
            idx = result.find(t)
    return result.strip()


def leer_txt(filename: str) -> str:
    path = DOCS_DIR / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def guardar_json(filename: str, data: list | dict):
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  → {filename}: {len(data) if isinstance(data, list) else 'ok'}", file=sys.stderr)


# ── Parseadores específicos ──────────────────────────────────────────────

def parsear_condiciones(texto: str) -> list[dict]:
    resultados = []
    for linea in texto.split("\n"):
        linea = linea.strip()
        if not linea or linea.startswith("#") or linea.startswith("Título"):
            continue
        linea = limpiar_linea(linea)
        if not linea:
            continue
        if ":" not in linea:
            continue
        nombre, _, desc = linea.partition(":")
        nombre = nombre.strip()
        desc = desc.strip()
        if not nombre or not desc:
            continue
        if not es_nombre_valido(nombre):
            continue
        if len(nombre) > 40 or len(desc) < 5:
            continue
        resultados.append({"nombre": nombre, "descripcion": desc, "efectos": [desc]})
    return resultados


def parsear_clases_razas(texto: str) -> list[dict]:
    resultados = []
    seccion = "general"
    idx = 0
    for linea in texto.split("\n"):
        idx += 1
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        linea = limpiar_linea(linea)
        if not linea:
            continue
        if linea.upper() == linea and linea.endswith(":") and len(linea) < 20:
            if "CLASE" in linea or "RAZA" in linea:
                seccion = "clase" if "CLASE" in linea else "raza"
            continue
        if ":" not in linea:
            continue
        nombre, _, desc = linea.partition(":")
        nombre = nombre.strip()
        desc = desc.strip()
        if not nombre or not desc:
            continue
        if not es_nombre_valido(nombre):
            continue
        if len(nombre) > 40 or len(desc) < 10:
            continue
        dg = ""
        hp = ""
        m = re.search(r"Dado de golpe:\s*(\S+)", desc)
        if m:
            dg = m.group(1)
        m = re.search(r"Habilidad principal:\s*(.+?)(?:\.|$)", desc)
        if m:
            hp = m.group(1).strip()
        resultados.append({
            "nombre": nombre,
            "tipo": seccion,
            "descripcion": desc,
            "dado_golpe": dg,
            "habilidad_principal": hp,
        })
    return resultados


def parsear_enemigos(texto: str) -> list[dict]:
    resultados = []
    for linea in texto.split("\n"):
        linea = linea.strip()
        if not linea or linea.startswith("#") or linea.startswith("Título"):
            continue
        linea = limpiar_linea(linea)
        if not linea:
            continue
        if ":" not in linea:
            continue
        nombre, _, resto = linea.partition(":")
        nombre = nombre.strip()
        resto = resto.strip()
        if not nombre or not resto:
            continue
        if not es_nombre_valido(nombre):
            continue
        if len(nombre) > 40 or len(resto) < 10:
            continue
        ca = ""
        pg = ""
        vel = ""
        m = re.search(r"CA\s*(\d+)", resto)
        if m:
            ca = m.group(1)
        m = re.search(r"PG\s*(\d+\s*\([^)]+\))", resto)
        if m:
            pg = m.group(1)
        m = re.search(r"Velocidad\s*(\d+)", resto)
        if m:
            vel = m.group(1)
        ataques = []
        m = re.search(r"Ataque:\s*(.+?)(?:\.\s*Habilidades|\.$)", resto)
        if m:
            ataques.append(m.group(1).strip())
        resultados.append({
            "nombre": nombre,
            "descripcion": resto,
            "ca": ca,
            "pg": pg,
            "velocidad": vel,
            "ataques": ataques,
        })
    return resultados


def parsear_objetos_equipo(texto: str) -> list[dict]:
    resultados = []
    for linea in texto.split("\n"):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        linea = limpiar_linea(linea)
        if not linea:
            continue
        if ":" in linea:
            nombre, _, desc = linea.partition(":")
            nombre = nombre.strip()
            desc = desc.strip()
            if not nombre or not desc:
                continue
            if not es_nombre_valido(nombre):
                continue
            if len(nombre) < 40 and len(desc) > 10:
                resultados.append({"nombre": nombre, "descripcion": desc, "tipo": "equipo"})
    return resultados


def parsear_reglas(texto: str, categoria: str) -> list[dict]:
    fragmentos = []
    for parrafo in texto.split("\n\n"):
        p = parrafo.strip()
        if not p or p.startswith("#") or p.startswith("Título") or len(p) < 50:
            continue
        p = limpiar_linea(p)
        if not p:
            continue
        fragmentos.append({"categoria": categoria, "contenido": p})
    return fragmentos


def parsear_hechizos_regex(texto: str) -> list[dict]:
    """Parsea hechizos del SRD usando regex (formato consistente: Nombre\\nEscuela nivel N\\n...)."""
    import re

    # Saltar directamente a la sección de descripciones individuales
    idx = texto.find("Agrandar/reducir")
    if idx < 0:
        idx = 0
    resto = texto[idx:]

    # Encontrar todos los inicios de bloques: línea con nombre, luego línea "Escuela nivel N"
    pattern = r'\n([A-ZÁÉÍÓÚÑ][a-záéíóúñ /]+)\n([A-Za-zÁÉÍÓÚÑáéíóúñ]+ nivel \d+)'
    matches = list(re.finditer(pattern, "\n" + resto))

    hechizos = []
    seen = set()

    for i, m in enumerate(matches):
        # Extract full block: from this match's name line to next match's name line
        block_start = m.start()  # includes the leading \n
        if i + 1 < len(matches):
            block_end = matches[i + 1].start()
        else:
            block_end = len(resto) - 1

        block = resto[block_start:block_end].strip()
        if not block:
            continue

        lines = block.split("\n")
        nombre = lines[0].strip()
        if len(nombre) > 60 or not nombre:
            continue

        # Escuela y nivel
        mm = re.match(r'([A-Za-zÁÉÍÓÚÑáéíóúñ]+)\s*nivel\s*(\d+)', lines[1].strip())
        if not mm:
            continue
        escuela = mm.group(1).strip()
        nivel_str = mm.group(2).strip()
        # Handle possible "Truco" (nivel 0)
        if nivel_str.isdigit():
            nivel = int(nivel_str)
        else:
            nivel = 0

        # Extraer campos
        tiempo = ""
        alcance = ""
        componentes = ""
        duracion = ""
        desc_lines = []

        for ln in lines[2:]:
            ln = ln.strip()
            if ln.startswith("Tiempo de lanzamiento:"):
                tiempo = ln.split(":", 1)[1].strip()
            elif ln.startswith("Alcance:"):
                alcance = ln.split(":", 1)[1].strip()
            elif ln.startswith("Componentes:"):
                componentes = ln.split(":", 1)[1].strip()
            elif ln.startswith("Duración:"):
                duracion = ln.split(":", 1)[1].strip()
            else:
                if ln:
                    desc_lines.append(ln)

        key = nombre.strip().lower()
        if key and key not in seen and nivel >= 0:
            seen.add(key)
            hechizos.append({
                "nombre": nombre.strip(),
                "nivel": nivel,
                "escuela": escuela,
                "tiempo": tiempo,
                "alcance": alcance,
                "componentes": componentes,
                "duracion": duracion,
                "descripcion": " ".join(desc_lines).strip(),
            })

    return hechizos


# ── Main ─────────────────────────────────────────────────────────────────

def sync_all():
    print("Sincronizando datos...", file=sys.stderr)

    # 1. Condiciones
    texto = leer_txt("condiciones.txt")
    if texto:
        data = parsear_condiciones(texto)
        guardar_json("condiciones.json", data)

    # 2. Clases y Razas
    texto = leer_txt("clases_y_razas.txt")
    if texto:
        data = parsear_clases_razas(texto)
        guardar_json("clases_razas.json", data)

    # 3. Enemigos
    texto = leer_txt("enemigos.txt")
    if texto:
        data = parsear_enemigos(texto)
        guardar_json("enemigos.json", data)

    # 4. Objetos y Equipo
    texto = leer_txt("objetos_y_equipo.txt")
    if texto:
        data = parsear_objetos_equipo(texto)
        guardar_json("objetos_equipo.json", data)

    # 5. Reglas
    for cat in ("reglas_basicas", "reglas_combate", "trasfondo_y_escenarios"):
        texto = leer_txt(f"{cat}.txt")
        if texto:
            data = parsear_reglas(texto, cat)
            guardar_json(f"{cat}.json", data)

    # 6. Hechizos (con LLM)
    texto = leer_txt("hechizos.txt")
    if texto and len(texto) > 500:
        print("  Extrayendo hechizos (regex)...", file=sys.stderr)
        data = parsear_hechizos_regex(texto)
        if data:
            guardar_json("hechizos.json", data)
        else:
            print("  (sin datos de hechizos)", file=sys.stderr)

    print("Sincronización completada.", file=sys.stderr)


def check_stats():
    print("=== Estadísticas de datos sincronizados ===")
    total = 0
    for f in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        n = len(data) if isinstance(data, list) else "—"
        print(f"  {f.name}: {n}")
        if isinstance(data, list):
            total += len(data)
    print(f"Total registros: {total}")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_stats()
    else:
        sync_all()
