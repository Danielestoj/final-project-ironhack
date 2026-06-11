import json
from pathlib import Path
from database import SessionLocal
from models.hechizo import HechizoDB
from models.objeto import ObjetoDB

DATA_DIR = Path(__file__).resolve().parent / "data"


def seed_hechizos():
    db = SessionLocal()
    try:
        if db.query(HechizoDB).count() > 0:
            return
        path = DATA_DIR / "hechizos.json"
        if not path.exists():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            db.add(HechizoDB(
                nombre=item.get("nombre", ""),
                nivel=item.get("nivel", 0),
                escuela=item.get("escuela", ""),
                tiempo=item.get("tiempo", ""),
                alcance=item.get("alcance", ""),
                componentes=item.get("componentes", ""),
                duracion=item.get("duracion", ""),
                descripcion=item.get("descripcion", ""),
                clases=json.dumps(item.get("clases", []), ensure_ascii=False),
            ))
        db.commit()
    finally:
        db.close()


def seed_objetos():
    db = SessionLocal()
    try:
        if db.query(ObjetoDB).count() > 0:
            return
        path = DATA_DIR / "objetos_equipo.json"
        if not path.exists():
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        items = []
        if isinstance(raw, dict):
            for seccion, lista in raw.items():
                for item in lista:
                    if isinstance(item, dict):
                        datos = {k: v for k, v in item.items() if k != "nombre"}
                        items.append({
                            "nombre": item.get("nombre", ""),
                            "seccion": seccion,
                            "datos": json.dumps(datos, ensure_ascii=False),
                        })
        for item in items:
            db.add(ObjetoDB(**item))
        db.commit()
    finally:
        db.close()


def seed_all():
    seed_hechizos()
    seed_objetos()


if __name__ == "__main__":
    seed_all()
