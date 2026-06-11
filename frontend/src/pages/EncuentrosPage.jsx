import { useState } from "react";
import client from "../api/client";

export function EncuentrosPage() {
  const [jugadores, setJugadores] = useState(4);
  const [nivel, setNivel] = useState(3);
  const [dificultad, setDificultad] = useState("medio");
  const [tipo, setTipo] = useState("");
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generar = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await client.post("/api/encuentros/generar", {
        jugadores: Number(jugadores),
        nivel: Number(nivel),
        dificultad,
        tipo,
      });
      setResultado(res.data);
    } catch { setError("Error al generar encuentro"); }
    finally { setLoading(false); }
  };

  return (
    <div className="page-encuentros">
      <div className="page-header">
        <h2>Generador de Encuentros</h2>
      </div>
      {error && <p className="form-error">{error}</p>}
      <form className="encuentro-form" onSubmit={generar}>
        <div className="form-row">
          <div className="form-group">
            <label>Jugadores</label>
            <input type="number" min="1" max="10" value={jugadores} onChange={(e) => setJugadores(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Nivel del grupo</label>
            <input type="number" min="1" max="20" value={nivel} onChange={(e) => setNivel(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Dificultad</label>
            <select value={dificultad} onChange={(e) => setDificultad(e.target.value)}>
              <option value="facil">Fácil</option>
              <option value="medio">Media</option>
              <option value="dificil">Difícil</option>
              <option value="mortal">Mortal</option>
            </select>
          </div>
          <div className="form-group">
            <label>Tipo (opcional)</label>
            <input value={tipo} onChange={(e) => setTipo(e.target.value)} placeholder="ej: dragon, goblin" />
          </div>
        </div>
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? "Generando..." : "Generar Encuentro"}
        </button>
      </form>

      {resultado && (
        <div className="encuentro-result">
          <h3>Encuentro {dificultad} (Nv. {resultado.nivel_grupo}, {resultado.num_jugadores} PJs)</h3>
          <p>Presupuesto XP: {resultado.presupuesto_xp} · Total XP: {resultado.total_xp}</p>
          <table className="encuentro-table">
            <thead>
              <tr><th>#</th><th>Nombre</th><th>CR</th><th>XP</th><th>Tipo</th></tr>
            </thead>
            <tbody>
              {resultado.encuentro.map((e, i) => (
                <tr key={i}>
                  <td>{i + 1}</td>
                  <td>{e.nombre}</td>
                  <td>{e.cr}</td>
                  <td>{e.xp}</td>
                  <td>{e.tipo || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
