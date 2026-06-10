import os, json, time, hashlib, subprocess, sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/pdf", tags=["PDF Processor"])

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
PENDING_DIR = DOCS_DIR / "Pending"
PROCESSED_DIR = DOCS_DIR / "Processed"
LOG_FILE = DOCS_DIR / "processing_log.json"


class ProcessRequest(BaseModel):
    filename: str


class SyncRequest(BaseModel):
    game_slug: str = "dnd"


def cargar_log() -> dict:
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    return {"procesados": {}}


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


@router.post("/check-pending")
def check_pending():
    if not PENDING_DIR.exists():
        return {"pending": [], "count": 0}

    log = cargar_log()
    pendientes = sorted(
        [f for f in PENDING_DIR.iterdir() if f.suffix.lower() in (".pdf", ".txt", ".md")],
        key=lambda f: f.stat().st_mtime,
    )

    no_procesados = []
    for p in pendientes:
        h = file_hash(p)
        if h not in log.get("procesados", {}):
            no_procesados.append(p.name)

    return {"pending": no_procesados, "count": len(no_procesados)}


@router.post("/process")
def process_file(body: ProcessRequest):
    filepath = PENDING_DIR / body.filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {body.filename}")

    try:
        result = subprocess.run(
            [sys.executable, "scripts/pdf_processor.py", "--file", str(filepath)],
            capture_output=True, text=True, timeout=120, cwd=BASE_DIR,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error del script: {result.stderr.strip() or result.stdout.strip()}")
        data = json.loads(result.stdout.strip())
        return data
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado procesando el PDF")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error al parsear la salida del script")


@router.post("/sync-to-db")
def sync_to_db(body: SyncRequest):
    from ingestar import ingestar_game
    try:
        ingestar_game(body.game_slug)
        return {"status": "ok", "game_slug": body.game_slug}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
