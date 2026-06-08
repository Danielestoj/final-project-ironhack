import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/games", tags=["Games"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GAMES_FILE = DATA_DIR / "games.json"


def _cargar_juegos() -> list[dict]:
    if GAMES_FILE.exists():
        return json.loads(GAMES_FILE.read_text(encoding="utf-8"))
    return []


def _guardar_juegos(juegos: list[dict]):
    GAMES_FILE.write_text(json.dumps(juegos, indent=2, ensure_ascii=False), encoding="utf-8")


PLANTILLA_DND = {
    "nav": [
        {"path": "chat", "label": "Chat", "icono": "💬"},
        {"path": "hechizos", "label": "Hechizos", "icono": "✨"},
        {"path": "personajes", "label": "Personajes", "icono": "🧝"},
        {"path": "condiciones", "label": "Condiciones", "icono": "⚡"},
        {"path": "clases-razas", "label": "Clases y Razas", "icono": "📚"},
        {"path": "enemigos", "label": "Enemigos", "icono": "👹"},
        {"path": "objetos", "label": "Objetos", "icono": "🛡️"},
        {"path": "perfil", "label": "Perfil", "icono": "👤"},
    ],
    "plantilla": False,
}


class CrearJuegoRequest(BaseModel):
    nombre: str
    descripcion: str = ""
    icono: str = "🎮"


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


@router.post("/")
def crear_juego(body: CrearJuegoRequest):
    juegos = _cargar_juegos()
    slug = body.nombre.lower().replace(" ", "-").replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    if any(j["slug"] == slug for j in juegos):
        raise HTTPException(status_code=409, detail=f"Ya existe un juego con slug '{slug}'")
    nuevo = {
        "slug": slug,
        "nombre": body.nombre,
        "icono": body.icono,
        "descripcion": body.descripcion,
        **PLANTILLA_DND,
    }
    juegos.append(nuevo)
    _guardar_juegos(juegos)

    # Crear estructura de directorios para el nuevo juego
    games_dir = Path(__file__).resolve().parent.parent / "games"
    game_dir = games_dir / slug
    game_dir.mkdir(parents=True, exist_ok=True)
    (game_dir / "data").mkdir(exist_ok=True)
    (game_dir / "docs").mkdir(exist_ok=True)
    (game_dir / "docs" / "Pending").mkdir(exist_ok=True)
    (game_dir / "docs" / "Processed").mkdir(exist_ok=True)
    (game_dir / "config.json").write_text(json.dumps(nuevo, indent=2, ensure_ascii=False), encoding="utf-8")

    return nuevo
