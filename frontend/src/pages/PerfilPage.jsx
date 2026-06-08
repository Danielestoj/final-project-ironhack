import { useState, useEffect } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

export function PerfilPage() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await client.get("/auth/perfil");
        setProfile(res.data);
      } catch (err) {
        setProfile(null);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  if (loading) return <p className="loading">Cargando perfil...</p>;

  return (
    <div className="page-perfil">
      <h2>Mi Perfil</h2>
      {profile ? (
        <div className="perfil-card">
          <p><strong>Nombre:</strong> {profile.nombre}</p>
          <p><strong>Email:</strong> {profile.email}</p>
          <p><strong>Rol:</strong> {profile.rol}</p>
          <p><strong>Fecha de registro:</strong> {new Date(profile.fecha_registro).toLocaleDateString()}</p>
        </div>
      ) : (
        <p>No se pudo cargar el perfil</p>
      )}
    </div>
  );
}
