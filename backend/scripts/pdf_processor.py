"""
Procesador de PDFs de D&D
===========================
Extrae texto completo de un PDF, lo categoriza por temática usando
detección por palabras clave + LM Studio, y genera archivos .txt
separados en backend/docs/.

Uso:
    python pdf_processor.py --file "ruta/al/archivo.pdf"
    python pdf_processor.py --check                  # lista pendientes no procesados
    python pdf_processor.py --process-all            # procesa todos los pendientes

Requiere: PyMuPDF (fitz):
    pip install PyMuPDF
"""

import sys
import os
import json
import time
import hashlib
import re
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
PENDING_DIR = DOCS_DIR / "Pending"
PROCESSED_DIR = DOCS_DIR / "Processed"
LOG_FILE = DOCS_DIR / "processing_log.json"
OUTPUT_DIR = BASE_DIR / "docs"

LLM_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-vl-3b-instruct")

# Palabras clave por categoría (orden de prioridad)
KEYWORDS = {
    "hechizos": [
        "hechizo", "conjuro", "lanzar", "magia", "mágico", "arcano", "divino",
        "bola de fuego", "proyectil", "armadura mágica", "curar heridas",
        "dormir", "telaraña", "rayo", "luz", "truco", "nivel", "escuela",
        "evocación", "abjuración", "encantamiento", "nigromancia", "ilusión",
        "componentes", "verbal", "somático", "material", "concentración",
    ],
    "reglas_combate": [
        "combate", "iniciativa", "atacar", "daño", "golpe", "crítico",
        "acción", "reacción", "acción bonus", "turno", "ca", "clase de armadura",
        "cobertura", "flanqueo", "cuerpo a cuerpo", "a distancia",
        "empujar", "agarrar", "derribado", "movimiento", "velocidad",
    ],
    "condiciones": [
        "cegado", "hechizado", "ensordecido", "asustado", "agarrado",
        "inmovilizado", "paralizado", "petrificado", "envenenado",
        "derribado", "inconsciente", "aturdido", "incapacitado", "preso",
        "condición", "salvación contra la muerte",
    ],
    "clases_y_razas": [
        "guerrero", "mago", "pícaro", "clérigo", "bárbaro", "explorador",
        "paladín", "druida", "hechicero", "brujo", "monje", "artífice",
        "humano", "elfo", "enano", "mediano", "semielfo", "semiorco",
        "gnomo", "tiefling", "dracónido", "clase", "raza", "trasfondo",
        "dado de golpe", "competencia", "habilidad", "talento",
        "característica", "multiclase",
    ],
    "enemigos": [
        "criatura", "monstruo", "bestia", "bestiario", "enemigo",
        "goblin", "esqueleto", "zombi", "bandido", "lobo", "oso",
        "dragón", "slime", "muerto viviente", "no-muerto", "demonio",
        "pj", "pg", "puntos de golpe", "ca ", "desafío",
    ],
    "objetos_y_equipo": [
        "arma", "armadura", "escudo", "objeto mágico", "equipo",
        "espada", "arco", "ballesta", "daga", "hacha", "martillo",
        "poción", "anillo", "varita", "bastón", "armadura de placas",
        "arma marcial", "arma simple", "monedas", "oro", "tesoro",
    ],
    "reglas_basicas": [
        "prueba", "habilidad", "dificultad", "cd ", "clase de dificultad",
        "descanso", "corto", "largo", "experiencia", "nivel", "subir",
        "puntos de golpe", "pg", "dado de golpe", "salvación",
        "ventaja", "desventaja", "d20", "dado", "personaje",
    ],
    "trasfondo_y_escenarios": [
        "trasfondo", "historia", "personalidad", "ideal", "vínculo",
        "defecto", "escenario", "reino", "ciudad", "mundo",
        "aventura", "campaña", "dungeon", "mazmorra", "exploración",
    ],
}

CATEGORIES = list(KEYWORDS.keys())

CATEGORY_PROMPTS = {
    "reglas_basicas": "Reglas básicas del juego (pruebas de habilidad, descansos, experiencia, niveles)",
    "reglas_combate": "Reglas de combate (acciones, iniciativa, daño, cobertura, maniobras)",
    "condiciones": "Condiciones de estado (cegado, paralizado, envenenado, etc.)",
    "hechizos": "Hechizos y magia (conjuros, escuelas de magia, componentes)",
    "clases_y_razas": "Clases de personaje, razas, trasfondos y habilidades",
    "enemigos": "Criaturas, monstruos, bestiario y enemigos",
    "objetos_y_equipo": "Objetos mágicos, armas, armaduras, equipo de aventurero",
    "trasfondo_y_escenarios": "Trasfondos de personaje, escenarios, lore del mundo",
}


# ── Helpers ────────────────────────────────────────────────────────────────

def cargar_log() -> dict:
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    return {"procesados": {}}


def guardar_log(log: dict):
    LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def listar_pendientes() -> list[Path]:
    if not PENDING_DIR.exists():
        return []
    return sorted(
        [f for f in PENDING_DIR.iterdir() if f.suffix.lower() in (".pdf", ".txt", ".md")],
        key=lambda f: f.stat().st_mtime,
    )


def extraer_texto_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        print("ERROR: PyMuPDF no instalado. Ejecuta: pip install PyMuPDF", file=sys.stderr)
        sys.exit(1)
    doc = fitz.open(str(path))
    paginas = []
    for pagina in doc:
        paginas.append(pagina.get_text())
    doc.close()
    return "\n".join(paginas)


def extraer_texto_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def detectar_categoria_por_keywords(texto: str) -> str:
    """Detecta la categoría más probable de un fragmento usando keywords."""
    texto_lower = texto.lower()
    puntajes = {}
    for cat, palabras in KEYWORDS.items():
        score = sum(1 for p in palabras if p in texto_lower)
        if score > 0:
            puntajes[cat] = score
    if not puntajes:
        return "reglas_basicas"
    return max(puntajes, key=puntajes.get)


def dividir_por_secciones(texto: str) -> list[tuple[str, str]]:
    """Divide el texto en secciones (párrafos) y asigna categoría a cada una."""
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    secciones = []
    for parrafo in parrafos:
        if len(parrafo) < 30:
            continue
        cat = detectar_categoria_por_keywords(parrafo)
        secciones.append((cat, parrafo))
    return secciones


def agrupar_por_categoria(secciones: list[tuple[str, str]]) -> dict[str, list[str]]:
    """Agrupa los fragmentos por categoría."""
    agrupado: dict[str, list[str]] = {cat: [] for cat in CATEGORIES}
    for cat, texto in secciones:
        agrupado[cat].append(texto)
    return {cat: frags for cat, frags in agrupado.items() if frags}


def refinar_con_llm(categoria: str, fragmentos: list[str]) -> list[str]:
    """Usa LM Studio para limpiar y organizar los fragmentos de una categoría."""
    if not fragmentos:
        return fragmentos

    from openai import OpenAI
    client = OpenAI(base_url=LLM_URL, api_key="lm-studio")

    texto_unido = "\n\n".join(fragmentos)

    if len(texto_unido) < 200:
        return fragmentos

    prompt = f"""Eres un asistente que organiza contenido de Dungeons & Dragons 5e.

La categoría es: {categoria} — {CATEGORY_PROMPTS.get(categoria, "")}

A continuación hay fragmentos de texto extraídos de documentos de D&D que pertenecen a esta categoría.
Tu tarea es:
1. Eliminar duplicados y contenido irrelevante
2. Ordenar la información de forma lógica
3. Devolver SOLO un array JSON de strings, sin explicaciones

Ejemplo: ["texto limpio 1", "texto limpio 2"]

FRAGMENTOS:
{texto_unido[:6000]}
"""
    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000,
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        resultado = json.loads(raw)
        if isinstance(resultado, list) and len(resultado) > 0:
            return resultado
    except Exception:
        pass
    return fragmentos


def guardar_categorias(categorias: dict, nombre_base: str, usar_llm: bool = True):
    guardados = []
    for cat, fragmentos in categorias.items():
        if not fragmentos:
            continue

        if usar_llm and len(fragmentos) > 1:
            print(f"  Refinando {cat} con LLM ({len(fragmentos)} fragmentos)...", file=sys.stderr)
            fragmentos = refinar_con_llm(cat, fragmentos)
            time.sleep(0.3)

        filename = f"{cat}.txt"
        filepath = OUTPUT_DIR / filename
        modo = "a" if filepath.exists() else "w"
        with open(filepath, modo, encoding="utf-8") as f:
            if filepath.exists() and filepath.stat().st_size > 0:
                f.write("\n\n")
            f.write(f"## Fuente: {nombre_base}\n\n")
            for frag in fragmentos:
                f.write(frag.strip() + "\n\n")
        guardados.append(filename)
    return guardados


def procesar_archivo(path: Path) -> dict:
    print(f"  Procesando: {path.name}", file=sys.stderr)

    if path.suffix.lower() == ".pdf":
        texto = extraer_texto_pdf(path)
    else:
        texto = extraer_texto_txt(path)

    if not texto.strip():
        return {"status": "error", "reason": "Texto vacío"}

    print(f"  Texto extraído: {len(texto):,} caracteres", file=sys.stderr)

    print(f"  Detectando categorías por keywords...", file=sys.stderr)
    secciones = dividir_por_secciones(texto)
    print(f"  {len(secciones)} secciones detectadas", file=sys.stderr)

    categorias = agrupar_por_categoria(secciones)
    for cat, frags in categorias.items():
        print(f"    {cat}: {len(frags)} fragmentos", file=sys.stderr)

    nombre_base = path.stem
    guardados = guardar_categorias(categorias, nombre_base, usar_llm=True)
    print(f"  Archivos actualizados: {guardados}", file=sys.stderr)

    destino = PROCESSED_DIR / path.name
    path.rename(destino)
    print(f"  Movido a: Processed/{path.name}", file=sys.stderr)

    return {
        "status": "ok",
        "archivo": path.name,
        "categorias": list(categorias.keys()),
        "total_fragmentos": sum(len(v) for v in categorias.values()),
        "archivos_guardados": guardados,
    }


def trigger_sync():
    """Llama al endpoint sync-to-db después de procesar archivos."""
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/pdf/sync-to-db",
            method="POST",
            data=b"{}",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            print(f"  Sync triggered: {resp.status}", file=sys.stderr)
            return json.loads(body)
    except Exception as e:
        print(f"  Sync error (non-fatal): {e}", file=sys.stderr)
        return None


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if "--check" in sys.argv:
        pendientes = listar_pendientes()
        log = cargar_log()
        procesados_log = log.get("procesados", {})
        no_procesados = []
        for p in pendientes:
            h = file_hash(p)
            ya_procesado = h in procesados_log
            archivo_en_processded = PROCESSED_DIR / p.name
            archivo_procesado_existe = ya_procesado and archivo_en_processded.exists()
            if not archivo_procesado_existe:
                no_procesados.append(str(p.name))
        print(json.dumps(no_procesados))
        return

    if "--process-all" in sys.argv:
        pendientes = listar_pendientes()
        if not pendientes:
            print(json.dumps({"ok": True, "mensaje": "No hay archivos pendientes"}))
            return
        resultados = []
        for p in pendientes:
            h = file_hash(p)
            r = procesar_archivo(p)
            resultados.append(r)
            log = cargar_log()
            log["procesados"][h] = {
                "nombre": p.name,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "resultado": r,
            }
            guardar_log(log)
        trigger_sync()
        print(json.dumps({"ok": True, "resultados": resultados}))
        return

    if "--file" in sys.argv:
        idx = sys.argv.index("--file") + 1
        if idx >= len(sys.argv):
            print(json.dumps({"ok": False, "error": "Falta ruta del archivo"}))
            return
        path = Path(sys.argv[idx])
        if not path.exists():
            print(json.dumps({"ok": False, "error": f"Archivo no encontrado: {path}"}))
            return
        h = file_hash(path)
        r = procesar_archivo(path)
        log = cargar_log()
        log["procesados"][h] = {
            "nombre": path.name,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "resultado": r,
        }
        guardar_log(log)
        trigger_sync()
        print(json.dumps({"ok": True, "resultado": r}))
        return

    print("Uso:")
    print("  python pdf_processor.py --file <ruta>")
    print("  python pdf_processor.py --check")
    print("  python pdf_processor.py --process-all")


if __name__ == "__main__":
    main()
