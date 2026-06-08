import { createContext, useContext, useState, useCallback } from "react";
import client from "../api/client";

const GameContext = createContext(null);

export function GameProvider({ children }) {
  const [games, setGames] = useState([]);
  const [currentGame, setCurrentGame] = useState(null);
  const [gamesLoaded, setGamesLoaded] = useState(false);

  const fetchGames = useCallback(async () => {
    try {
      const res = await client.get("/api/games/");
      setGames(res.data);
      setGamesLoaded(true);
      return res.data;
    } catch {
      setGamesLoaded(true);
      return [];
    }
  }, []);

  const selectGame = useCallback((slug) => {
    const game = games.find((g) => g.slug === slug);
    if (game) setCurrentGame(game);
    return game;
  }, [games]);

  const clearGame = useCallback(() => {
    setCurrentGame(null);
  }, []);

  return (
    <GameContext.Provider value={{ games, currentGame, gamesLoaded, fetchGames, selectGame, clearGame }}>
      {children}
    </GameContext.Provider>
  );
}

export const useGames = () => useContext(GameContext);
