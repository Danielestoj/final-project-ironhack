import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def cargar_datos(nombre: str) -> list | dict:
    path = DATA_DIR / nombre
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []
