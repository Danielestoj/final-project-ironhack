import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useGames } from "../context/GameContext";
import { useAuth } from "../context/AuthContext";
import client from "../api/client";

export function GamesPage() {
  const { games, fetchGames, selectGame } = useGames();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGames().then(() => setLoading(false));
  }, [fetchGames]);

  const enterGame = (slug) => {
    selectGame(slug);
    navigate(`/games/${slug}/chat`);
  };

  const handleDelete = async (e, slug, nombre) => {
    e.stopPropagation();
    if (!window.confirm(`¿Eliminar "${nombre}"? Se borrará todo su contenido permanentemente.`)) return;
    try {
      await client.delete(`/api/games/${slug}`);
      await fetchGames();
    } catch (err) {
      alert(err.response?.data?.detail || "Error al eliminar el juego");
    }
  };

  return (
    <div className="page-games">
      <h2>Selecciona un juego</h2>
      {loading && <p className="loading">Cargando juegos...</p>}
      {!loading && games.length === 0 && (
        <p className="empty">No hay juegos disponibles. {user?.rol === "admin" && "Crea uno nuevo."}</p>
      )}
      <div className="games-grid">
        {games.map((g) => (
          <div key={g.slug} className="game-card" onClick={() => enterGame(g.slug)}>
            {user?.rol === "admin" && (
              <button className="game-delete-btn" onClick={(e) => handleDelete(e, g.slug, g.nombre)} title="Eliminar juego">
                🗑️
              </button>
            )}
            <span className="game-icon">{g.icono}</span>
            <h3>{g.nombre}</h3>
            <p className="game-desc">{g.descripcion}</p>
          </div>
        ))}
        {user?.rol === "admin" && (
          <div className="game-card game-card--add" onClick={() => navigate("/games/add")}>
            <span className="game-icon">+</span>
            <h3>Añadir juego</h3>
            <p className="game-desc">Crear un nuevo juego desde la plantilla</p>
          </div>
        )}
      </div>
    </div>
  );
}
