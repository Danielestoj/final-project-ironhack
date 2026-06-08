import { useState, useEffect } from "react";
import client from "../api/client";

const RAZAS = ["Humano", "Elfo", "Enano", "Mediano", "Semielfo", "Semiorco", "Gnomo", "Tiefling"];
const CLASES = ["Guerrero", "Mago", "Pícaro", "Clérigo", "Bárbaro", "Explorador", "Paladín", "Druida"];

const initialForm = { nombre: "", raza: "Humano", clase: "Guerrero", nivel: 1, fuerza: 10, destreza: 10, constitucion: 10, inteligencia: 10, sabiduria: 10, carisma: 10, puntos_golpe: 10 };

export function PersonajesPage() {
  const [personajes, setPersonajes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);

  const fetchPersonajes = async () => {
    setLoading(true);
    try {
      const res = await client.get("/personajes/");
      setPersonajes(res.data);
    } catch (err) {
      setError("Error al cargar personajes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPersonajes(); }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = { ...form, nivel: Number(form.nivel), puntos_golpe: Number(form.puntos_golpe), fuerza: Number(form.fuerza), destreza: Number(form.destreza), constitucion: Number(form.constitucion), inteligencia: Number(form.inteligencia), sabiduria: Number(form.sabiduria), carisma: Number(form.carisma) };
      await client.post("/personajes/", payload);
      setShowForm(false);
      setForm(initialForm);
      fetchPersonajes();
    } catch (err) {
      setError("Error al crear personaje");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("¿Eliminar personaje?")) return;
    try {
      await client.delete(`/personajes/${id}`);
      fetchPersonajes();
    } catch (err) {
      setError("Error al eliminar");
    }
  };

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
            <select name="raza" value={form.raza} onChange={handleChange}>{RAZAS.map(r => <option key={r}>{r}</option>)}</select>
            <select name="clase" value={form.clase} onChange={handleChange}>{CLASES.map(c => <option key={c}>{c}</option>)}</select>
            <input name="nivel" type="number" min="1" max="20" value={form.nivel} onChange={handleChange} placeholder="Nivel" />
          </div>
          <div className="form-row stats">
            {["fuerza", "destreza", "constitucion", "inteligencia", "sabiduria", "carisma"].map(stat => (
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
            <h3>{pj.nombre}</h3>
            <p>{pj.raza} · {pj.clase} · Nivel {pj.nivel}</p>
            <p>PG: {pj.puntos_golpe}</p>
            <div className="personaje-stats">
              <span>FUE {pj.fuerza}</span><span>DES {pj.destreza}</span><span>CON {pj.constitucion}</span>
              <span>INT {pj.inteligencia}</span><span>SAB {pj.sabiduria}</span><span>CAR {pj.carisma}</span>
            </div>
            {pj.hechizos_favoritos?.length > 0 && (
              <p className="hechizos-list">Hechizos: {pj.hechizos_favoritos.join(", ")}</p>
            )}
            <button className="btn-delete" onClick={() => handleDelete(pj.id)}>Eliminar</button>
          </div>
        ))}
      </div>
    </div>
  );
}
