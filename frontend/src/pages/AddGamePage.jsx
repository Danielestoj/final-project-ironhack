import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { useGames } from "../context/GameContext";

export function AddGamePage() {
  const navigate = useNavigate();
  const { fetchGames, selectGame } = useGames();
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [icono, setIcono] = useState("🎮");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nombre.trim()) return;
    setSaving(true);
    setError("");
    try {
      const res = await client.post("/api/games/", {
        nombre: nombre.trim(),
        descripcion: descripcion.trim(),
        icono,
      });
      await fetchGames();
      selectGame(res.data.slug);
      navigate(`/games/${res.data.slug}/chat`);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al crear el juego");
    } finally {
      setSaving(false);
    }
  };

  const ICONOS = ["🎮", "🎲", "⚔️", "🐉", "🔮", "🕵️", "🌌", "🧙", "🏰"];

  return (
    <div className="page-add-game">
      <h2>Añadir nuevo juego</h2>
      <form className="add-game-form" onSubmit={handleSubmit}>
        <label>
          Nombre
          <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Ej: Pathfinder" required />
        </label>
        <label>
          Descripción
          <textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)} placeholder="Breve descripción del juego" rows={3} />
        </label>
        <label>
          Icono
          <div className="icono-picker">
            {ICONOS.map((ic) => (
              <span key={ic} className={`icono-opt ${icono === ic ? "selected" : ""}`} onClick={() => setIcono(ic)}>
                {ic}
              </span>
            ))}
          </div>
        </label>
        {error && <p className="form-error">{error}</p>}
        <div className="add-game-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate("/games")}>Cancelar</button>
          <button type="submit" className="btn-primary" disabled={saving || !nombre.trim()}>
            {saving ? "Creando..." : "Crear juego"}
          </button>
        </div>
      </form>
    </div>
  );
}
