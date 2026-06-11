import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
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
  const { slug } = useParams();
  const navigate = useNavigate();
  const [personajes, setPersonajes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);

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

  const generarAleatorio = async () => {
    setLoading(true);
    try {
      await client.post("/personajes/random");
      fetchPersonajes();
    } catch { setError("Error al generar personaje"); }
    finally { setLoading(false); }
  };

  const exportPdf = async (pj) => {
    try {
      const res = await client.get(`/personajes/${pj.id}/pdf`, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a"); a.href = url; a.download = `${pj.nombre}.pdf`;
      a.click(); URL.revokeObjectURL(url);
    } catch { setError("Error al exportar PDF"); }
  };

  return (
    <div className="page-personajes">
      <div className="page-header">
        <h2>Mis Personajes</h2>
        <div className="page-header-actions">
          <button className="btn-secondary" onClick={generarAleatorio} disabled={loading}>
            🎲 Aleatorio
          </button>
          <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancelar" : "+ Nuevo personaje"}
          </button>
        </div>
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
          <div key={pj.id} className="personaje-card">
            <h3 onClick={() => navigate(`/games/${slug}/personajes/${pj.id}`)}>{pj.nombre}</h3>
            <p>{pj.raza} · {pj.clase} · Nivel {pj.nivel}</p>
            <p>PG: {pj.pg_actual || pj.pg_max || pj.puntos_golpe || "-"}/{pj.pg_max || pj.puntos_golpe || "-"}</p>
            <div className="personaje-stats">
              <span>FUE {pj.fuerza}</span><span>DES {pj.destreza}</span><span>CON {pj.constitucion}</span>
              <span>INT {pj.inteligencia}</span><span>SAB {pj.sabiduria}</span><span>CAR {pj.carisma}</span>
            </div>
            <div className="personaje-card-actions">
              <button className="btn-sm btn-secondary" onClick={(e) => { e.stopPropagation(); exportPdf(pj); }}>📄 PDF</button>
              <button className="btn-sm btn-danger" onClick={(e) => { e.stopPropagation(); handleDelete(pj.id); }}>Eliminar</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
