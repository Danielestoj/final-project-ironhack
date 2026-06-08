from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from auth.jwt import crear_token, obtener_usuario_actual
from models.usuario import TokenRespuesta, UsuarioCrear, UsuarioLogin, UsuarioPublico, UsuarioDB

router = APIRouter(prefix="/auth", tags=["Autenticación"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]


@router.post("/registro", response_model=TokenRespuesta, status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioCrear):
    from services.usuario_service import usuario_service
    try:
        usuario = usuario_service.registrar(datos)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    token = crear_token({"sub": usuario.email, "rol": usuario.rol})
    return TokenRespuesta(
        access_token=token,
        expira_en_segundos=3600,
        usuario=UsuarioPublico(
            id=usuario.id, email=usuario.email, nombre=usuario.nombre,
            rol=usuario.rol, fecha_registro=usuario.fecha_registro,
        ),
    )


@router.post("/login", response_model=TokenRespuesta)
def login(credenciales: UsuarioLogin):
    from services.usuario_service import usuario_service
    try:
        usuario = usuario_service.autenticar(credenciales.email, credenciales.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")
    token = crear_token({"sub": usuario.email, "rol": usuario.rol})
    return TokenRespuesta(
        access_token=token,
        expira_en_segundos=3600,
        usuario=UsuarioPublico(
            id=usuario.id, email=usuario.email, nombre=usuario.nombre,
            rol=usuario.rol, fecha_registro=usuario.fecha_registro,
        ),
    )


@router.get("/perfil", response_model=UsuarioPublico)
def ver_perfil(usuario: UsuarioActual):
    return UsuarioPublico(
        id=usuario.id, email=usuario.email, nombre=usuario.nombre,
        rol=usuario.rol, fecha_registro=usuario.fecha_registro,
    )
