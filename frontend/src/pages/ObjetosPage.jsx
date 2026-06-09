import { useState, useEffect, useCallback } from "react";
import client from "../api/client";

const LABELS = {
  armaduras: "Armaduras",
  armas: "Armas",
  equipo: "Equipo",
  herramientas: "Herramientas",
  objetos_magicos: "Objetos Mágicos",
};

function resumir(item) {
  const keys = Object.keys(item).filter((k) => k !== "nombre" && k !== "seccion" && item[k]);
  return keys.slice(0, 2).map((k) => ({ label: k, valor: item[k] }));
}

export function ObjetosPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [seccion, setSeccion] = useState("");
  const [selected, setSelected] = useState(null);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const params = {};
      if (q) params.q = q;
      if (seccion) params.seccion = seccion;
      const res = await client.get("/objetos/", { params });
      setItems(res.data);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchItems();
  };

  const openModal = (item) => setSelected(item);
  const closeModal = useCallback(() => setSelected(null), []);

  useEffect(() => {
    if (!selected) return;
    const handleKey = (e) => {
      if (e.key === "Escape") closeModal();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [selected, closeModal]);

  const agrupado = {};
  for (const item of items) {
    const s = item.seccion || "otros";
    if (!agrupado[s]) agrupado[s] = [];
    agrupado[s].push(item);
  }

  return (
    <div className="page-objetos">
      <h2>Objetos y Equipo</h2>

      <form className="search-form" onSubmit={handleSearch}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar objeto..." />
        <select value={seccion} onChange={(e) => setSeccion(e.target.value)}>
          <option value="">Todas las secciones</option>
          {Object.entries(LABELS).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
        <button type="submit">Buscar</button>
      </form>

      {loading && <p className="loading">Cargando...</p>}
      {!loading && items.length === 0 && <p className="empty">Sin resultados</p>}

      {!loading &&
        items.length > 0 &&
        Object.entries(agrupado).map(([key, grupo]) => (
          <section key={key} className="obj-section">
            <h3 className="obj-section-title">
              {LABELS[key] || key} <span className="obj-count">{grupo.length}</span>
            </h3>
            <div className="obj-grid">
              {grupo.map((item, i) => {
                const campos = item.seccion === "objetos_magicos" ? [] : resumir(item);
                return (
                  <div key={i} className="obj-card" onClick={() => openModal(item)}>
                    <h4>{item.nombre}</h4>
                    {campos.map((c, j) => (
                      <p key={j} className="obj-meta">
                        {c.valor}
                      </p>
                    ))}
                  </div>
                );
              })}
            </div>
          </section>
        ))}

      {selected && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>
              &times;
            </button>
            <h2>{selected.nombre}</h2>
            <p className="obj-meta">{LABELS[selected.seccion] || selected.seccion}</p>
            <div className="obj-detail">
              {Object.entries(selected)
                .filter(([k]) => k !== "nombre" && k !== "seccion")
                .map(([k, v]) => (
                  <p key={k}>
                    <strong>{k}:</strong> {v}
                  </p>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
