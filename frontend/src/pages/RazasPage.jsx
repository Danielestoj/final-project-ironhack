import { useState, useEffect, useCallback } from "react";
import client from "../api/client";

export function RazasPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (q) params.q = q;
      const res = await client.get("/razas/", { params });
      setData(res.data);
    } catch {
      setError("Error al cargar datos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchData();
  };

  const openModal = (item) => {
    setSelected(item);
  };

  const closeModal = useCallback(() => setSelected(null), []);

  useEffect(() => {
    if (!selected) return;
    const handleKey = (e) => { if (e.key === "Escape") closeModal(); };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selected, closeModal]);

  const renderDetail = (label, value) => {
    if (!value || (Array.isArray(value) && value.length === 0)) return null;
    const display = Array.isArray(value) ? value.join("\n") : value;
    return (
      <p>
        <strong>{label}:</strong>{" "}
        {display}
      </p>
    );
  };

  return (
    <div className="page-list">
      <h2>Razas</h2>
      <form className="search-bar" onSubmit={handleSearch}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar raza..." />
        <button type="submit">Buscar</button>
      </form>
      {loading && <p className="loading">Cargando...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && data.length === 0 && <p className="empty">Sin resultados</p>}
      <div className="list-grid">
        {data.map((item, i) => (
          <div key={i} className="list-card" onClick={() => openModal(item)}>
            <h3>{item.nombre}</h3>
            <p className="list-meta">{item.atributos?.length || 0} atributos raciales</p>
          </div>
        ))}
      </div>
      {selected && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal-content modal-content--wide" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>&times;</button>
            <h2>{selected.nombre}</h2>
            <div className="hechizo-detail">
              {selected.atributos?.map((a, i) => (
                <p key={i}>
                  <strong>{a.nombre}:</strong> {a.descripcion}
                </p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
