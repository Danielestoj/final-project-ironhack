import { useState, useEffect } from "react";
import client from "../api/client";

export function MetricsPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");

  const fetchDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await client.get("/api/metrics/dashboard");
      setDashboard(res.data);
    } catch (err) {
      setError("Error al cargar métricas");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDashboard(); }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg("");
    try {
      const res = await client.post("/api/metrics/save");
      setSaveMsg(`Guardado en ${res.data.path} (${res.data.entries} eventos)`);
    } catch {
      setSaveMsg("Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="loading">Cargando métricas...</p>;
  if (error) return <p className="form-error">{error}</p>;
  if (!dashboard) return null;

  const maxSpellVisits = dashboard.top_spells.length > 0 ? dashboard.top_spells[0].visitas : 1;

  return (
    <div className="page-metrics">
      <div className="metrics-header">
        <h2>Métricas</h2>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? "Guardando..." : "Guardar en JSON"}
        </button>
      </div>
      {saveMsg && <p className="metrics-save-msg">{saveMsg}</p>}

      <div className="metrics-summary">
        <div className="metrics-card">
          <span className="metrics-num">{dashboard.total_chat_queries}</span>
          <span className="metrics-label">Consultas en chat</span>
        </div>
        <div className="metrics-card">
          <span className="metrics-num">{dashboard.total_searches}</span>
          <span className="metrics-label">Búsquedas</span>
        </div>
        <div className="metrics-card">
          <span className="metrics-num">{dashboard.top_spells.length > 0 ? dashboard.top_spells[0].visitas : 0}</span>
          <span className="metrics-label">Hechizo más visto (veces)</span>
        </div>
      </div>

      <div className="metrics-section">
        <h3>Hechizos más vistos</h3>
        {dashboard.top_spells.length === 0 ? (
          <p className="empty">Sin datos</p>
        ) : (
          <div className="metrics-bars">
            {dashboard.top_spells.map((s) => (
              <div key={s.nombre} className="metrics-bar-row">
                <span className="metrics-bar-label">{s.nombre}</span>
                <div className="metrics-bar-track">
                  <div
                    className="metrics-bar-fill"
                    style={{ width: `${(s.visitas / maxSpellVisits) * 100}%` }}
                  />
                </div>
                <span className="metrics-bar-count">{s.visitas}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="metrics-section">
        <h3>Términos de búsqueda más usados</h3>
        {dashboard.top_search_terms.length === 0 ? (
          <p className="empty">Sin datos</p>
        ) : (
          <div className="metrics-tags">
            {dashboard.top_search_terms.map((t) => (
              <span key={t.termino} className="metrics-tag">
                {t.termino} <small>{t.count}</small>
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="metrics-section">
        <h3>Actividad por juego</h3>
        <table className="metrics-table">
          <thead>
            <tr>
              <th>Juego</th>
              <th>Vistas de hechizos</th>
              <th>Consultas en chat</th>
              <th>Búsquedas</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(dashboard.game_activity).map(([slug, act]) => (
              <tr key={slug}>
                <td>{slug}</td>
                <td>{act.spell_views}</td>
                <td>{act.chat_queries}</td>
                <td>{act.searches}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="metrics-section">
        <h3>Últimas consultas del chat ({dashboard.recent_chat.length})</h3>
        {dashboard.recent_chat.length === 0 ? (
          <p className="empty">Sin datos</p>
        ) : (
          <div className="metrics-query-list">
            {dashboard.recent_chat.slice(0, 10).map((q, i) => (
              <div key={i} className="metrics-query-item">
                <span className="metrics-query-text">{q.texto}</span>
                <span className="metrics-query-meta">{q.juego} · {new Date(q.timestamp).toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
