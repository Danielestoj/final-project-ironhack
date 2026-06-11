import io
import json
import random
from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.jwt import obtener_usuario_actual
from models.personaje import PersonajeCrear, PersonajeActualizar, PersonajeOut, PersonajeDB, PersonajeHechizo, PersonajeObjeto, PersonajeAtaque
from models.usuario import UsuarioDB
from services.personaje_service import personaje_service

router = APIRouter(prefix="/personajes", tags=["Personajes"])
UsuarioActual = Annotated[UsuarioDB, Depends(obtener_usuario_actual)]
DBSession = Annotated[Session, Depends(get_db)]

RAZAS = ["Humano", "Elfo", "Enano", "Mediano", "Semielfo", "Semiorco", "Gnomo", "Tiefling", "Dracónido"]
CLASES = ["Guerrero", "Mago", "Pícaro", "Clérigo", "Bárbaro", "Explorador", "Paladín", "Druida", "Brujo", "Hechicero", "Monje"]
ALINEAMIENTOS = ["Legal bueno", "Neutral bueno", "Caótico bueno", "Legal neutral", "Neutral", "Caótico neutral", "Legal malvado", "Neutral malvado", "Caótico malvado"]


def _generar_stats_4d6():
    stats = []
    for _ in range(6):
        tiradas = [random.randint(1, 6) for _ in range(4)]
        tiradas.remove(min(tiradas))
        stats.append(sum(tiradas))
    return stats


def _calcular_pg(clase: str, nivel: int, mod_con: int) -> int:
    dado = {"Guerrero": 10, "Mago": 6, "Pícaro": 8, "Clérigo": 8, "Bárbaro": 12,
            "Explorador": 10, "Paladín": 10, "Druida": 8, "Brujo": 8, "Hechicero": 6, "Monje": 8}
    d = dado.get(clase, 8)
    return d + mod_con + (nivel - 1) * (d // 2 + 1 + mod_con)


@router.get("/", response_model=List[PersonajeOut])
def listar_personajes(usuario: UsuarioActual, db: DBSession):
    return personaje_service.listar(db, usuario.id)


@router.get("/{personaje_id}", response_model=PersonajeOut)
def obtener_personaje(personaje_id: int, usuario: UsuarioActual, db: DBSession):
    try:
        pj = personaje_service.obtener(db, personaje_id)
        if pj.usuario_id != usuario.id:
            raise HTTPException(status_code=403, detail="No tienes acceso a este personaje")
        return pj
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")


@router.post("/", response_model=PersonajeOut, status_code=status.HTTP_201_CREATED)
def crear_personaje(datos: PersonajeCrear, usuario: UsuarioActual, db: DBSession):
    return personaje_service.crear(db, datos, usuario.id)


@router.post("/random", response_model=PersonajeOut, status_code=status.HTTP_201_CREATED)
def crear_personaje_aleatorio(usuario: UsuarioActual, db: DBSession):
    stats = _generar_stats_4d6()
    raza = random.choice(RAZAS)
    clase = random.choice(CLASES)
    nivel = random.choice([1, 2, 3])
    stat_names = ["fuerza", "destreza", "constitucion", "inteligencia", "sabiduria", "carisma"]
    stat_dict = dict(zip(stat_names, stats))
    mod_con = (stats[2] - 10) // 2
    pg = _calcular_pg(clase, nivel, mod_con)
    nombres = ["Aldric", "Borin", "Caelia", "Doran", "Elara", "Finn", "Gromm", "Halia", "Ignar", "Jora"]
    nombre = random.choice(nombres)

    datos = PersonajeCrear(
        nombre=nombre, raza=raza, clase=clase, nivel=nivel,
        alineamiento=random.choice(ALINEAMIENTOS),
        pg_max=pg, pg_actual=pg,
        **stat_dict,
    )
    return personaje_service.crear(db, datos, usuario.id)


@router.put("/{personaje_id}", response_model=PersonajeOut)
def actualizar_personaje(personaje_id: int, datos: PersonajeActualizar, usuario: UsuarioActual, db: DBSession):
    try:
        return personaje_service.actualizar(db, personaje_id, datos, usuario.id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.post("/{personaje_id}/level-up", response_model=PersonajeOut)
def level_up(personaje_id: int, usuario: UsuarioActual, db: DBSession):
    try:
        pj = personaje_service.obtener(db, personaje_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    if pj.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    if pj.nivel >= 20:
        raise HTTPException(status_code=400, detail="Ya estás en nivel máximo")

    nuevo_nivel = pj.nivel + 1
    mod_con = (pj.constitucion - 10) // 2
    dado_pg = {"Guerrero": 10, "Mago": 6, "Pícaro": 8, "Clérigo": 8, "Bárbaro": 12,
               "Explorador": 10, "Paladín": 10, "Druida": 8, "Brujo": 8, "Hechicero": 6, "Monje": 8}
    incremento_pg = random.randint(1, dado_pg.get(pj.clase, 8)) + mod_con
    if incremento_pg < 1:
        incremento_pg = 1

    pj_db = db.query(PersonajeDB).filter(PersonajeDB.id == personaje_id).first()
    pj_db.nivel = nuevo_nivel
    pj_db.pg_max += incremento_pg
    pj_db.pg_actual = pj_db.pg_max
    pj_db.experiencia += 300 * nuevo_nivel
    pj_db.bonif_competencia = 2 + (nuevo_nivel - 1) // 4
    pj_db.fecha_actualizacion = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pj_db)
    from services.personaje_service import _pj_to_out
    return _pj_to_out(pj_db)


@router.get("/{personaje_id}/pdf")
def exportar_pdf(personaje_id: int, usuario: UsuarioActual, db: DBSession):
    try:
        pj = personaje_service.obtener(db, personaje_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    if pj.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes acceso")

    from fpdf import FPDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    LM = 10
    USABLE = 190
    CX = lambda w: LM + (USABLE - w) / 2

    def sec_hdr(y, title):
        pdf.set_xy(LM, y)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.set_draw_color(160, 160, 160)
        pdf.cell(USABLE, 5.5, title.upper(), border="B")
        return y + 7.5

    def cell(x, y, w, h, label="", value="", val_size=9):
        pdf.set_draw_color(170, 170, 170)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, w, h)
        if label:
            pdf.set_font("Helvetica", "", 6)
            pdf.set_text_color(120, 120, 120)
            pdf.set_xy(x + 1.2, y + 0.6)
            pdf.cell(w - 2.4, 2.5, label)
        if value:
            pdf.set_font("Helvetica", "", val_size)
            pdf.set_text_color(30, 30, 30)
            vx = x + 1.2
            vy = y + (h - 3) / 2 + 0.5
            pdf.set_xy(vx, vy)
            pdf.cell(w - 2.4, 3, str(value))

    def cbox(x, y, s, checked):
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.4)
        pdf.rect(x, y, s, s)
        if checked:
            pdf.set_fill_color(60, 60, 60)
            pdf.rect(x + 0.6, y + 0.6, s - 1.2, s - 1.2, style="F")

    def prof_dot(x, y, s, level):
        """level: 0=empty, 1=filled, 2=filled+expert"""
        pdf.set_draw_color(100, 100, 100)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, s, s)
        if level >= 1:
            pdf.set_fill_color(60, 60, 60)
            pdf.rect(x + 0.5, y + 0.5, s - 1, s - 1, style="F")
        if level >= 2:
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(x + 1.5, y + 1.5, s - 3, s - 3, style="F")

    STAT_NAMES = {
        "fuerza": "FUE", "destreza": "DES", "constitucion": "CON",
        "inteligencia": "INT", "sabiduria": "SAB", "carisma": "CAR",
    }
    SAVE_KEYS = ["fuerza", "destreza", "constitucion", "inteligencia", "sabiduria", "carisma"]
    SAVE_LABELS = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]
    SKILLS = [
        ("acrobacias", "Acrobacias", "destreza"),
        ("arcanos", "Arcanos", "inteligencia"),
        ("atletismo", "Atletismo", "fuerza"),
        ("engaño", "Engaño", "carisma"),
        ("historia", "Historia", "inteligencia"),
        ("interpretacion", "Interpretación", "carisma"),
        ("intimidacion", "Intimidación", "carisma"),
        ("investigacion", "Investigación", "inteligencia"),
        ("juego_manos", "Juego de Manos", "destreza"),
        ("medicina", "Medicina", "sabiduria"),
        ("naturaleza", "Naturaleza", "inteligencia"),
        ("percepcion", "Percepción", "sabiduria"),
        ("perspicacia", "Perspicacia", "sabiduria"),
        ("persuasion", "Persuasión", "carisma"),
        ("religion", "Religión", "inteligencia"),
        ("sigilo", "Sigilo", "destreza"),
        ("supervivencia", "Supervivencia", "sabiduria"),
        ("trato_animales", "Trato con Animales", "sabiduria"),
    ]
    MONEY = [("pc", "PC"), ("pe", "PE"), ("ppt", "PPT"), ("po", "PO"), ("pp", "PP")]
    CB = 3.5  # checkbox size

    # ═══════════════════════════════════════════════
    # 1 — HEADER
    # ═══════════════════════════════════════════════
    y = LM

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 30)
    pdf.set_xy(LM, y)
    pdf.cell(USABLE, 10, pj.nombre or "Personaje", align="C")
    y += 11

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(LM, y)
    parts = [p for p in [pj.raza, pj.clase, f"Nivel {pj.nivel}" if pj.nivel else ""] if p]
    pdf.cell(USABLE, 6, " · ".join(parts), align="C")
    y += 8

    # Inspiration + bonus row
    cell(LM, y, 55, 9, "INSPIRACIÓN", "✔" if pj.inspiracion else "", 8)
    cbx = LM + 55 + 2
    cbox(cbx, y + 2, CB, pj.inspiracion)
    cell(LM + 70, y, 35, 9, "BONIF. COMP.", str(pj.bonif_competencia or 2))
    y += 11

    # ═══════════════════════════════════════════════
    # 2 — STATS
    # ═══════════════════════════════════════════════
    y = sec_hdr(y, "Características")
    sw = 29
    gap = (USABLE - 6 * sw) / 5
    for i, s in enumerate(STAT_NAMES.keys()):
        val = getattr(pj, s, 10) or 10
        mod = (val - 10) // 2
        mod_str = f"{'+' if mod >= 0 else ''}{mod}"
        x = LM + i * (sw + gap)
        pdf.set_draw_color(170, 170, 170)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, sw, 17)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(120, 120, 120)
        pdf.set_xy(x + 1, y + 0.5)
        pdf.cell(sw - 2, 3, STAT_NAMES[s], align="C")
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 30)
        pdf.set_xy(x + 1, y + 4)
        pdf.cell(sw - 2, 6, str(val), align="C")
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(180, 60, 60)
        pdf.set_xy(x + 1, y + 10.5)
        pdf.cell(sw - 2, 5, mod_str, align="C")
    y += 19

    # ═══════════════════════════════════════════════
    # 3 — COMBAT
    # ═══════════════════════════════════════════════
    y = sec_hdr(y, "Combate")
    combat_fields = [
        ("CA", pj.clase_armadura), ("PG Máx", pj.pg_max), ("PG Act", pj.pg_actual),
        ("PG Temp", pj.pg_temporales), ("Iniciativa", pj.iniciativa),
        ("Velocidad", f"{pj.velocidad}m" if pj.velocidad else ""),
        ("DG", pj.dados_golpe),
    ]
    cw = USABLE / len(combat_fields)
    for i, (label, val) in enumerate(combat_fields):
        x = LM + i * cw
        cell(x, y, cw - 0.5, 9, label, str(val) if val is not None and val != "" else "")
    y += 10.5

    # Death saves
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.set_xy(LM, y)
    pdf.cell(20, 5, "Salv. Muerte:")
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(12, 5, "Éxitos:")
    for i in range(3):
        cbox(pdf.get_x() + i * (CB + 1), y + 0.5, CB, i < (pj.muerte_exitos or 0))
    pdf.set_xy(LM + 80, y)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(10, 5, "Fallos:")
    for i in range(3):
        cbox(pdf.get_x() + i * (CB + 1), y + 0.5, CB, i < (pj.muerte_fallos or 0))
    y += 7

    # ═══════════════════════════════════════════════
    # 4 — SAVING THROWS
    # ═══════════════════════════════════════════════
    y = sec_hdr(y, "Tiradas de Salvación")
    saves_per_row = 3
    sv_w = USABLE / saves_per_row
    for i, key in enumerate(SAVE_KEYS):
        prof = getattr(pj, f"{key}_salv_prof", False)
        val = getattr(pj, key, 10) or 10
        mod = (val - 10) // 2
        mod_str = f"{'+' if mod >= 0 else ''}{mod}"
        col = i % saves_per_row
        row = i // saves_per_row
        sx = LM + col * sv_w
        sy = y + row * 7
        cbox(sx, sy + 1.5, CB, prof)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(50, 50, 50)
        pdf.set_xy(sx + CB + 2, sy + 1.5)
        pdf.cell(sv_w - CB - 14, 3.5, SAVE_LABELS[i])
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(180, 60, 60)
        pdf.set_xy(sx + sv_w - 12, sy + 1.5)
        pdf.cell(10, 3.5, mod_str, align="R")
    y += 7 * ((len(SAVE_KEYS) + saves_per_row - 1) // saves_per_row) + 1

    # ═══════════════════════════════════════════════
    # 5 — SKILLS
    # ═══════════════════════════════════════════════
    y = sec_hdr(y, "Habilidades")
    sk_cols = 2
    sk_w = USABLE / sk_cols
    sk_per_col = (len(SKILLS) + sk_cols - 1) // sk_cols
    for i, (key, label, stat) in enumerate(SKILLS):
        prof_val = getattr(pj, f"{key}_prof", 0) or 0
        mod = ((getattr(pj, stat, 10) or 10) - 10) // 2
        total = mod + (prof_val == 1 and (pj.bonif_competencia or 2) or prof_val == 2 and 2 * (pj.bonif_competencia or 2) or 0)
        total_str = f"{'+' if total >= 0 else ''}{total}"
        col = i // sk_per_col
        row = i % sk_per_col
        sx = LM + col * sk_w
        sy = y + row * 5.5
        prof_dot(sx + 0.5, sy + 1, 3.5, prof_val)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(50, 50, 50)
        pdf.set_xy(sx + 5.5, sy + 1)
        pdf.cell(sk_w - 24, 3.5, label)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(130, 130, 130)
        pdf.cell(12, 3.5, f"({stat[:3].upper()})")
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(180, 60, 60)
        pdf.cell(8, 3.5, total_str, align="R")
    y += sk_per_col * 5.5 + 2

    # ═══════════════════════════════════════════════
    # 6 — ATTACKS
    # ═══════════════════════════════════════════════
    y = sec_hdr(y, "Ataques y Conjuros")
    atk_headers = ["Nombre", "Bonif. Ataque", "Daño", "Tipo"]
    atk_w = [72, 36, 42, 40]
    atk_h = 7
    # Header row
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(100, 100, 100)
    pdf.set_draw_color(170, 170, 170)
    pdf.set_line_width(0.3)
    hx = LM
    for wi, hdr in enumerate(atk_headers):
        pdf.rect(hx, y, atk_w[wi], atk_h)
        pdf.set_xy(hx + 1, y + 1.5)
        pdf.cell(atk_w[wi] - 2, 3.5, hdr)
        hx += atk_w[wi]
    y += atk_h

    # Attack rows (existing + empty)
    atk_rows = list(pj.ataques or [])
    while len(atk_rows) < 3:
        atk_rows.append(None)
    for atk in atk_rows:
        vals = [atk.nombre if atk else "", atk.bonif_ataque if atk else "", atk.danio if atk else "", atk.tipo if atk else ""]
        hx = LM
        for wi, v in enumerate(vals):
            pdf.set_draw_color(170, 170, 170)
            pdf.set_line_width(0.3)
            pdf.rect(hx, y, atk_w[wi], atk_h)
            if v:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(30, 30, 30)
                pdf.set_xy(hx + 1.5, y + 1.5)
                pdf.cell(atk_w[wi] - 3, 3.5, v)
            hx += atk_w[wi]
        y += atk_h
    y += 1

    # ═══════════════════════════════════════════════
    # 7 — EQUIPMENT
    # ═══════════════════════════════════════════════
    y = sec_hdr(y, "Equipo")
    eq_h = 18
    pdf.set_draw_color(170, 170, 170)
    pdf.set_line_width(0.3)
    pdf.rect(LM, y, USABLE, eq_h)
    objetos = [o.nombre_objeto for o in (pj.objetos or [])]
    if objetos:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 30, 30)
        pdf.set_xy(LM + 2, y + 1.5)
        pdf.multi_cell(USABLE - 4, 4, ", ".join(objetos))
    y += eq_h + 1

    # Money
    mw = USABLE / len(MONEY)
    for i, (k, label) in enumerate(MONEY):
        cell(LM + i * mw, y, mw - 0.5, 8, label, str(getattr(pj, k, 0) or 0))
    y += 10

    # Competences
    if pj.competencias_idiomas:
        y = sec_hdr(y, "Competencias e Idiomas")
        ch = 14
        pdf.set_draw_color(170, 170, 170)
        pdf.set_line_width(0.3)
        pdf.rect(LM, y, USABLE, ch)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(30, 30, 30)
        pdf.set_xy(LM + 2, y + 1)
        pdf.multi_cell(USABLE - 4, 3.5, pj.competencias_idiomas)
        y += ch + 1

    # ═══════════════════════════════════════════════
    # 8 — SPELLS
    # ═══════════════════════════════════════════════
    slots_raw = pj.espacios_conjuros or "{}"
    try:
        slots = json.loads(slots_raw)
    except (json.JSONDecodeError, TypeError):
        slots = {}
    has_spellcasting = pj.clase_lanzadora or pj.hechizos or any(
        v.get("total", 0) for v in slots.values()
    )
    if has_spellcasting:
        y = sec_hdr(y, "Conjuros")
        spell_fields = [
            ("Clase Lanzadora", pj.clase_lanzadora),
            ("Carac.", pj.carac_lanzamiento),
            ("Salvación CD", pj.salvacion_conjuro),
            ("Bonif. Ataque", pj.bonif_ataque_conjuro),
        ]
        sfw = USABLE / len(spell_fields)
        for i, (label, val) in enumerate(spell_fields):
            cell(LM + i * sfw, y, sfw - 0.5, 9, label, str(val) if val else "")
        y += 10.5

        # Cantrips
        trucos = [h for h in (pj.hechizos or []) if h.es_truco]
        if trucos:
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(LM, y)
            pdf.cell(12, 4.5, "Trucos:")
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, 4.5, ", ".join(h.nombre_hechizo for h in trucos))
            y += 5.5

        # Spell levels
        for lv in range(1, 10):
            slot_data = slots.get(str(lv), {})
            total = slot_data.get("total", 0)
            lvl_spells = [h for h in (pj.hechizos or []) if h.nivel == lv and not h.es_truco]
            if total == 0 and not lvl_spells:
                continue
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(100, 100, 100)
            pdf.set_xy(LM, y)
            pdf.cell(14, 4.5, f"Nivel {lv}:")
            # Spell slot dots
            gastados = slot_data.get("gastados", 0)
            for i in range(total):
                cbox(pdf.get_x() + i * (CB + 1), y + 0.5, CB, i >= gastados)
            pdf.set_xy(LM + 14 + total * (CB + 1) + 2, y)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, 4.5, ", ".join(h.nombre_hechizo for h in lvl_spells))
            y += 5.5
        y += 1

    # ═══════════════════════════════════════════════
    # 9 — FEATURES & TRAITS
    # ═══════════════════════════════════════════════
    feature_fields = [
        ("Rasgos y Atributos", pj.rasgos_atributos, 2),
        ("Rasgos de Personalidad", pj.rasgos_personalidad, 1.5),
        ("Ideales", pj.ideales, 1.5),
        ("Vínculos", pj.vinculos, 1.5),
        ("Defectos", pj.defectos, 1.5),
    ]
    for label, text, rows in feature_fields:
        if y > 250:
            pdf.add_page()
            y = LM
        y = sec_hdr(y, label)
        bh = 6 * rows
        pdf.set_draw_color(170, 170, 170)
        pdf.set_line_width(0.3)
        pdf.rect(LM, y, USABLE, bh)
        if text:
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(30, 30, 30)
            pdf.set_xy(LM + 2, y + 1)
            pdf.multi_cell(USABLE - 4, 4, text)
        y += bh + 1

    # ═══════════════════════════════════════════════
    # 10 — APPEARANCE & HISTORY
    # ═══════════════════════════════════════════════
    if y > 240:
        pdf.add_page()
        y = LM
    y = sec_hdr(y, "Apariencia e Historia")
    app_fields = [
        ("Edad", pj.edad), ("Altura", pj.altura), ("Peso", pj.peso),
        ("Ojos", pj.ojos), ("Piel", pj.piel), ("Cabello", pj.cabello),
    ]
    afw = USABLE / 3
    row_count = (len(app_fields) + 2) // 3
    for ri in range(row_count):
        for ci in range(3):
            idx = ri * 3 + ci
            if idx < len(app_fields):
                label, val = app_fields[idx]
                cell(LM + ci * afw, y, afw - 0.5, 8, label, str(val) if val else "")
        y += 9.5

    # Large text boxes
    for label, text in [("Apariencia", pj.apariencia), ("Historia", pj.historia),
                         ("Aliados y Org.", pj.aliados_organizaciones),
                         ("Tesoro", pj.tesoro)]:
        if y > 255:
            pdf.add_page()
            y = LM
        y = sec_hdr(y, label) if label else y
        bh = 16
        pdf.set_draw_color(170, 170, 170)
        pdf.set_line_width(0.3)
        pdf.rect(LM, y, USABLE, bh)
        if text:
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(30, 30, 30)
            pdf.set_xy(LM + 2, y + 1)
            pdf.multi_cell(USABLE - 4, 4, text)
        y += bh + 1

    buf = io.BytesIO(pdf.output())
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={pj.nombre}.pdf"})


@router.delete("/{personaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_personaje(personaje_id: int, usuario: UsuarioActual, db: DBSession):
    try:
        personaje_service.eliminar(db, personaje_id, usuario.id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
