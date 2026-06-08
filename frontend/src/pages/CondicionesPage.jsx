import { useState, useEffect } from "react";
import client from "../api/client";

export function CondicionesPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const params = {};
      if (q) params.q = q;
      const res = await client.get("/condiciones/", { params });
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
      <h2>Condiciones</h2>
      <div className="search-bar">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filtrar..." />
        <button onClick={fetchData}>Buscar</button>
      </div>
      {loading && <p className="loading">Cargando...</p>}
      {!loading && data.length === 0 && <p className="empty">Sin resultados</p>}
      <div className="list-grid">
        {data.map((item, i) => (
          <div key={i} className="list-card">
            <h3>{item.nombre}</h3>
            <p>{item.descripcion}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
