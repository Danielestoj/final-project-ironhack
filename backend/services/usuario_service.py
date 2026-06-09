from datetime import datetime, timezone
from sqlalchemy.orm import Session
from auth.password import hashear_password, verificar_password
from models.usuario import UsuarioDB, UsuarioCrear


class UsuarioService:
    def registrar(self, db: Session, datos: UsuarioCrear) -> UsuarioDB:
        existe = db.query(UsuarioDB).filter(UsuarioDB.email == datos.email).first()
        if existe:
            raise ValueError(f"El email '{datos.email}' ya está registrado")
        usuario = UsuarioDB(
            email=datos.email,
            nombre=datos.nombre,
            password_hash=hashear_password(datos.password),
            fecha_registro=datetime.now(timezone.utc),
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    def autenticar(self, db: Session, email: str, password: str) -> UsuarioDB:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
        if not usuario or not verificar_password(password, usuario.password_hash):
            raise ValueError("Email o contraseña incorrectos")
        return usuario

    def obtener_por_email(self, db: Session, email: str) -> UsuarioDB:
        usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
        if not usuario:
            raise KeyError(email)
        return usuario


usuario_service = UsuarioService()
