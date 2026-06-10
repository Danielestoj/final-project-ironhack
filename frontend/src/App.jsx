import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { GameProvider } from "./context/GameContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";
import { GameLayout } from "./components/GameLayout";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ChatPage } from "./pages/ChatPage";
import { HechizosPage } from "./pages/HechizosPage";
import { PersonajesPage } from "./pages/PersonajesPage";
import { PerfilPage } from "./pages/PerfilPage";
import { GamesPage } from "./pages/GamesPage";
import { AddGamePage } from "./pages/AddGamePage";
import { CondicionesPage } from "./pages/CondicionesPage";
import { ClasesPage } from "./pages/ClasesPage";
import { RazasPage } from "./pages/RazasPage";
import { EnemigosPage } from "./pages/EnemigosPage";
import { ObjetosPage } from "./pages/ObjetosPage";
import { MetricsPage } from "./pages/MetricsPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <GameProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/games" element={<GamesPage />} />
                <Route path="/games/add" element={<AddGamePage />} />
                <Route path="/perfil" element={<PerfilPage />} />
                <Route path="/metrics" element={<MetricsPage />} />
                <Route path="/games/:slug" element={<GameLayout />}>
                  <Route index element={<Navigate to="chat" replace />} />
                  <Route path="chat" element={<ChatPage />} />
                  <Route path="hechizos" element={<HechizosPage />} />
                  <Route path="personajes" element={<PersonajesPage />} />
                  <Route path="condiciones" element={<CondicionesPage />} />
                  <Route path="clases" element={<ClasesPage />} />
                  <Route path="razas" element={<RazasPage />} />
                  <Route path="enemigos" element={<EnemigosPage />} />
                  <Route path="objetos" element={<ObjetosPage />} />
                  <Route path="perfil" element={<PerfilPage />} />
                </Route>
                <Route path="*" element={<Navigate to="/games" replace />} />
              </Route>
            </Route>
          </Routes>
        </GameProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
