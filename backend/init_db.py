"""Create all tables and seed the admin user."""

from datetime import datetime, timezone
from database import engine, SessionLocal, Base
from models.usuario import UsuarioDB
from models.personaje import PersonajeDB, PersonajeHechizo, PersonajeObjeto, PersonajeAtaque
from auth.password import hashear_password


def init():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("  OK")

    db = SessionLocal()
    try:
        admin = db.query(UsuarioDB).filter(UsuarioDB.email == "admin@admin.com").first()
        if not admin:
            admin = UsuarioDB(
                email="admin@admin.com",
                nombre="Admin",
                password_hash=hashear_password("12345678"),
                rol="admin",
                fecha_registro=datetime.now(timezone.utc),
            )
            db.add(admin)
            db.commit()
            print("  Admin creado: admin@admin.com / 12345678")
        else:
            print("  Admin ya existe")
    finally:
        db.close()

    print("\n¡Base de datos lista!")


if __name__ == "__main__":
    init()
