import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from auth.jwt import obtener_usuario_actual
from models.usuario import UsuarioDB

router = APIRouter(prefix="/api/games", tags=["Games"])

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
GAMES_FILE = DATA_DIR / "games.json"
GAMES_DIR = BASE_DIR / "games"

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

CATEGORY_NAV = {
    "hechizos": {"path": "hechizos", "label": "Hechizos", "icono": "✨"},
    "reglas_combate": {"path": "combate", "label": "Combate", "icono": "⚔️"},
    "condiciones": {"path": "condiciones", "label": "Condiciones", "icono": "⚡"},
    "clases_y_razas": {"path": "clases-razas", "label": "Clases y Razas", "icono": "📚"},
    "enemigos": {"path": "enemigos", "label": "Enemigos", "icono": "👹"},
    "objetos_y_equipo": {"path": "objetos", "label": "Objetos", "icono": "🛡️"},
    "reglas_basicas": {"path": "reglas", "label": "Reglas", "icono": "📖"},
    "trasfondo_y_escenarios": {"path": "trasfondo", "label": "Trasfondo", "icono": "🌍"},
}


def _cargar_juegos() -> list[dict]:
    if GAMES_FILE.exists():
        return json.loads(GAMES_FILE.read_text(encoding="utf-8"))
    return []


def _guardar_juegos(juegos: list[dict]):
    GAMES_FILE.write_text(json.dumps(juegos, indent=2, ensure_ascii=False), encoding="utf-8")


def _slugify(nombre: str) -> str:
    slug = nombre.lower().replace(" ", "-").replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug


def _detectar_categoria_por_keywords(texto: str) -> str:
    texto_lower = texto.lower()
    puntajes = {}
    for cat, palabras in KEYWORDS.items():
        score = sum(1 for p in palabras if p in texto_lower)
        if score > 0:
            puntajes[cat] = score
    if not puntajes:
        return "reglas_basicas"
    return max(puntajes, key=puntajes.get)


def _dividir_por_secciones(texto: str) -> list[tuple[str, str]]:
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    secciones = []
    for parrafo in parrafos:
        if len(parrafo) < 30:
            continue
        cat = _detectar_categoria_por_keywords(parrafo)
        secciones.append((cat, parrafo))
    return secciones


def _agrupar_por_categoria(secciones: list[tuple[str, str]]) -> dict[str, list[str]]:
    agrupado: dict[str, list[str]] = {}
    for cat, texto in secciones:
        if cat not in agrupado:
            agrupado[cat] = []
        agrupado[cat].append(texto)
    return agrupado


def _extraer_texto_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        raise HTTPException(status_code=500, detail="PyMuPDF no instalado. pip install PyMuPDF")
    doc = fitz.open(str(path))
    paginas = [pagina.get_text() for pagina in doc]
    doc.close()
    return "\n".join(paginas)


def _extraer_texto_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


NAV_PATH_MAP = {v["path"]: k for k, v in CATEGORY_NAV.items()}


def _generar_nav(categorias: list[str]) -> list[dict]:
    nav = [{"path": "chat", "label": "Chat", "icono": "💬"}]
    visited_paths = {"chat"}
    for cat in categorias:
        if cat in CATEGORY_NAV:
            entry = CATEGORY_NAV[cat]
        else:
            entry = {
                "path": cat,
                "label": cat.replace("_", " ").replace("-", " ").title(),
                "icono": "📋",
            }
        if entry["path"] in visited_paths:
            continue
        visited_paths.add(entry["path"])
        nav.append(entry)
    nav.append({"path": "perfil", "label": "Perfil", "icono": "👤"})
    return nav


def _guardar_categorias(docs_dir: Path, categorias: dict, nombre_base: str):
    for cat, fragmentos in categorias.items():
        if not fragmentos:
            continue
        txt_path = docs_dir / f"{cat}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"## Fuente: {nombre_base}\n\n")
            for frag in fragmentos:
                f.write(frag.strip() + "\n\n")


def _sincronizar_juego(docs_dir: Path, data_dir: Path):
    TEXTOS_LEGALES = [
        "Documento de referencia del sistema",
        "Prohibida la reventa",
        "Tienes permiso para imprimir",
        "o fotocopiar este documento",
    ]

    def es_nombre_valido(nombre):
        n = nombre.strip()
        if len(n) < 3:
            return False
        if n[0].islower() and n not in ("d100", "d20", "d12", "d10", "d8", "d6", "d4"):
            return False
        for t in TEXTOS_LEGALES:
            if t in n:
                return False
        return True

    def leer_txt(filename):
        path = docs_dir / filename
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def guardar_json(filename, data):
        data_dir.mkdir(parents=True, exist_ok=True)
        path = data_dir / filename
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def parsear_generico(texto):
        resultados = []
        for linea in texto.split("\n"):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
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
            resultados.append({"nombre": nombre, "descripcion": desc})
        return resultados

    def parsear_reglas(texto, categoria):
        fragmentos = []
        for parrafo in texto.split("\n\n"):
            p = parrafo.strip()
            if not p or p.startswith("#") or len(p) < 40:
                continue
            fragmentos.append({"categoria": categoria, "contenido": p})
        return fragmentos

    for cat in ("hechizos", "condiciones", "clases_y_razas", "enemigos", "objetos_y_equipo"):
        texto = leer_txt(f"{cat}.txt")
        if texto:
            data = parsear_generico(texto)
            guardar_json(f"{cat}.json", data)

    for cat in ("reglas_basicas", "reglas_combate", "trasfondo_y_escenarios"):
        texto = leer_txt(f"{cat}.txt")
        if texto:
            data = parsear_reglas(texto, cat)
            guardar_json(f"{cat}.json", data)


def _procesar_archivo_juego(game_dir: Path, filename: str) -> list[str]:
    docs_dir = game_dir / "docs"
    pending_dir = docs_dir / "Pending"
    processed_dir = docs_dir / "Processed"
    data_dir = game_dir / "data"

    filepath = pending_dir / filename
    if not filepath.exists():
        return []

    if filepath.suffix.lower() == ".pdf":
        texto = _extraer_texto_pdf(filepath)
    else:
        texto = _extraer_texto_txt(filepath)

    if not texto.strip():
        return []

    secciones = _dividir_por_secciones(texto)
    categorias = _agrupar_por_categoria(secciones)

    _guardar_categorias(docs_dir, categorias, filepath.stem)
    _sincronizar_juego(docs_dir, data_dir)

    processed_dir.mkdir(parents=True, exist_ok=True)
    destino = processed_dir / filepath.name
    filepath.rename(destino)

    return list(categorias.keys())


@router.get("/")
def listar_juegos():
    return _cargar_juegos()


@router.get("/{slug}")
def obtener_juego(slug: str):
    juegos = _cargar_juegos()
    for j in juegos:
        if j["slug"] == slug:
            return j
    raise HTTPException(status_code=404, detail="Juego no encontrado")


@router.get("/{slug}/data/{section}")
def obtener_datos_seccion(slug: str, section: str):
    juegos = _cargar_juegos()
    if not any(j["slug"] == slug for j in juegos):
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    internal_cat = NAV_PATH_MAP.get(section, section)

    data_file = GAMES_DIR / slug / "data" / f"{internal_cat}.json"
    if data_file.exists():
        return json.loads(data_file.read_text(encoding="utf-8"))

    fallback = DATA_DIR / f"{internal_cat}.json"
    if fallback.exists():
        return json.loads(fallback.read_text(encoding="utf-8"))

    return []


@router.post("/")
async def crear_juego(
    nombre: str = Form(...),
    descripcion: str = Form(""),
    icono: str = Form("🎮"),
    categorias: str = Form("[]"),
    archivo: UploadFile = File(...),
    usuario: UsuarioDB = Depends(obtener_usuario_actual),
):
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden crear juegos")

    juegos = _cargar_juegos()
    slug = _slugify(nombre)
    if any(j["slug"] == slug for j in juegos):
        raise HTTPException(status_code=409, detail=f"Ya existe un juego con slug '{slug}'")

    game_dir = GAMES_DIR / slug
    game_dir.mkdir(parents=True, exist_ok=True)
    (game_dir / "data").mkdir(exist_ok=True)
    docs_dir = game_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "Pending").mkdir(exist_ok=True)
    (docs_dir / "Processed").mkdir(exist_ok=True)

    filepath = docs_dir / "Pending" / archivo.filename
    content = await archivo.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    filepath.write_bytes(content)

    detectadas = _procesar_archivo_juego(game_dir, archivo.filename)
    try:
        manuales = json.loads(categorias)
        if not isinstance(manuales, list):
            manuales = []
    except json.JSONDecodeError:
        manuales = []
    categorias_final = list(dict.fromkeys(detectadas + manuales))
    nav = _generar_nav(categorias_final)

    nuevo = {
        "slug": slug,
        "nombre": nombre,
        "icono": icono,
        "descripcion": descripcion,
        "nav": nav,
        "plantilla": False,
    }
    juegos.append(nuevo)
    _guardar_juegos(juegos)

    (game_dir / "config.json").write_text(json.dumps(nuevo, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Indexar en ChromaDB (colección específica del juego) ──
    try:
        from ingestar import ingestar_game
        ingestar_game(slug)
    except Exception as exc:
        print(f"[N8N] Error indexando ChromaDB para {slug}: {exc}")

    # ── Notificar a N8N ──
    try:
        import httpx
        httpx.post(
            "https://danielestojeda.app.n8n.cloud/webhook/dnd-game-created",
            json={
                "slug": slug,
                "nombre": nombre,
                "categorias": categorias_final,
                "timestamp": datetime.utcnow().isoformat(),
            },
            timeout=5,
        )
    except Exception:
        pass  # N8N no crítico

    return nuevo


@router.delete("/{slug}")
def eliminar_juego(slug: str, usuario: UsuarioDB = Depends(obtener_usuario_actual)):
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar juegos")

    juegos = _cargar_juegos()
    juego = next((j for j in juegos if j["slug"] == slug), None)
    if not juego:
        raise HTTPException(status_code=404, detail="Juego no encontrado")

    juegos = [j for j in juegos if j["slug"] != slug]
    _guardar_juegos(juegos)

    game_dir = GAMES_DIR / slug
    if game_dir.exists():
        shutil.rmtree(game_dir)

    return {"ok": True, "mensaje": f"Juego '{juego['nombre']}' eliminado"}
