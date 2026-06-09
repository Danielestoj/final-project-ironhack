import { useState, useEffect, useCallback } from "react";
import client from "../api/client";
import { SearchSelect } from "../components/SearchSelect";

const RAZAS = ["Humano", "Elfo", "Enano", "Mediano", "Semielfo", "Semiorco", "Gnomo", "Tiefling", "Dracónido"];
const CLASES = ["Guerrero", "Mago", "Pícaro", "Clérigo", "Bárbaro", "Explorador", "Paladín", "Druida", "Brujo", "Hechicero", "Monje"];
const ALINEAMIENTOS = ["Legal bueno", "Neutral bueno", "Caótico bueno", "Legal neutral", "Neutral", "Caótico neutral", "Legal malvado", "Neutral malvado", "Caótico malvado"];
const HABILIDADES = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"];
const CARACS = ["Inteligencia", "Sabiduría", "Carisma"];

const SKILLS = [
  { key: "acrobacias", label: "Acrobacias", stat: "destreza" },
  { key: "arcanos", label: "Arcanos", stat: "inteligencia" },
  { key: "atletismo", label: "Atletismo", stat: "fuerza" },
  { key: "engaño", label: "Engaño", stat: "carisma" },
  { key: "historia", label: "Historia", stat: "inteligencia" },
  { key: "interpretacion", label: "Interpretación", stat: "carisma" },
  { key: "intimidacion", label: "Intimidación", stat: "carisma" },
  { key: "investigacion", label: "Investigación", stat: "inteligencia" },
  { key: "juego_manos", label: "Juego de Manos", stat: "destreza" },
  { key: "medicina", label: "Medicina", stat: "sabiduria" },
  { key: "naturaleza", label: "Naturaleza", stat: "inteligencia" },
  { key: "percepcion", label: "Percepción", stat: "sabiduria" },
  { key: "perspicacia", label: "Perspicacia", stat: "sabiduria" },
  { key: "persuasion", label: "Persuasión", stat: "carisma" },
  { key: "religion", label: "Religión", stat: "inteligencia" },
  { key: "sigilo", label: "Sigilo", stat: "destreza" },
  { key: "supervivencia", label: "Supervivencia", stat: "sabiduria" },
  { key: "trato_animales", label: "Trato con Animales", stat: "sabiduria" },
];

const SAVES = [
  { key: "fuerza", label: "Fuerza", stat: "fuerza" },
  { key: "destreza", label: "Destreza", stat: "destreza" },
  { key: "constitucion", label: "Constitución", stat: "constitucion" },
  { key: "inteligencia", label: "Inteligencia", stat: "inteligencia" },
  { key: "sabiduria", label: "Sabiduría", stat: "sabiduria" },
  { key: "carisma", label: "Carisma", stat: "carisma" },
];

const calcMod = (score) => Math.floor((Number(score) - 10) / 2);
const calcSkill = (prof, mod, bonus) => mod + (prof === 1 ? bonus : prof === 2 ? bonus * 2 : 0);

const initialForm = { nombre: "", raza: "Humano", clase: "Guerrero", nivel: 1, fuerza: 10, destreza: 10, constitucion: 10, inteligencia: 10, sabiduria: 10, carisma: 10, pg_max: 10, pg_actual: 10 };

function emptyPj() {
  return {
    nombre: "", nombre_jugador: "", raza: "", clase: "", nivel: 1, trasfondo: "", experiencia: 0, alineamiento: "",
    fuerza: 10, destreza: 10, constitucion: 10, inteligencia: 10, sabiduria: 10, carisma: 10,
    clase_armadura: 10, iniciativa: 0, velocidad: 9, pg_max: 10, pg_actual: 10, pg_temporales: 0,
    dados_golpe: "1d10", muerte_exitos: 0, muerte_fallos: 0, inspiracion: false, bonif_competencia: 2,
    fuerza_salv_prof: false, destreza_salv_prof: false, constitucion_salv_prof: false,
    inteligencia_salv_prof: false, sabiduria_salv_prof: false, carisma_salv_prof: false,
    acrobacias_prof: 0, arcanos_prof: 0, atletismo_prof: 0, engaño_prof: 0, historia_prof: 0,
    interpretacion_prof: 0, intimidacion_prof: 0, investigacion_prof: 0, juego_manos_prof: 0,
    medicina_prof: 0, naturaleza_prof: 0, percepcion_prof: 0, perspicacia_prof: 0, persuasion_prof: 0,
    religion_prof: 0, sigilo_prof: 0, supervivencia_prof: 0, trato_animales_prof: 0,
    competencias_idiomas: "", rasgos_atributos: "", rasgos_personalidad: "", ideales: "", vinculos: "", defectos: "",
    edad: "", altura: "", peso: "", ojos: "", piel: "", cabello: "",
    apariencia: "", historia: "", aliados_organizaciones: "", tesoro: "", rasgos_adicionales: "",
    pc: 0, pe: 0, ppt: 0, po: 0, pp: 0,
    clase_lanzadora: "", carac_lanzamiento: "", salvacion_conjuro: 0, bonif_ataque_conjuro: 0,
    espacios_conjuros: "{}",
    hechizos: [], objetos: [], ataques: [],
  };
}

function parseSlots(str) {
  try { return JSON.parse(str || "{}"); } catch { return {}; }
}

export function PersonajesPage() {
  const [personajes, setPersonajes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [selectedPj, setSelectedPj] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editPj, setEditPj] = useState(null);
  const [savingModal, setSavingModal] = useState(false);

  const fetchPersonajes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await client.get("/personajes/");
      setPersonajes(res.data);
    } catch { setError("Error al cargar personajes"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchPersonajes(); }, [fetchPersonajes]);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...form, nivel: Number(form.nivel), pg_max: Number(form.pg_max), pg_actual: Number(form.pg_actual), fuerza: Number(form.fuerza), destreza: Number(form.destreza), constitucion: Number(form.constitucion), inteligencia: Number(form.inteligencia), sabiduria: Number(form.sabiduria), carisma: Number(form.carisma) };
      await client.post("/personajes/", payload);
      setShowForm(false);
      setForm(initialForm);
      fetchPersonajes();
    } catch { setError("Error al crear personaje"); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm("¿Eliminar personaje?")) return;
    try {
      await client.delete(`/personajes/${id}`);
      fetchPersonajes();
    } catch { setError("Error al eliminar"); }
  };

  const openModal = async (pj) => {
    try {
      const res = await client.get(`/personajes/${pj.id}`);
      setSelectedPj(res.data);
      setEditPj(JSON.parse(JSON.stringify(res.data)));
      setEditing(false);
    } catch { setError("Error al cargar personaje"); }
  };

  const closeModal = () => {
    if (editing && !confirm("Hay cambios sin guardar. ¿Cerrar?")) return;
    setSelectedPj(null);
    setEditPj(null);
    setEditing(false);
  };

  const toggleEdit = () => {
    if (editing) {
      setEditPj(JSON.parse(JSON.stringify(selectedPj)));
      setEditing(false);
    } else {
      setEditing(true);
    }
  };

  const handleEditChange = (field, value) => setEditPj({ ...editPj, [field]: value });

  const handleSave = async () => {
    setSavingModal(true);
    try {
      const res = await client.put(`/personajes/${selectedPj.id}`, editPj);
      setSelectedPj(res.data);
      setEditPj(JSON.parse(JSON.stringify(res.data)));
      setEditing(false);
      fetchPersonajes();
    } catch { setError("Error al guardar"); }
    finally { setSavingModal(false); }
  };

  useEffect(() => {
    if (!selectedPj) return;
    const handleKey = (e) => { if (e.key === "Escape") closeModal(); };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selectedPj, editing]);

  const renderField = (label, fieldKey, type = "text", opts = {}) => {
    const val = editPj ? editPj[fieldKey] : "";
    if (!editing) {
      const display = val || (type === "number" ? "0" : "-");
      return <div className="pj-field"><span className="pj-label">{label}</span><span className="pj-value">{display}</span></div>;
    }
    if (type === "select") {
      return <div className="pj-field"><span className="pj-label">{label}</span><select value={val} onChange={(e) => handleEditChange(fieldKey, e.target.value)} className="pj-input">{opts.options.map((o) => <option key={o} value={o}>{o}</option>)}</select></div>;
    }
    if (type === "number") {
      return <div className="pj-field"><span className="pj-label">{label}</span><input type="number" value={val} onChange={(e) => handleEditChange(fieldKey, Number(e.target.value))} className="pj-input" /></div>;
    }
    if (type === "textarea") {
      return <div className="pj-field pj-field-full"><span className="pj-label">{label}</span><textarea value={val} onChange={(e) => handleEditChange(fieldKey, e.target.value)} className="pj-textarea" rows={opts.rows || 3} /></div>;
    }
    return <div className="pj-field"><span className="pj-label">{label}</span><input type="text" value={val} onChange={(e) => handleEditChange(fieldKey, e.target.value)} className="pj-input" /></div>;
  };

  const statMod = (pj, stat) => calcMod(pj ? pj[stat] : 10);

  if (!selectedPj) {
    return (
      <div className="page-personajes">
        <div className="page-header">
          <h2>Mis Personajes</h2>
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancelar" : "+ Nuevo personaje"}
          </button>
        </div>
        {error && <p className="form-error">{error}</p>}
        {showForm && (
          <form className="personaje-form" onSubmit={handleSubmit}>
            <div className="form-row">
              <input name="nombre" value={form.nombre} onChange={handleChange} placeholder="Nombre" required />
              <select name="raza" value={form.raza} onChange={handleChange}>{RAZAS.map((r) => <option key={r}>{r}</option>)}</select>
              <select name="clase" value={form.clase} onChange={handleChange}>{CLASES.map((c) => <option key={c}>{c}</option>)}</select>
              <input name="nivel" type="number" min="1" max="20" value={form.nivel} onChange={handleChange} placeholder="Nivel" />
            </div>
            <div className="form-row stats">
              {["fuerza", "destreza", "constitucion", "inteligencia", "sabiduria", "carisma"].map((stat) => (
                <div key={stat} className="stat-field">
                  <label>{stat.charAt(0).toUpperCase() + stat.slice(1)}</label>
                  <input name={stat} type="number" min="1" max="20" value={form[stat]} onChange={handleChange} />
                </div>
              ))}
            </div>
            <button type="submit" disabled={saving}>{saving ? "Guardando..." : "Crear personaje"}</button>
          </form>
        )}
        {loading && <p className="loading">Cargando...</p>}
        {!loading && personajes.length === 0 && !showForm && <p className="empty">No tienes personajes. ¡Crea uno!</p>}
        <div className="personaje-grid">
          {personajes.map((pj) => (
            <div key={pj.id} className="personaje-card" onClick={() => openModal(pj)}>
              <h3>{pj.nombre}</h3>
              <p>{pj.raza} · {pj.clase} · Nivel {pj.nivel}</p>
              <p>PG: {pj.pg_actual || pj.pg_max || pj.puntos_golpe || "-"}/{pj.pg_max || pj.puntos_golpe || "-"}</p>
              <div className="personaje-stats">
                <span>FUE {pj.fuerza}</span><span>DES {pj.destreza}</span><span>CON {pj.constitucion}</span>
                <span>INT {pj.inteligencia}</span><span>SAB {pj.sabiduria}</span><span>CAR {pj.carisma}</span>
              </div>
              <button className="btn-delete" onClick={(e) => { e.stopPropagation(); handleDelete(pj.id); }}>Eliminar</button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const p = editing ? editPj : selectedPj;
  const prof = p.bonif_competencia || 2;
  const slots = parseSlots(p.espacios_conjuros);

  return (
    <div className="pj-modal-backdrop" onClick={closeModal}>
      <div className="pj-modal" onClick={(e) => e.stopPropagation()}>
        <div className="pj-modal-header">
          <h2>{p.nombre || "Personaje"}</h2>
          <div className="pj-header-buttons">
            <button className="pj-btn pj-btn-edit" onClick={toggleEdit}>{editing ? "Cancelar" : "Editar"}</button>
            <button className="pj-btn pj-btn-close" onClick={closeModal}>&times;</button>
          </div>
        </div>

        <div className="pj-modal-body">
          {/* ── Section 1: Básicos ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Información Básica</h3>
            <div className="pj-grid pj-grid-4">
              {renderField("Nombre", "nombre")}
              {renderField("Jugador", "nombre_jugador")}
              {renderField("Raza", "raza", "select", { options: RAZAS })}
              {renderField("Clase", "clase", "select", { options: CLASES })}
              {renderField("Nivel", "nivel", "number")}
              {renderField("Trasfondo", "trasfondo")}
              {renderField("Experiencia", "experiencia", "number")}
              {renderField("Alineamiento", "alineamiento", "select", { options: ALINEAMIENTOS })}
            </div>
            <div className="pj-inline">
              <label className="pj-check-field">
                <input type="checkbox" checked={p.inspiracion} disabled={!editing}
                  onChange={(e) => handleEditChange("inspiracion", e.target.checked)} />
                Inspiración
              </label>
              {renderField("Bonif. Competencia", "bonif_competencia", "number")}
            </div>
          </section>

          {/* ── Section 2: Stats ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Características</h3>
            <div className="pj-stats-row">
              {["fuerza", "destreza", "constitucion", "inteligencia", "sabiduria", "carisma"].map((s) => {
                const val = p[s] || 10;
                const mod = calcMod(val);
                return (
                  <div key={s} className="pj-stat-block">
                    <span className="pj-stat-name">{s.charAt(0).toUpperCase() + s.slice(1)}</span>
                    {editing ? (
                      <input type="number" min="1" max="30" value={val}
                        onChange={(e) => handleEditChange(s, Number(e.target.value))} className="pj-stat-input" />
                    ) : (
                      <span className="pj-stat-val">{val}</span>
                    )}
                    <span className="pj-stat-mod">{mod >= 0 ? "+" : ""}{mod}</span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ── Section 3: Combate ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Combate</h3>
            <div className="pj-grid pj-grid-4">
              {renderField("CA", "clase_armadura", "number")}
              {renderField("Iniciativa", "iniciativa", "number")}
              {renderField("Velocidad (m)", "velocidad", "number")}
              {renderField("PG Máximos", "pg_max", "number")}
              {renderField("PG Actuales", "pg_actual", "number")}
              {renderField("PG Temporales", "pg_temporales", "number")}
              {renderField("Dados de Golpe", "dados_golpe")}
            </div>
            <div className="pj-death-saves">
              <span className="pj-label">Salvaciones de Muerte:</span>
              <span className="pj-death-group">Éxitos: {"⚪".repeat(3).split("").map((d, i) => (
                <button key={i} type="button" className={`pj-death-dot ${i < (p.muerte_exitos || 0) ? "active" : ""}`}
                  disabled={!editing} onClick={() => handleEditChange("muerte_exitos", i < (p.muerte_exitos || 0) ? i : i + 1)}>⬤</button>
              ))}</span>
              <span className="pj-death-group">Fallos: {"⚪".repeat(3).split("").map((d, i) => (
                <button key={i} type="button" className={`pj-death-dot ${i < (p.muerte_fallos || 0) ? "active fail" : ""}`}
                  disabled={!editing} onClick={() => handleEditChange("muerte_fallos", i < (p.muerte_fallos || 0) ? i : i + 1)}>⬤</button>
              ))}</span>
            </div>
          </section>

          {/* ── Section 4: Salvaciones ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Tiradas de Salvación</h3>
            <div className="pj-saves-grid">
              {SAVES.map((sv) => {
                const profKey = sv.key + "_salv_prof";
                const isProf = p[profKey] || false;
                const mod = statMod(p, sv.stat) + (isProf ? prof : 0);
                return (
                  <div key={sv.key} className="pj-save-row">
                    {editing ? (
                      <input type="checkbox" checked={isProf} onChange={(e) => handleEditChange(profKey, e.target.checked)} />
                    ) : (
                      <span className={`pj-prof-dot ${isProf ? "active" : ""}`}>⬤</span>
                    )}
                    <span className="pj-save-label">{sv.label}</span>
                    <span className="pj-save-mod">{mod >= 0 ? "+" : ""}{mod}</span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ── Section 5: Habilidades ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Habilidades</h3>
            <div className="pj-skills-grid">
              {SKILLS.map((sk) => {
                const profKey = sk.key + "_prof";
                const profLevel = p[profKey] || 0;
                const mod = statMod(p, sk.stat);
                const total = calcSkill(profLevel, mod, prof);
                return (
                  <div key={sk.key} className="pj-skill-row">
                    {editing ? (
                      <select value={profLevel} onChange={(e) => handleEditChange(profKey, Number(e.target.value))} className="pj-prof-select">
                        <option value={0}>○</option><option value={1}>◐</option><option value={2}>⬤</option>
                      </select>
                    ) : (
                      <span className={`pj-prof-dot ${profLevel >= 1 ? "active" : ""} ${profLevel >= 2 ? "expert" : ""}`}>
                        {profLevel === 0 ? "○" : profLevel === 1 ? "◐" : "⬤"}
                      </span>
                    )}
                    <span className="pj-skill-label">{sk.label}</span>
                    <span className="pj-skill-stat">({sk.stat.slice(0, 3).toUpperCase()})</span>
                    <span className="pj-skill-mod">{total >= 0 ? "+" : ""}{total}</span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* ── Section 6: Ataques ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Ataques y Conjuros</h3>
            <table className="pj-attacks-table">
              <thead><tr><th>Nombre</th><th>Bonif. Ataque</th><th>Daño</th><th>Tipo</th>{editing && <th></th>}</tr></thead>
              <tbody>
                {(p.ataques || []).map((at, i) => (
                  <tr key={i}>
                    {editing ? (
                      <>
                        <td><input value={at.nombre} onChange={(e) => { const a = [...p.ataques]; a[i] = { ...a[i], nombre: e.target.value }; handleEditChange("ataques", a); }} className="pj-input-sm" /></td>
                        <td><input value={at.bonif_ataque} onChange={(e) => { const a = [...p.ataques]; a[i] = { ...a[i], bonif_ataque: e.target.value }; handleEditChange("ataques", a); }} className="pj-input-sm" /></td>
                        <td><input value={at.danio} onChange={(e) => { const a = [...p.ataques]; a[i] = { ...a[i], danio: e.target.value }; handleEditChange("ataques", a); }} className="pj-input-sm" /></td>
                        <td><input value={at.tipo} onChange={(e) => { const a = [...p.ataques]; a[i] = { ...a[i], tipo: e.target.value }; handleEditChange("ataques", a); }} className="pj-input-sm" /></td>
                        <td><button type="button" className="pj-btn-sm pj-btn-danger" onClick={() => handleEditChange("ataques", p.ataques.filter((_, j) => j !== i))}>&times;</button></td>
                      </>
                    ) : (
                      <>
                        <td>{at.nombre}</td><td>{at.bonif_ataque}</td><td>{at.danio}</td><td>{at.tipo}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
            {editing && (
              <button type="button" className="pj-btn pj-btn-add" onClick={() => handleEditChange("ataques", [...(p.ataques || []), { nombre: "", bonif_ataque: "", danio: "", tipo: "" }])}>+ Añadir ataque</button>
            )}
          </section>

          {/* ── Section 7: Equipo y Monedas ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Equipo</h3>
            {editing ? (
              <SearchSelect
                endpoint="/objetos/" selected={p.objetos || []}
                onChange={(v) => handleEditChange("objetos", v.map((x) => ({ nombre_objeto: x.nombre, cantidad: 1 })))}
                placeholder="Buscar objeto..."
                labelKey="nombre"
                matchKey="nombre_objeto"
              />
            ) : (
              <div className="pj-tags">
                {(p.objetos || []).map((o, i) => <span key={i} className="ss-tag">{o.nombre_objeto}</span>)}
                {(p.objetos || []).length === 0 && <span className="pj-empty">-</span>}
              </div>
            )}
            <div className="pj-money">
              {[["pc", "PC"], ["pe", "PE"], ["ppt", "PPT"], ["po", "PO"], ["pp", "PP"]].map(([k, label]) => (
                <div key={k} className="pj-money-field">
                  <span className="pj-label">{label}</span>
                  {editing ? (
                    <input type="number" min="0" value={p[k] || 0} onChange={(e) => handleEditChange(k, Number(e.target.value))} className="pj-input-sm" />
                  ) : (
                    <span className="pj-value">{p[k] || 0}</span>
                  )}
                </div>
              ))}
            </div>
            <div className="pj-field pj-field-full">
              <span className="pj-label">Competencias e Idiomas</span>
              {editing ? (
                <textarea value={p.competencias_idiomas || ""} onChange={(e) => handleEditChange("competencias_idiomas", e.target.value)} className="pj-textarea" rows={2} />
              ) : (
                <p className="pj-value">{p.competencias_idiomas || "-"}</p>
              )}
            </div>
          </section>

          {/* ── Section 8: Conjuros ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Conjuros</h3>
            <div className="pj-grid pj-grid-4">
              {renderField("Clase Lanzadora", "clase_lanzadora")}
              {renderField("Caract. Lanzamiento", "carac_lanzamiento", "select", { options: CARACS })}
              {renderField("Salvación Conjuro", "salvacion_conjuro", "number")}
              {renderField("Bonif. Ataque", "bonif_ataque_conjuro", "number")}
            </div>
            <div className="pj-spell-section">
              <h4>Trucos</h4>
              {editing ? (
                <SearchSelect
                  endpoint="/hechizos/" selected={(p.hechizos || []).filter((h) => h.es_truco)}
                  onChange={(v) => {
                    const otros = (p.hechizos || []).filter((h) => !h.es_truco);
                    handleEditChange("hechizos", [...otros, ...v.map((x) => ({ nombre_hechizo: x.nombre, es_truco: true, nivel: 0, preparado: false }))]);
                  }}
                  placeholder="Buscar truco..."
                  labelKey="nombre"
                  matchKey="nombre_hechizo"
                />
              ) : (
                <div className="pj-tags">
                  {(p.hechizos || []).filter((h) => h.es_truco).map((h, i) => <span key={i} className="ss-tag">{h.nombre_hechizo}</span>)}
                  {(p.hechizos || []).filter((h) => h.es_truco).length === 0 && <span className="pj-empty">-</span>}
                </div>
              )}
            </div>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((lv) => {
              const lvlSpells = (p.hechizos || []).filter((h) => !h.es_truco && h.nivel === lv);
              const slotData = slots[String(lv)] || { total: 0, gastados: 0 };
              if (!editing && lvlSpells.length === 0 && slotData.total === 0) return null;
              return (
                <div key={lv} className="pj-spell-section">
                  <h4>Nivel {lv}</h4>
                  <div className="pj-spell-slots">
                    <span>Espacios: {slotData.gastados || 0}/{slotData.total || 0}</span>
                    {editing && (
                      <span className="pj-spell-slots-edit">
                        <input type="number" min="0" max="9" value={slotData.total || 0} className="pj-input-xs"
                          onChange={(e) => {
                            const newSlots = { ...slots, [lv]: { ...slotData, total: Number(e.target.value) } };
                            handleEditChange("espacios_conjuros", JSON.stringify(newSlots));
                          }} /> totales
                        <input type="number" min="0" max="9" value={slotData.gastados || 0} className="pj-input-xs"
                          onChange={(e) => {
                            const newSlots = { ...slots, [lv]: { ...slotData, gastados: Number(e.target.value) } };
                            handleEditChange("espacios_conjuros", JSON.stringify(newSlots));
                          }} /> gastados
                      </span>
                    )}
                  </div>
                  {editing ? (
                    <SearchSelect
                      endpoint="/hechizos/" selected={lvlSpells}
                      onChange={(v) => {
                        const otros = (p.hechizos || []).filter((h) => h.es_truco || h.nivel !== lv);
                        handleEditChange("hechizos", [...otros, ...v.map((x) => ({ nombre_hechizo: x.nombre, es_truco: false, nivel: lv, preparado: true }))]);
                      }}
                      placeholder={`Buscar conjuro nivel ${lv}...`}
                      labelKey="nombre"
                      matchKey="nombre_hechizo"
                    />
                  ) : (
                    <div className="pj-tags">
                      {lvlSpells.map((h, i) => <span key={i} className="ss-tag">{h.nombre_hechizo}</span>)}
                    </div>
                  )}
                </div>
              );
            })}
          </section>

          {/* ── Section 9: Rasgos y Personalidad ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Rasgos y Personalidad</h3>
            {renderField("Rasgos y Atributos", "rasgos_atributos", "textarea", { rows: 3 })}
            {renderField("Rasgos de Personalidad", "rasgos_personalidad", "textarea", { rows: 2 })}
            {renderField("Ideales", "ideales", "textarea", { rows: 2 })}
            {renderField("Vínculos", "vinculos", "textarea", { rows: 2 })}
            {renderField("Defectos", "defectos", "textarea", { rows: 2 })}
          </section>

          {/* ── Section 10: Apariencia e Historia ── */}
          <section className="pj-section">
            <h3 className="pj-section-title">Apariencia e Historia</h3>
            <div className="pj-grid pj-grid-4">
              {renderField("Edad", "edad")}
              {renderField("Altura", "altura")}
              {renderField("Peso", "peso")}
              {renderField("Ojos", "ojos")}
              {renderField("Piel", "piel")}
              {renderField("Cabello", "cabello")}
            </div>
            {renderField("Apariencia", "apariencia", "textarea", { rows: 3 })}
            {renderField("Historia", "historia", "textarea", { rows: 4 })}
            {renderField("Aliados y Organizaciones", "aliados_organizaciones", "textarea", { rows: 2 })}
            {renderField("Tesoro", "tesoro", "textarea", { rows: 2 })}
            {renderField("Rasgos Adicionales", "rasgos_adicionales", "textarea", { rows: 2 })}
          </section>
        </div>

        {editing && (
          <div className="pj-modal-footer">
            <button className="btn-primary" onClick={handleSave} disabled={savingModal}>
              {savingModal ? "Guardando..." : "💾 Guardar Cambios"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
