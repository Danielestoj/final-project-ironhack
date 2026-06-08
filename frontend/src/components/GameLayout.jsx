import { useEffect } from "react";
import { Outlet, useParams, useNavigate, useLocation } from "react-router-dom";
import { useGames } from "../context/GameContext";

export function GameLayout() {
  const { slug } = useParams();
  const { games, selectGame, currentGame, clearGame } = useGames();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (slug) {
      const game = selectGame(slug);
      if (!game) {
        navigate("/games", { replace: true });
      }
    }
    return () => clearGame();
  }, [slug, selectGame, clearGame, navigate]);

  if (!currentGame) return null;

  return (
    <div className="game-layout">
      <nav className="game-nav">
        {currentGame.nav.map((item) => (
          <button
            key={item.path}
            className={`game-nav-btn ${location.pathname === `/games/${slug}/${item.path}` ? "active" : ""}`}
            onClick={() => navigate(`/games/${slug}/${item.path}`)}
          >
            <span className="game-nav-icon">{item.icono}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="game-content">
        <Outlet />
      </div>
    </div>
  );
}
