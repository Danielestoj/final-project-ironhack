from datetime import datetime, timezone
from typing import Dict

from auth.password import hashear_password, verificar_password
from models.usuario import UsuarioDB, UsuarioCrear


class UsuarioService:
    def __init__(self) -> None:
        self._store: Dict[str, UsuarioDB] = {}
        self._next_id: int = 1
        self._crear_admin_inicial()

    def _crear_admin_inicial(self) -> None:
        admin = UsuarioDB(
            id=self._next_id,
            email="admin@admin.com",
            nombre="Admin",
            rol="admin",
            fecha_registro=datetime.now(timezone.utc),
            password_hash=hashear_password("12345678"),
        )
        self._store[admin.email] = admin
        self._next_id += 1

    def registrar(self, datos: UsuarioCrear) -> UsuarioDB:
        if datos.email in self._store:
            raise ValueError(f"El email '{datos.email}' ya está registrado")
        usuario = UsuarioDB(
            id=self._next_id,
            email=datos.email,
            nombre=datos.nombre,
            rol="usuario",
            fecha_registro=datetime.now(timezone.utc),
            password_hash=hashear_password(datos.password),
        )
        self._store[datos.email] = usuario
        self._next_id += 1
        return usuario

    def autenticar(self, email: str, password: str) -> UsuarioDB:
        usuario = self._store.get(email)
        if not usuario or not verificar_password(password, usuario.password_hash):
            raise ValueError("Email o contraseña incorrectos")
        return usuario

    def obtener_por_email(self, email: str) -> UsuarioDB:
        if email not in self._store:
            raise KeyError(email)
        return self._store[email]


usuario_service = UsuarioService()
