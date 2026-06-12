import { useState, useEffect, useCallback } from "react";
import client from "../api/client";

export function ClasesPage() {
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
      const res = await client.get("/clases/", { params });
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
      <p><strong>{label}:</strong> {display}</p>
    );
  };

  const renderTabla = (tabla) => {
    if (!tabla?.columnas || !tabla?.filas) return null;
    return (
      <div className="class-table-section">
        <h3 className="desc-section-title">Tabla de progresión</h3>
        <div className="class-table-wrapper">
          <table className="class-table">
            <thead>
              <tr>{tabla.columnas.map((col, i) => <th key={i}>{col}</th>)}</tr>
            </thead>
            <tbody>
              {tabla.filas.map((fila, i) => (
                <tr key={i}>{fila.map((celda, j) => <td key={j}>{celda}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderDescripcion = (text) => {
    if (!text) return null;
    const rawLines = text.split("\n");
    const blocks = [];
    let buf = [];
    for (const line of rawLines) {
      const t = line.trim();
      if (!t) continue;
      const isHeader = /^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s[a-záéíóúñ]+)*:$/.test(t) || t.endsWith(":");
      const isBullet = t.startsWith("●") || t.startsWith("•") || t.startsWith("(a)") || t.startsWith("(b)");
      if (isHeader || isBullet) {
        if (buf.length) { blocks.push({ type: "text", lines: buf.splice(0) }); }
        blocks.push({ type: isHeader ? "header" : "bullet", lines: [t] });
      } else {
        buf.push(t);
      }
    }
    if (buf.length) blocks.push({ type: "text", lines: buf });
    return (
      <div className="class-desc-full">
        {blocks.map((b, i) => {
          if (b.type === "header") return <p key={i} className="desc-header"><strong>{b.lines[0]}</strong></p>;
          if (b.type === "bullet") return <p key={i} className="desc-bullet">{b.lines[0]}</p>;
          return <p key={i} className="desc-text">{b.lines.join(" ")}</p>;
        })}
      </div>
    );
  };

  return (
    <div className="page-list">
      <h2>Clases</h2>
      <form className="search-bar" onSubmit={handleSearch}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar clase..." />
        <button type="submit">Buscar</button>
      </form>
      {loading && <p className="loading">Cargando...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && data.length === 0 && <p className="empty">Sin resultados</p>}
      <div className="list-grid">
        {data.map((item, i) => (
          <div key={i} className="list-card" onClick={() => openModal(item)}>
            <h3>{item.nombre}</h3>
            <p className="list-meta">DG: {item.dado_golpe || "-"} · Salvaciones: {item.habilidad_principal || "-"}</p>
          </div>
        ))}
      </div>
      {selected && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal-content modal-content--wide" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>&times;</button>
            <h2>{selected.nombre}</h2>
            <p className="list-meta">DG: {selected.dado_golpe || "-"}</p>
            <div className="hechizo-detail">
              <p><strong>DG:</strong> {selected.dado_golpe || "-"}</p>
              {renderDetail("Salvaciones", selected.habilidad_principal)}
              {selected.armadura && <p><strong>Armadura:</strong> {selected.armadura}</p>}
              {selected.armas && <p><strong>Armas:</strong> {selected.armas}</p>}
              {selected.equipo && <p><strong>Equipo inicial:</strong> {selected.equipo}</p>}
              {renderTabla(selected.tabla)}
              <div className="desc-section">
                <h3 className="desc-section-title">Descripción</h3>
                {renderDescripcion(selected.descripcion)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
