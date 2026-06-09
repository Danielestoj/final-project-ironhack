import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

try:
    import fitz
except ImportError:
    print("PyMuPDF no instalado. pip install PyMuPDF")
    sys.exit(1)

PDF_PATH = Path.home() / "Downloads" / "SRD_CC_v5.1_ES.pdf"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

HEADER_FOOTER_PAT = re.compile(
    r"Documento de referencia del sistema 5\.1\.\s*\d+\s*"
    r"Prohibida la reventa\. Tienes permiso para imprimir\s*"
    r"o fotocopiar este documento solo para uso personal\.\s*"
)

MONSTER_NAME_RE = re.compile(r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:[- ][A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*$")

MONSTER_TYPE_RE = re.compile(
    r"^\s*(Aberración|Bestia|Celestial|Cieno|Constructo|Dracónido|Elemental|"
    r"Fata|Gigante|Humanoide|Monstruosidad|Muerto viviente|No-muerto|Planta|"
    r"Sabio|Demonio|Diablo|Dragón|Engendro|Esbirro|Espíritu|Gigante|"
    r"Humanoide|Monstruosidad|Mortales|No-muerto|Ofidios|"
    r"Pnj|Titán|Vampiro)\s+(Pequeño|Mediano|Grande|Enorme|Diminuto)"
    r"(?: \(.*?\))?,\s*(?:cualquier|legal|caótico|neutral|bueno|malvado)"
)

FIELD_NAMES = [
    "Clase de Armadura",
    "Puntos de golpe",
    "Velocidad",
    "Tiradas de salvación",
    "Habilidades",
    "Resistencia a daño",
    "Inmunidad a daño",
    "Inmunidad a estados",
    "Vulnerabilidad a daño",
    "Sentidos",
    "Idiomas",
    "Desafío",
]

ABILITY_NAMES = ["FUE", "DES", "CON", "INT", "SAB", "CAR"]

NPC_NAMES = [
    "Acólito", "Archimago", "Asesino", "Bandido", "Batidor",
    "Berserker", "Caballero", "Capitán bandido", "Druida",
    "Espía", "Gladiador", "Guardia", "Guerrero tribal",
    "Mago", "Matón", "Noble", "Plebeyo", "Sacerdote",
    "Sectario", "Sectario fanático", "Veterano",
]


def clean_text(text):
    text = HEADER_FOOTER_PAT.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def extract_full_text(doc, start_page, end_page):
    lines = []
    for i in range(start_page - 1, end_page):
        text = doc[i].get_text()
        text = clean_text(text)
        lines.append(text)
    return "\n".join(lines)


def parse_abilities(text):
    match = re.search(
        r"FUE\s+DES\s+CON\s+INT\s+SAB\s+CAR\s*\n"
        r"([\d\s(−) +]+)",
        text,
    )
    if not match:
        return {}
    vals = re.findall(r"(\d+)\s*\([−\-]\s*\d+\)|(\d+)\s*\(\+*\s*\d+\)", match.group(1))
    # simpler: just find all numbers
    nums = re.findall(r"\d+", match.group(1))
    nums = [int(n) for n in nums[:6]]
    if len(nums) < 6:
        return {}
    return {
        "fue": nums[0],
        "des": nums[1],
        "con": nums[2],
        "int": nums[3],
        "sab": nums[4],
        "car": nums[5],
    }


def parse_monster_stat_block(text):
    lines = text.strip().split("\n")
    lines = [l.strip() for l in lines if l.strip()]
    if len(lines) < 4:
        return None

    name = lines[0]
    tipo_linea = lines[1]

    stats = {"nombre": name, "tipo": tipo_linea}

    i = 2
    while i < len(lines):
        line = lines[i]
        matched = False
        for field in FIELD_NAMES:
            if line.startswith(field + ":"):
                val = line[len(field) + 1:].strip()
                key = field.lower().replace(" ", "_").replace("í", "i")
                stats[key] = val
                matched = True
                break
        if matched:
            i += 1
        else:
            # Check for ability scores
            if all(ab in line for ab in ["FUE", "DES", "CON", "INT", "SAB", "CAR"]):
                # collect ability text
                ab_text = line
                i += 1
                while i < len(lines) and not any(
                    lines[i].startswith(f + ":") for f in FIELD_NAMES
                ) and not any(lines[i].startswith(f)
                              for f in ["FUE", "DES", "CON", "INT", "SAB", "CAR", "Acciones", "Reacciones"]):
                    ab_text += " " + lines[i]
                    i += 1
                abilities = parse_abilities(ab_text)
                if abilities:
                    stats["caracteristicas"] = abilities
                continue
            elif line.startswith("Acciones"):
                # Collect actions until next monster or end
                acciones_text = []
                i += 1
                while i < len(lines):
                    # Check if this is a new monster name
                    if len(lines[i].split()) <= 4 and not lines[i].startswith(tuple(FIELD_NAMES + ["FUE", "DES"])):
                        # Could be next monster name
                        pass
                    acciones_text.append(lines[i])
                    i += 1
                if acciones_text:
                    stats["acciones"] = "\n".join(acciones_text)
                break
            elif line.startswith("Reacciones"):
                reacciones_text = []
                i += 1
                while i < len(lines):
                    reacciones_text.append(lines[i])
                    i += 1
                if reacciones_text:
                    stats["reacciones"] = "\n".join(reacciones_text)
                break
            else:
                i += 1

    return stats


def split_monsters(text):
    blocks = []
    current = []
    lines = text.split("\n")

    section_headers = {f"Monstruos ({chr(c)})" for c in range(ord("A"), ord("Z") + 1)}
    section_headers.add("Apéndice MM-B")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line in section_headers or line.startswith("Monstruos ("):
            i += 1
            continue

        # Check for NPC sections
        if "Personajes no jugadores" in line or line.startswith("Personalizar un PNJ"):
            i += 1
            continue

        # Detect start of a monster/NPC block: name line followed by type line
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            is_monster_name = bool(re.search(
                r"Humanoide|Aberración|Bestia|Celestial|Cieno|Constructo|Dracónido|Elemental|"
                r"Fata|Gigante|Monstruosidad|Muerto viviente|No-muerto|Planta|"
                r"Demonio|Diablo|Dragón|Engendro|Titán|Vampiro|Mortales",
                next_line[:60],
            ))
            if is_monster_name:
                if current:
                    blocks.append("\n".join(current))
                current = [line]
                i += 1
                continue

        if current:
            current.append(line)
        i += 1

    if current:
        blocks.append("\n".join(current))
    return blocks


def extract_enemigos():
    print("Extrayendo monstruos y PNJs...")
    doc = fitz.open(str(PDF_PATH))
    text = extract_full_text(doc, 282, 437)
    doc.close()

    monster_blocks = split_monsters(text)
    enemigos = []
    seen_names = set()

    for block in monster_blocks:
        stats = parse_monster_stat_block(block)
        if stats and stats["nombre"] and stats["nombre"] not in seen_names:
            # Basic validation
            if any(f in stats for f in ["clase_de_armadura", "puntos_de_golpe", "desafio"]):
                seen_names.add(stats["nombre"])
                enemigos.append(stats)

    print(f"  => {len(enemigos)} monstruos/PNJs extraídos")
    return enemigos


RARITY_RE = re.compile(
    r"^(Poción|Armadura|Anillo|Arma|Escudo|Varita|Bastón|Botas|Guantes|Capa|"
    r"Cinturón|Diadema|Yelmo|Collar|Bolsa|Polvo|Perla|Piedra|Frasco|Gema|"
    r"Objeto maravilloso|Objeto)\b.*,"
    r"\s*(común|infrecuente|raro|muy raro|legendario|variado|varia)"
)


def extract_magic_items():
    print("Extrayendo objetos magicos...")
    doc = fitz.open(str(PDF_PATH))
    text = extract_full_text(doc, 222, 271)
    doc.close()

    # Find start of actual items
    start_idx = text.find("Abanico del viento")
    if start_idx < 0:
        start_idx = text.find("Objetos magicos de la A a la Z")
    if start_idx > 0:
        text = text[start_idx:]
    else:
        for m in RARITY_RE.finditer(text):
            start_idx = m.start()
            break
        if start_idx:
            text = text[start_idx:]

    # Find end of magic items
    end_idx = text.find("Objetos magicos conscientes")
    if end_idx < 0:
        end_idx = text.find("Artefactos")
    if end_idx > 0:
        text = text[:end_idx]

    items = []
    lines = text.split("\n")
    i = 0
    current_name = None
    current_rarity = None
    current_desc = []

    def save_current():
        if not current_name:
            return
        text_desc = " ".join(current_desc).strip() if current_desc else ""
        if len(text_desc) > 20:
            items.append({
                "nombre": current_name,
                "rareza": (current_rarity or "").strip(),
                "descripcion": text_desc,
            })

    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line.startswith("Objetos magicos de la A a la Z"):
            continue

        # Detect item name (short line) followed by rarity line
        if len(line) < 60 and len(line) > 2:
            if i < len(lines):
                peek = lines[i].strip()
                if RARITY_RE.match(peek):
                    save_current()
                    current_name = line
                    current_rarity = peek
                    current_desc = []
                    i += 1
                    continue

        if current_name:
            current_desc.append(line)

    save_current()

    # ── Post-process: fix rareza/descripcion split across lines ──
    for item in items:
        changed = True
        while changed:
            changed = False
            r = item.get("rareza", "")
            d = item.get("descripcion", "")
            if not d:
                break
            if d[0].islower() or d[0] == "(":
                idx = d.find(") ")
                if idx >= 0:
                    item["rareza"] = (r + " " + d[:idx + 1]).strip()
                    item["descripcion"] = d[idx + 2:].strip()
                    changed = True
                else:
                    idx = d.find(")")
                    if idx >= 0:
                        item["rareza"] = (r + " " + d[:idx + 1]).strip()
                        item["descripcion"] = d[idx + 1:].strip()
                        changed = True
                    else:
                        item["rareza"] = (r + " " + d).strip()
                        item["descripcion"] = ""
                        changed = False
        # Fix missing opening paren before "requiere"
        r = item.get("rareza", "")
        if "requiere" in r and "(requiere" not in r:
            item["rareza"] = r.replace("requiere", "(requiere")

    # ── Remove entries with garbage names (name fragments) ──
    items = [it for it in items if len(it["nombre"]) > 3 and it["nombre"][0].isupper()]

    print(f"  => {len(items)} objetos mágicos extraídos")
    return items


def generate_equipment_data():
    """Escribe datos de armaduras, armas y equipo del SRD."""

    armaduras = [
        {"nombre": "Acolchada", "tipo": "ligera", "ca": "11 + Des", "fuerza_min": "", "sigilo": "desventaja", "peso": "4 kg", "precio": "5 po"},
        {"nombre": "Cuero", "tipo": "ligera", "ca": "11 + Des", "fuerza_min": "", "sigilo": "", "peso": "5 kg", "precio": "10 po"},
        {"nombre": "Cuero tachonado", "tipo": "ligera", "ca": "12 + Des", "fuerza_min": "", "sigilo": "", "peso": "6,5 kg", "precio": "45 po"},
        {"nombre": "Pieles", "tipo": "media", "ca": "12 + Des (máx 2)", "fuerza_min": "", "sigilo": "", "peso": "6 kg", "precio": "10 po"},
        {"nombre": "Camisote de mallas", "tipo": "media", "ca": "13 + Des (máx 2)", "fuerza_min": "", "sigilo": "", "peso": "10 kg", "precio": "50 po"},
        {"nombre": "Cota de escamas", "tipo": "media", "ca": "14 + Des (máx 2)", "fuerza_min": "", "sigilo": "desventaja", "peso": "22,5 kg", "precio": "50 po"},
        {"nombre": "Coraza", "tipo": "media", "ca": "15 + Des (máx 2)", "fuerza_min": "", "sigilo": "", "peso": "10 kg", "precio": "400 po"},
        {"nombre": "Media armadura", "tipo": "media", "ca": "15 + Des (máx 2)", "fuerza_min": "", "sigilo": "desventaja", "peso": "20 kg", "precio": "750 po"},
        {"nombre": "Anillas", "tipo": "pesada", "ca": "14", "fuerza_min": "", "sigilo": "desventaja", "peso": "20 kg", "precio": "30 po"},
        {"nombre": "Cota de malla", "tipo": "pesada", "ca": "16", "fuerza_min": "Fue 13", "sigilo": "desventaja", "peso": "27,5 kg", "precio": "75 po"},
        {"nombre": "Armadura de bandas", "tipo": "pesada", "ca": "17", "fuerza_min": "Fue 15", "sigilo": "desventaja", "peso": "17,5 kg", "precio": "200 po"},
        {"nombre": "Armadura de placas", "tipo": "pesada", "ca": "18", "fuerza_min": "Fue 15", "sigilo": "desventaja", "peso": "27,5 kg", "precio": "1500 po"},
        {"nombre": "Escudo", "tipo": "escudo", "ca": "+2", "fuerza_min": "", "sigilo": "", "peso": "3 kg", "precio": "10 po"},
    ]

    armas = [
        {"nombre": "Bastón", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d6 contundente", "peso": "2 kg", "precio": "2 pp", "propiedades": "Versátil (1d8)"},
        {"nombre": "Clava", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d4 contundente", "peso": "1 kg", "precio": "1 pp", "propiedades": "Ligera"},
        {"nombre": "Daga", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d4 perforante", "peso": "0,5 kg", "precio": "2 po", "propiedades": "Ligera, arrojadiza (alcance 6/18), sutil"},
        {"nombre": "Gran garrote", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d8 contundente", "peso": "5 kg", "precio": "2 pp", "propiedades": "A dos manos"},
        {"nombre": "Hacha de mano", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d6 cortante", "peso": "1 kg", "precio": "5 po", "propiedades": "Ligera, arrojadiza (alcance 6/18)"},
        {"nombre": "Jabalina", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d6 perforante", "peso": "1 kg", "precio": "5 pp", "propiedades": "Arrojadiza (alcance 9/36)"},
        {"nombre": "Lanza", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d6 perforante", "peso": "1,5 kg", "precio": "1 po", "propiedades": "Versátil (1d8), arrojadiza (alcance 6/18)"},
        {"nombre": "Maza", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d6 contundente", "peso": "2 kg", "precio": "5 po", "propiedades": ""},
        {"nombre": "Martillo ligero", "tipo": "simple", "categoria": "cuerpo a cuerpo", "daño": "1d4 contundente", "peso": "1 kg", "precio": "2 po", "propiedades": "Ligera, arrojadiza (alcance 6/18)"},
        {"nombre": "Cimitarra", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d6 cortante", "peso": "1,5 kg", "precio": "25 po", "propiedades": "Ligera, sutil"},
        {"nombre": "Espada larga", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d8 cortante", "peso": "1,5 kg", "precio": "15 po", "propiedades": "Versátil (1d10)"},
        {"nombre": "Espadón", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "2d6 cortante", "peso": "3 kg", "precio": "50 po", "propiedades": "A dos manos, pesada"},
        {"nombre": "Gran hacha", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d12 cortante", "peso": "3,5 kg", "precio": "30 po", "propiedades": "A dos manos, pesada"},
        {"nombre": "Hacha de batalla", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d8 cortante", "peso": "2 kg", "precio": "10 po", "propiedades": "Versátil (1d10)"},
        {"nombre": "Martillo de guerra", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d8 contundente", "peso": "1 kg", "precio": "15 po", "propiedades": "Versátil (1d10)"},
        {"nombre": "Mayal", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d8 contundente", "peso": "1 kg", "precio": "10 po", "propiedades": ""},
        {"nombre": "Pica", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d10 perforante", "peso": "9 kg", "precio": "5 po", "propiedades": "A dos manos, pesada, alcanzable"},
        {"nombre": "Alabarda", "tipo": "marcial", "categoria": "cuerpo a cuerpo", "daño": "1d10 cortante", "peso": "3 kg", "precio": "20 po", "propiedades": "A dos manos, pesada, alcanzable"},
        {"nombre": "Arco corto", "tipo": "simple", "categoria": "a distancia", "daño": "1d6 perforante", "peso": "1 kg", "precio": "25 po", "propiedades": "A dos manos, munición (alcance 24/96)"},
        {"nombre": "Arco largo", "tipo": "marcial", "categoria": "a distancia", "daño": "1d8 perforante", "peso": "1 kg", "precio": "50 po", "propiedades": "A dos manos, munición (alcance 45/180), pesada"},
        {"nombre": "Ballesta ligera", "tipo": "simple", "categoria": "a distancia", "daño": "1d8 perforante", "peso": "2,5 kg", "precio": "25 po", "propiedades": "A dos manos, munición (alcance 24/96), recarga"},
        {"nombre": "Ballesta de mano", "tipo": "marcial", "categoria": "a distancia", "daño": "1d6 perforante", "peso": "1,5 kg", "precio": "75 po", "propiedades": "Ligera, munición (alcance 9/36), recarga"},
        {"nombre": "Ballesta pesada", "tipo": "marcial", "categoria": "a distancia", "daño": "1d10 perforante", "peso": "9 kg", "precio": "50 po", "propiedades": "A dos manos, munición (alcance 30/120), pesada, recarga"},
        {"nombre": "Honda", "tipo": "simple", "categoria": "a distancia", "daño": "1d4 contundente", "peso": "—", "precio": "1 pp", "propiedades": "Munición (alcance 9/36)"},
    ]

    equipo_aventurero = [
        {"nombre": "Antorcha", "precio": "1 pc", "peso": "0,5 kg"},
        {"nombre": "Bolsa", "precio": "5 pp", "peso": "0,5 kg"},
        {"nombre": "Cama portátil", "precio": "1 po", "peso": "3,5 kg"},
        {"nombre": "Cantimplora", "precio": "2 pp", "peso": "2,5 kg (llena)"},
        {"nombre": "Cesta", "precio": "4 pp", "peso": "1 kg"},
        {"nombre": "Cuerda de cáñamo (15 m)", "precio": "1 po", "peso": "5 kg"},
        {"nombre": "Cuerda de seda (15 m)", "precio": "10 po", "peso": "2,5 kg"},
        {"nombre": "Equipo de acampada", "precio": "2 po", "peso": "10 kg"},
        {"nombre": "Espejo de acero", "precio": "5 po", "peso": "0,25 kg"},
        {"nombre": "Linterna", "precio": "10 po", "peso": "0,5 kg"},
        {"nombre": "Mochila", "precio": "2 po", "peso": "2,5 kg"},
        {"nombre": "Martillo de herrero", "precio": "2 po", "peso": "1,5 kg"},
        {"nombre": "Piedra de afilar", "precio": "1 pp", "peso": "0,5 kg"},
        {"nombre": "Pico de minero", "precio": "2 po", "peso": "5 kg"},
        {"nombre": "Raciones (1 día)", "precio": "5 pp", "peso": "1 kg"},
        {"nombre": "Saco", "precio": "1 pp", "peso": "0,25 kg"},
        {"nombre": "Yesca y pedernal", "precio": "5 pp", "peso": "0,5 kg"},
        {"nombre": "Vela", "precio": "1 pc", "peso": "—"},
        {"nombre": "Martillo", "precio": "1 po", "peso": "1,5 kg"},
        {"nombre": "Palanqueta", "precio": "2 po", "peso": "2,5 kg"},
    ]

    herramientas = [
        {"nombre": "Herramientas de artesano", "precio": "5 po", "peso": "2,5 kg"},
        {"nombre": "Herramientas de ladrón", "precio": "25 po", "peso": "0,5 kg"},
        {"nombre": "Instrumento musical", "precio": "5 po", "peso": "1 kg"},
        {"nombre": "Kit de disfraces", "precio": "25 po", "peso": "1,5 kg"},
        {"nombre": "Kit de envenenador", "precio": "50 po", "peso": "1 kg"},
        {"nombre": "Kit de herboristería", "precio": "5 po", "peso": "1,5 kg"},
        {"nombre": "Kit de pócimas de curación", "precio": "50 po", "peso": "1,5 kg"},
        {"nombre": "Navaja de yesca", "precio": "5 pp", "peso": "0,5 kg"},
    ]

    return {"armaduras": armaduras, "armas": armas, "equipo": equipo_aventurero, "herramientas": herramientas}


def extract_deidades():
    print("Extrayendo panteones y deidades...")
    doc = fitz.open(str(PDF_PATH))
    text = extract_full_text(doc, 390, 393)
    doc.close()

    deidades = []
    current_panteon = None
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    i = 0

    while i < len(lines):
        line = lines[i]

        if "Apéndice MJ" in line or line.startswith("Apéndice"):
            i += 1
            continue

        # Detect pantheon name
        m = re.search(r"(?:El\s+)?pante[oó]n\s+(\w+)", line, re.IGNORECASE)
        if m:
            current_panteon = m.group(1)
            i += 1
            continue
        m2 = re.match(r"Deidades\s+(\w+)", line, re.IGNORECASE)
        if m2:
            current_panteon = m2.group(1)
            i += 1
            continue

        # Skip table headers
        if line in ("Deidad", "Alineamiento", "Dominios recomendados", "Símbolo"):
            i += 1
            continue

        # Deity names contain "dios/diosa/señor" and are followed by an alignment code
        if ("dios" in line.lower() or "señor" in line.lower()):
            # Skip descriptive text (not an actual deity name)
            if line.lower().startswith(("estos", "allí", "all", "cuando")):
                i += 1
                continue
            nombre = line
            # Next non-empty line must be an alignment code (1-3 uppercase)
            j = i + 1
            while j < len(lines) and not lines[j]:
                j += 1
            if j < len(lines) and re.match(r"^[A-ZÁÉÍÓÚÑ]{1,3}$", lines[j]):
                alineamiento = lines[j]
                # Next non-empty after that is domain
                k = j + 1
                while k < len(lines) and not lines[k]:
                    k += 1
                dominio = lines[k] if k < len(lines) else ""
                # Next non-empty after that is symbol (skip)
                deidades.append({
                    "panteon": current_panteon or "desconocido",
                    "nombre": nombre,
                    "dominio": dominio,
                    "alineamiento": alineamiento,
                })
                i = k + 1
                continue

        i += 1

    print(f"  => {len(deidades)} deidades extraídas")
    return deidades


def add_draconido():
    path = DATA_DIR / "clases_razas.json"
    if not path.exists():
        print("  clases_razas.json no encontrado")
        return
    data = json.loads(path.read_text(encoding="utf-8"))

    # Check if Dracónido exists
    exists = any(r["nombre"] == "Dracónido" for r in data)
    if not exists:
        data.append({
            "nombre": "Dracónido",
            "tipo": "raza",
            "descripcion": "+2 Fuerza, +1 Carisma. De 16 años, tamaño Mediano, velocidad 9 m. "
                          "Ascendencia dracónica (tipo de daño según el ancestro: ácido, eléctrico, fuego, frío o veneno). "
                          "Arma de aliento (acción, CD 8 + bonif. competencia + mod. Con, daño 2d6 a 1d10 según nivel). "
                          "Resistencia al daño de tu ascendencia.",
            "dado_golpe": "",
            "habilidad_principal": "",
        })
        print("  => Dracónido añadido a clases_razas.json")

    # Fix Explorador
    for r in data:
        if r["nombre"] == "Explorador" and r.get("tipo") == "clase":
            if not r.get("habilidad_principal"):
                r["habilidad_principal"] = "Destreza, Sabiduría"
                print("  => Explorador: habilidad_principal corregida")
            break

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  => clases_razas.json: {len(data)} entradas")


def clean_reglas_duplicates():
    path = DATA_DIR / "reglas_basicas.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))

    seen = set()
    cleaned = []
    for item in data:
        content = item.get("contenido", "")
        # Deduplicate by first 100 chars
        key = content[:100]
        if key not in seen:
            seen.add(key)
            cleaned.append(item)
        else:
            pass

    path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  => reglas_basicas.json: {len(data)} => {len(cleaned)} (duplicados eliminados)")


def save_json(filename, data):
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  OK {filename} guardado ({len(data)} entradas)")


def main():
    if not PDF_PATH.exists():
        print(f"PDF no encontrado: {PDF_PATH}")
        return

    print(f"Leyendo PDF: {PDF_PATH}")
    print()

    # 1. Enemigos (monstruos + PNJs)
    enemigos = extract_enemigos()
    save_json("enemigos.json", enemigos)

    # 2. Objetos mágicos
    items = extract_magic_items()
    equip_data = generate_equipment_data()
    equip_data["objetos_magicos"] = items
    save_json("objetos_equipo.json", equip_data)

    # 3. Deidades
    deidades = extract_deidades()
    trasfondo_path = DATA_DIR / "trasfondo_y_escenarios.json"

    DEFAULT_BACKGROUNDS = [
        {"categoria": "trasfondo_y_escenarios", "contenido": "Si un personaje fuera a recibir la misma competencia de dos fuentes distintas, en lugar de eso podra elegir una competencia diferente del mismo tipo (habilidades o herramientas). Idiomas: algunos trasfondos permiten a los personajes aprender idiomas adicionales. Equipo: cada trasfondo proporciona un paquete de equipo inicial. Caracteristicas recomendadas: se pueden escoger de la lista, tirar dados, o usar como inspiracion."},
        {"categoria": "trasfondo_y_escenarios", "contenido": "Acolito. Rasgo: Refugio del Fiel. Puedes hospedarte a ti y a tus companeros en templos de tu fe. Personalidad (d8): Idolatro a cierto heroe de mi fe, Soy capaz de lograr concordia, Veo presagios, Nada apaga mi optimismo, Cito textos sagrados, Soy tolerante/intolerante, He disfrutado los lujos, Poca experiencia practica. Ideal (d6): Tradicion (legal), Caridad (bueno), Cambio (caotico), Poder (legal), Fe (bueno). Vinculo (d6): Sufri una injusticia, Busco una reliquia, Debo proteger a mi congregacion, Luchare por mi fe, Morire por mi dios. Defecto (d6): Juzgo a otros, Soy dogmatico, Soy quisquilloso, Desconfio de extranjeros, Soy tajante."},
    ]

    if trasfondo_path.exists():
        trasfondo = json.loads(trasfondo_path.read_text(encoding="utf-8"))
    else:
        trasfondo = list(DEFAULT_BACKGROUNDS)
    # Ensure default backgrounds exist
    existing_content = {t.get("contenido", "")[:60] for t in trasfondo if isinstance(t, dict)}
    for bg in DEFAULT_BACKGROUNDS:
        if bg["contenido"][:60] not in existing_content:
            trasfondo.append(bg)
    trasfondo = [t for t in trasfondo if not (isinstance(t, dict) and t.get("tipo") == "deidades")]
    if deidades:
        trasfondo.append({"tipo": "deidades", "titulo": "Panteones y deidades", "lista": deidades})
    save_json("trasfondo_y_escenarios.json", trasfondo)

    # 4. Clases y razas
    add_draconido()

    # 5. Limpiar duplicados
    clean_reglas_duplicates()

    print()
    print("¡Extracción completada!")


if __name__ == "__main__":
    main()
