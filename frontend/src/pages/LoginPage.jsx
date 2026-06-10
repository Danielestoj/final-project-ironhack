import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function validar(email, password) {
  const errs = {};
  if (!email.trim()) errs.email = "El email es requerido";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = "Formato de email inválido";
  if (!password) errs.password = "La contraseña es requerida";
  return errs;
}

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [errores, setErrores] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const errs = validar(email, password);
    setErrores(errs);
    if (Object.keys(errs).length > 0) return;

    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/games");
    } catch (err) {
      setError(err.response?.data?.detail || "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <h1>Iniciar sesión</h1>
        {error && <p className="form-error">{error}</p>}
        <div className="field-group">
          <input type="email" value={email} onChange={(e) => { setEmail(e.target.value); setErrores((prev) => ({ ...prev, email: "" })); }} placeholder="Email" required />
          {errores.email && <span className="field-error">{errores.email}</span>}
        </div>
        <div className="field-group">
          <input type="password" value={password} onChange={(e) => { setPassword(e.target.value); setErrores((prev) => ({ ...prev, password: "" })); }} placeholder="Contraseña" required />
          {errores.password && <span className="field-error">{errores.password}</span>}
        </div>
        <button type="submit" disabled={loading}>{loading ? "Entrando..." : "Entrar"}</button>
        <p className="auth-link">¿No tienes cuenta? <Link to="/register">Regístrate</Link></p>
      </form>
    </div>
  );
}
