import { createContext, useContext, useState } from "react";
import { login as apiLogin, register as apiRegister, logout as apiLogout, getToken, getUser } from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getToken());
  const [user, setUser] = useState(getUser());

  const login = async (email, password) => {
    const data = await apiLogin(email, password);
    setToken(data.access_token);
    setUser(data.usuario);
  };

  const register = async (email, password, nombre) => {
    const data = await apiRegister(email, password, nombre);
    setToken(data.access_token);
    setUser(data.usuario);
  };

  const logout = () => {
    apiLogout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, isAuth: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
