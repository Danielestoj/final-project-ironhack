from datetime import datetime, timezone
from typing import Dict, List

from models.personaje import PersonajeDB, PersonajeCrear, PersonajeActualizar


class PersonajeService:
    def __init__(self) -> None:
        self._store: Dict[int, PersonajeDB] = {}
        self._next_id: int = 1

    def listar(self, usuario_id: int) -> List[PersonajeDB]:
        return [p for p in self._store.values() if p.usuario_id == usuario_id]

    def obtener(self, personaje_id: int) -> PersonajeDB:
        if personaje_id not in self._store:
            raise KeyError(f"Personaje {personaje_id} no encontrado")
        return self._store[personaje_id]

    def crear(self, datos: PersonajeCrear, usuario_id: int) -> PersonajeDB:
        ahora = datetime.now(timezone.utc)
        personaje = PersonajeDB(
            id=self._next_id,
            **datos.model_dump(),
            usuario_id=usuario_id,
            fecha_creacion=ahora,
            fecha_actualizacion=ahora,
        )
        self._store[personaje.id] = personaje
        self._next_id += 1
        return personaje

    def actualizar(self, personaje_id: int, datos: PersonajeActualizar, usuario_id: int) -> PersonajeDB:
        if personaje_id not in self._store:
            raise KeyError(f"Personaje {personaje_id} no encontrado")
        personaje = self._store[personaje_id]
        if personaje.usuario_id != usuario_id:
            raise ValueError("No tienes permiso para modificar este personaje")
        update_data = datos.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(personaje, key, value)
        personaje.fecha_actualizacion = datetime.now(timezone.utc)
        return personaje

    def eliminar(self, personaje_id: int, usuario_id: int) -> None:
        if personaje_id not in self._store:
            raise KeyError(f"Personaje {personaje_id} no encontrado")
        if self._store[personaje_id].usuario_id != usuario_id:
            raise ValueError("No tienes permiso para eliminar este personaje")
        del self._store[personaje_id]


personaje_service = PersonajeService()
