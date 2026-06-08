import { useState, useEffect } from "react";
import client from "../api/client";

export function ClasesRazasPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tipo, setTipo] = useState("");
  const [q, setQ] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (tipo) params.tipo = tipo;
      if (q) params.q = q;
      const res = await client.get("/clases-razas/", { params });
      setData(res.data);
    } catch {
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  return (
    <div className="page-list">
      <h2>Clases y Razas</h2>
      <div className="search-bar">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar..." />
        <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="">Todos</option>
          <option value="clase">Clases</option>
          <option value="raza">Razas</option>
          <option value="general">General</option>
        </select>
        <button onClick={fetchData}>Buscar</button>
      </div>
      {loading && <p className="loading">Cargando...</p>}
      {!loading && data.length === 0 && <p className="empty">Sin resultados</p>}
      <div className="list-grid">
        {data.map((item, i) => (
          <div key={i} className="list-card">
            <h3>{item.nombre}</h3>
            <p className="list-meta">{item.tipo} · DG: {item.dado_golpe || "-"} · {item.habilidad_principal || "-"}</p>
            <p>{item.descripcion}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
