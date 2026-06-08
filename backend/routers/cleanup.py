import subprocess, sys, json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/data", tags=["Cleanup"])

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
VENV_PYTHON = Path(__file__).resolve().parent.parent / "venv" / "Scripts" / "python.exe"


@router.post("/cleanup")
def cleanup_data():
    try:
        python = VENV_PYTHON if VENV_PYTHON.exists() else sys.executable
        script = SCRIPTS_DIR / "cleanup_data.py"
        result = subprocess.run(
            [str(python), str(script)],
            capture_output=True, text=True, timeout=120,
        )
        return {
            "ok": True,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Cleanup timed out after 120s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
