import json
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from models.personaje import (
    PersonajeDB, PersonajeHechizo, PersonajeObjeto, PersonajeAtaque,
    PersonajeCrear, PersonajeActualizar, PersonajeOut,
    HechizoSchema, ObjetoSchema, AtaqueSchema,
)


def _pj_to_out(pj: PersonajeDB) -> PersonajeOut:
    return PersonajeOut(
        id=pj.id,
        usuario_id=pj.usuario_id,
        nombre=pj.nombre,
        nombre_jugador=pj.nombre_jugador or "",
        raza=pj.raza or "",
        clase=pj.clase or "",
        nivel=pj.nivel or 1,
        trasfondo=pj.trasfondo or "",
        experiencia=pj.experiencia or 0,
        alineamiento=pj.alineamiento or "",
        fuerza=pj.fuerza or 10,
        destreza=pj.destreza or 10,
        constitucion=pj.constitucion or 10,
        inteligencia=pj.inteligencia or 10,
        sabiduria=pj.sabiduria or 10,
        carisma=pj.carisma or 10,
        clase_armadura=pj.clase_armadura or 10,
        iniciativa=pj.iniciativa or 0,
        velocidad=pj.velocidad or 9,
        pg_max=pj.pg_max or 10,
        pg_actual=pj.pg_actual or 10,
        pg_temporales=pj.pg_temporales or 0,
        dados_golpe=pj.dados_golpe or "1d10",
        muerte_exitos=pj.muerte_exitos or 0,
        muerte_fallos=pj.muerte_fallos or 0,
        inspiracion=pj.inspiracion or False,
        bonif_competencia=pj.bonif_competencia or 2,
        fuerza_salv_prof=pj.fuerza_salv_prof or False,
        destreza_salv_prof=pj.destreza_salv_prof or False,
        constitucion_salv_prof=pj.constitucion_salv_prof or False,
        inteligencia_salv_prof=pj.inteligencia_salv_prof or False,
        sabiduria_salv_prof=pj.sabiduria_salv_prof or False,
        carisma_salv_prof=pj.carisma_salv_prof or False,
        acrobacias_prof=pj.acrobacias_prof or 0,
        arcanos_prof=pj.arcanos_prof or 0,
        atletismo_prof=pj.atletismo_prof or 0,
        engaño_prof=pj.engaño_prof or 0,
        historia_prof=pj.historia_prof or 0,
        interpretacion_prof=pj.interpretacion_prof or 0,
        intimidacion_prof=pj.intimidacion_prof or 0,
        investigacion_prof=pj.investigacion_prof or 0,
        juego_manos_prof=pj.juego_manos_prof or 0,
        medicina_prof=pj.medicina_prof or 0,
        naturaleza_prof=pj.naturaleza_prof or 0,
        percepcion_prof=pj.percepcion_prof or 0,
        perspicacia_prof=pj.perspicacia_prof or 0,
        persuasion_prof=pj.persuasion_prof or 0,
        religion_prof=pj.religion_prof or 0,
        sigilo_prof=pj.sigilo_prof or 0,
        supervivencia_prof=pj.supervivencia_prof or 0,
        trato_animales_prof=pj.trato_animales_prof or 0,
        competencias_idiomas=pj.competencias_idiomas or "",
        rasgos_atributos=pj.rasgos_atributos or "",
        rasgos_personalidad=pj.rasgos_personalidad or "",
        ideales=pj.ideales or "",
        vinculos=pj.vinculos or "",
        defectos=pj.defectos or "",
        edad=pj.edad or "",
        altura=pj.altura or "",
        peso=pj.peso or "",
        ojos=pj.ojos or "",
        piel=pj.piel or "",
        cabello=pj.cabello or "",
        apariencia=pj.apariencia or "",
        historia=pj.historia or "",
        aliados_organizaciones=pj.aliados_organizaciones or "",
        tesoro=pj.tesoro or "",
        rasgos_adicionales=pj.rasgos_adicionales or "",
        pc=pj.pc or 0,
        pe=pj.pe or 0,
        ppt=pj.ppt or 0,
        po=pj.po or 0,
        pp=pj.pp or 0,
        clase_lanzadora=pj.clase_lanzadora or "",
        carac_lanzamiento=pj.carac_lanzamiento or "",
        salvacion_conjuro=pj.salvacion_conjuro or 0,
        bonif_ataque_conjuro=pj.bonif_ataque_conjuro or 0,
        espacios_conjuros=pj.espacios_conjuros or "{}",
        hechizos=[HechizoSchema.model_validate(h) for h in pj.hechizos],
        objetos=[ObjetoSchema.model_validate(o) for o in pj.objetos],
        ataques=[AtaqueSchema.model_validate(a) for a in pj.ataques],
        hechizos_favoritos=[h.nombre_hechizo for h in pj.hechizos],
        fecha_creacion=pj.fecha_creacion,
        fecha_actualizacion=pj.fecha_actualizacion,
    )


def _sync_relations(db: Session, pj: PersonajeDB, datos: PersonajeActualizar):
    if datos.hechizos is not None:
        db.query(PersonajeHechizo).filter(PersonajeHechizo.personaje_id == pj.id).delete()
        for h in datos.hechizos:
            db.add(PersonajeHechizo(personaje_id=pj.id, **h.model_dump()))
    if datos.objetos is not None:
        db.query(PersonajeObjeto).filter(PersonajeObjeto.personaje_id == pj.id).delete()
        for o in datos.objetos:
            db.add(PersonajeObjeto(personaje_id=pj.id, **o.model_dump()))
    if datos.ataques is not None:
        db.query(PersonajeAtaque).filter(PersonajeAtaque.personaje_id == pj.id).delete()
        for a in datos.ataques:
            db.add(PersonajeAtaque(personaje_id=pj.id, **a.model_dump()))


class PersonajeService:
    def listar(self, db: Session, usuario_id: int) -> List[PersonajeOut]:
        pjs = db.query(PersonajeDB).filter(PersonajeDB.usuario_id == usuario_id).all()
        return [_pj_to_out(p) for p in pjs]

    def obtener(self, db: Session, personaje_id: int) -> PersonajeOut:
        pj = db.query(PersonajeDB).filter(PersonajeDB.id == personaje_id).first()
        if not pj:
            raise KeyError(f"Personaje {personaje_id} no encontrado")
        return _pj_to_out(pj)

    def crear(self, db: Session, datos: PersonajeCrear, usuario_id: int) -> PersonajeOut:
        ahora = datetime.now(timezone.utc)
        pj = PersonajeDB(usuario_id=usuario_id, fecha_creacion=ahora, fecha_actualizacion=ahora)
        for key, value in datos.model_dump(exclude={"hechizos", "objetos", "ataques", "hechizos_favoritos"}).items():
            if value is not None:
                setattr(pj, key, value)
        db.add(pj)
        db.flush()
        # Relations
        for h in datos.hechizos:
            db.add(PersonajeHechizo(personaje_id=pj.id, **h.model_dump()))
        for o in datos.objetos:
            db.add(PersonajeObjeto(personaje_id=pj.id, **o.model_dump()))
        for a in datos.ataques:
            db.add(PersonajeAtaque(personaje_id=pj.id, **a.model_dump()))
        db.commit()
        db.refresh(pj)
        return _pj_to_out(pj)

    def actualizar(self, db: Session, personaje_id: int, datos: PersonajeActualizar, usuario_id: int) -> PersonajeOut:
        pj = db.query(PersonajeDB).filter(PersonajeDB.id == personaje_id).first()
        if not pj:
            raise KeyError(f"Personaje {personaje_id} no encontrado")
        if pj.usuario_id != usuario_id:
            raise ValueError("No tienes permiso para modificar este personaje")
        update_data = datos.model_dump(exclude_unset=True, exclude={"hechizos", "objetos", "ataques", "hechizos_favoritos"})
        for key, value in update_data.items():
            if value is not None:
                setattr(pj, key, value)
        pj.fecha_actualizacion = datetime.now(timezone.utc)
        _sync_relations(db, pj, datos)
        db.commit()
        db.refresh(pj)
        return _pj_to_out(pj)

    def eliminar(self, db: Session, personaje_id: int, usuario_id: int) -> None:
        pj = db.query(PersonajeDB).filter(PersonajeDB.id == personaje_id).first()
        if not pj:
            raise KeyError(f"Personaje {personaje_id} no encontrado")
        if pj.usuario_id != usuario_id:
            raise ValueError("No tienes permiso para eliminar este personaje")
        db.delete(pj)
        db.commit()


personaje_service = PersonajeService()
