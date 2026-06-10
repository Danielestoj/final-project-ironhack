import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function validar(nombre, email, password) {
  const errs = {};
  if (!nombre.trim()) errs.nombre = "El nombre es requerido";
  else if (nombre.trim().length < 2) errs.nombre = "El nombre debe tener al menos 2 caracteres";
  if (!email.trim()) errs.email = "El email es requerido";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = "Formato de email inválido";
  if (!password) errs.password = "La contraseña es requerida";
  else if (password.length < 8) errs.password = "La contraseña debe tener al menos 8 caracteres";
  return errs;
}

export function RegisterPage() {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [errores, setErrores] = useState({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const errs = validar(nombre, email, password);
    setErrores(errs);
    if (Object.keys(errs).length > 0) return;

    setError("");
    setLoading(true);
    try {
      await register(email, password, nombre);
      navigate("/games");
    } catch (err) {
      setError(err.response?.data?.detail || "Error al registrarse");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <h1>Crear cuenta</h1>
        {error && <p className="form-error">{error}</p>}
        <div className="field-group">
          <input type="text" value={nombre} onChange={(e) => { setNombre(e.target.value); setErrores((prev) => ({ ...prev, nombre: "" })); }} placeholder="Nombre" required minLength={2} />
          {errores.nombre && <span className="field-error">{errores.nombre}</span>}
        </div>
        <div className="field-group">
          <input type="email" value={email} onChange={(e) => { setEmail(e.target.value); setErrores((prev) => ({ ...prev, email: "" })); }} placeholder="Email" required />
          {errores.email && <span className="field-error">{errores.email}</span>}
        </div>
        <div className="field-group">
          <input type="password" value={password} onChange={(e) => { setPassword(e.target.value); setErrores((prev) => ({ ...prev, password: "" })); }} placeholder="Contraseña (mín. 8 caracteres)" required minLength={8} />
          {errores.password && <span className="field-error">{errores.password}</span>}
        </div>
        <button type="submit" disabled={loading}>{loading ? "Registrando..." : "Registrarse"}</button>
        <p className="auth-link">¿Ya tienes cuenta? <Link to="/login">Entra</Link></p>
      </form>
    </div>
  );
}
