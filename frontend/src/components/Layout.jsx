import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useGames } from "../context/GameContext";
import { useEffect } from "react";

export function Layout() {
  const { user, logout } = useAuth();
  const { games, currentGame, selectGame } = useGames();
  const navigate = useNavigate();
  const location = useLocation();

  const inGame = location.pathname.startsWith("/games/") && currentGame;

  const handleGameChange = (e) => {
    const slug = e.target.value;
    if (slug) {
      selectGame(slug);
      navigate(`/games/${slug}/chat`);
    }
  };

  const goHome = () => {
    navigate("/games");
  };

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-title" onClick={goHome}>
            Multigame RPG
          </h1>
          <select className="game-selector" value={currentGame?.slug || ""} onChange={handleGameChange}>
            <option value="">Seleccionar juego</option>
            {games.map((g) => (
              <option key={g.slug} value={g.slug}>{g.icono} {g.nombre}</option>
            ))}
          </select>
        </div>
        <div className="header-right">
          {user?.rol === "admin" && (
            <button className="nav-btn" onClick={() => navigate("/metrics")}>
              Métricas
            </button>
          )}
          <button className="nav-btn" onClick={() => navigate("/perfil")}>
            Perfil
          </button>
          <button className="nav-btn nav-btn--logout" onClick={() => { logout(); navigate("/login"); }}>
            Salir
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
