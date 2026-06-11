import { useState, useEffect } from "react";
import client from "../api/client";

export function InitiativeTracker() {
  const [combates, setCombates] = useState([]);
  const [selectedCombat, setSelectedCombat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newParticipants, setNewParticipants] = useState([
    { nombre: "", iniciativa: 10, pg: 10, pg_max: 10, tipo: "pj", condiciones: [] }
  ]);

  const fetchCombates = async () => {
    setLoading(true);
    try {
      const res = await client.get("/api/combate/");
      setCombates(res.data);
    } catch { setError("Error al cargar combates"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchCombates(); }, []);

  const addParticipantRow = () => {
    setNewParticipants([...newParticipants, { nombre: "", iniciativa: 10, pg: 10, pg_max: 10, tipo: "pj", condiciones: [] }]);
  };

  const updateParticipantRow = (i, field, value) => {
    const updated = [...newParticipants];
    updated[i] = { ...updated[i], [field]: value };
    if (field === "pg") updated[i].pg_max = value;
    setNewParticipants(updated);
  };

  const removeParticipantRow = (i) => {
    if (newParticipants.length > 1) setNewParticipants(newParticipants.filter((_, j) => j !== i));
  };

  const createCombat = async (e) => {
    e.preventDefault();
    try {
      const res = await client.post("/api/combate/", {
        nombre: "Combate",
        participantes: newParticipants,
      });
      setSelectedCombat(res.data);
      setShowForm(false);
      fetchCombates();
    } catch { setError("Error al crear combate"); }
  };

  const loadCombat = async (id) => {
    try {
      const res = await client.get(`/api/combate/${id}`);
      setSelectedCombat(res.data);
    } catch { setError("Error al cargar combate"); }
  };

  const nextTurn = async () => {
    try {
      const res = await client.post(`/api/combate/${selectedCombat.id}/next`);
      setSelectedCombat(prev => ({ ...prev, ronda: res.data.ronda, turno_actual: res.data.turno_actual }));
    } catch { setError("Error al avanzar turno"); }
  };

  const damage = async (idx) => {
    const dmg = Number(prompt("Daño:"));
    if (isNaN(dmg) || dmg <= 0) return;
    try {
      const res = await client.post(`/api/combate/${selectedCombat.id}/damage?idx=${idx}&dano=${dmg}`);
      setSelectedCombat(prev => {
        const p = [...prev.participantes];
        p[idx] = { ...p[idx], pg: res.data.pg_restantes };
        return { ...prev, participantes: p };
      });
    } catch { setError("Error al aplicar daño"); }
  };

  const heal = async (idx) => {
    const val = Number(prompt("Curación:"));
    if (isNaN(val) || val <= 0) return;
    try {
      const res = await client.post(`/api/combate/${selectedCombat.id}/heal?idx=${idx}&curacion=${val}`);
      setSelectedCombat(prev => {
        const p = [...prev.participantes];
        p[idx] = { ...p[idx], pg: res.data.pg_restantes };
        return { ...prev, participantes: p };
      });
    } catch { setError("Error al curar"); }
  };

  const endCombat = async () => {
    if (!confirm("¿Terminar combate?")) return;
    try {
      await client.post(`/api/combate/${selectedCombat.id}/end`);
      setSelectedCombat(null);
      fetchCombates();
    } catch { setError("Error al terminar combate"); }
  };

  if (selectedCombat) {
    const p = selectedCombat.participantes;
    const current = p[selectedCombat.turno_actual];
    return (
      <div className="combat-view">
        {error && <p className="form-error">{error}</p>}
        <div className="combat-header">
          <h2>⚔ {selectedCombat.nombre}</h2>
          <span className="combat-round">Ronda {selectedCombat.ronda} · Turno: <strong>{current?.nombre}</strong></span>
          <div className="combat-actions">
            <button onClick={nextTurn} className="btn-primary">Siguiente Turno</button>
            <button onClick={() => setSelectedCombat(null)} className="btn-secondary">Volver</button>
            <button onClick={endCombat} className="btn-danger">Terminar</button>
          </div>
        </div>
        <div className="combat-grid">
          {p.map((part, i) => {
            const esActual = i === selectedCombat.turno_actual;
            const pct = part.pg_max > 0 ? (part.pg / part.pg_max) * 100 : 0;
            return (
              <div key={i} className={`combat-card ${esActual ? "combat-card--active" : ""} ${part.tipo === "enemigo" ? "combat-card--enemy" : ""}`}>
                <div className="combat-card-header">
                  <strong>{part.nombre}</strong>
                  <span className="combat-init">Inic: {part.iniciativa}</span>
                </div>
                <div className="combat-hp-bar">
                  <div className="combat-hp-fill" style={{ width: `${pct}%` }} />
                </div>
                <div className="combat-hp-text">PG: {part.pg}/{part.pg_max}</div>
                <div className="combat-card-actions">
                  <button onClick={() => damage(i)} className="btn-sm btn-danger">Daño</button>
                  <button onClick={() => heal(i)} className="btn-sm btn-primary">Curar</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="combat-page">
      <div className="page-header">
        <h2>⚔ Iniciativa de Combate</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancelar" : "+ Nuevo Combate"}
        </button>
      </div>
      {error && <p className="form-error">{error}</p>}
      {showForm && (
        <form className="combat-form" onSubmit={createCombat}>
          <h3>Participantes</h3>
          <div className="combat-form-header">
            <span>Nombre</span>
            <span>Iniciativa</span>
            <span>PG</span>
            <span>Tipo</span>
            <span></span>
          </div>
          {newParticipants.map((p, i) => (
            <div key={i} className="combat-form-row">
              <input value={p.nombre} onChange={(e) => updateParticipantRow(i, "nombre", e.target.value)} placeholder="Ej: Aldric" required />
              <input type="number" value={p.iniciativa} onChange={(e) => updateParticipantRow(i, "iniciativa", Number(e.target.value))} />
              <input type="number" value={p.pg} onChange={(e) => updateParticipantRow(i, "pg", Number(e.target.value))} />
              <select value={p.tipo} onChange={(e) => updateParticipantRow(i, "tipo", e.target.value)}>
                <option value="pj">PJ</option><option value="enemigo">Enemigo</option>
              </select>
              {newParticipants.length > 1 && <button type="button" onClick={() => removeParticipantRow(i)} className="btn-sm btn-danger">&times;</button>}
            </div>
          ))}
          <div className="combat-form-actions">
            <button type="button" onClick={addParticipantRow} className="btn-secondary">+ Añadir</button>
            <button type="submit" className="btn-primary">Iniciar Combate</button>
          </div>
        </form>
      )}
      {loading && <p className="loading">Cargando...</p>}
      {!loading && combates.length === 0 && <p className="empty">No hay combates activos.</p>}
      <div className="combat-list">
        {combates.map((c) => (
          <div key={c.id} className="combat-list-card" onClick={() => loadCombat(c.id)}>
            <strong>{c.nombre}</strong>
            <span>Ronda {c.ronda} · {c.participantes?.length || 0} participantes</span>
          </div>
        ))}
      </div>
    </div>
  );
}
