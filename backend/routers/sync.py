import subprocess, sys, json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/pdf", tags=["Sync"])

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
VENV_PYTHON = Path(__file__).resolve().parent.parent / "venv" / "Scripts" / "python.exe"


@router.post("/sync-to-db")
def sync_to_db():
    try:
        python = VENV_PYTHON if VENV_PYTHON.exists() else sys.executable
        script = SCRIPTS_DIR / "sync_to_db.py"
        result = subprocess.run(
            [str(python), str(script)],
            capture_output=True, text=True, timeout=300,
        )
        return {
            "ok": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Sync timed out after 300s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
