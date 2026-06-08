import { useState, useEffect, useCallback } from "react";
import client from "../api/client";

export function HechizosPage() {
  const [hechizos, setHechizos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [nivel, setNivel] = useState("");
  const [escuela, setEscuela] = useState("");
  const [selected, setSelected] = useState(null);

  const fetchHechizos = async () => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (q) params.q = q;
      if (nivel !== "") params.nivel = parseInt(nivel);
      if (escuela) params.escuela = escuela;
      const res = await client.get("/hechizos/", { params });
      setHechizos(res.data);
    } catch (err) {
      setError("Error al cargar hechizos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchHechizos(); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchHechizos();
    client.post("/api/metrics/search", { q, nivel, escuela, game_slug: "dnd" }).catch(() => {});
  };

  const ESCUELAS = [
    "Abjuración", "Adivinación", "Conjuración", "Encantamiento",
    "Evocación", "Ilusionismo", "Nigromancia", "Transmutación",
  ];

  const openModal = (h) => {
    setSelected(h);
    client.post("/api/metrics/spell-view", { nombre: h.nombre, game_slug: "dnd" }).catch(() => {});
  };

  const closeModal = useCallback(() => setSelected(null), []);

  useEffect(() => {
    if (!selected) return;
    const handleKey = (e) => { if (e.key === "Escape") closeModal(); };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selected, closeModal]);

  return (
    <div className="page-hechizos">
      <h2>Hechizos</h2>
      <form className="search-form" onSubmit={handleSearch}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar hechizo..." />
        <select value={nivel} onChange={(e) => setNivel(e.target.value)}>
          <option value="">Todos los niveles</option>
          {[0,1,2,3,4,5,6,7,8,9].map(n => <option key={n} value={n}>Nivel {n}</option>)}
        </select>
        <select value={escuela} onChange={(e) => setEscuela(e.target.value)}>
          <option value="">Todas las escuelas</option>
          {ESCUELAS.map(e => <option key={e} value={e}>{e}</option>)}
        </select>
        <button type="submit">Buscar</button>
      </form>

      {loading && <p className="loading">Cargando...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && hechizos.length === 0 && <p className="empty">No se encontraron hechizos</p>}

      <div className="hechizo-grid">
        {hechizos.map((h) => (
          <div key={h.nombre} className="hechizo-card" onClick={() => openModal(h)}>
            <h3>{h.nombre}</h3>
            <p className="hechizo-meta">{h.escuela} · Nivel {h.nivel}</p>
          </div>
        ))}
      </div>

      {selected && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>&times;</button>
            <h2>{selected.nombre}</h2>
            <p className="hechizo-meta">{selected.escuela} · Nivel {selected.nivel}</p>
            <div className="hechizo-detail">
              {selected.tiempo && <p><strong>Tiempo:</strong> {selected.tiempo}</p>}
              {selected.alcance && <p><strong>Alcance:</strong> {selected.alcance}</p>}
              {selected.componentes && <p><strong>Componentes:</strong> {selected.componentes}</p>}
              {selected.duracion && <p><strong>Duración:</strong> {selected.duracion}</p>}
              <p className="hechizo-desc">{selected.descripcion}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
