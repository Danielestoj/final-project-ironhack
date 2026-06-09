import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import client from "../api/client";
import { useGames } from "../context/GameContext";

export function GameSectionPage() {
  const { slug, section } = useParams();
  const { currentGame } = useGames();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    client
      .get(`/api/games/${slug}/data/${section}`)
      .then((res) => setData(res.data))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [slug, section]);

  const navItem = currentGame?.nav?.find((n) => n.path === section);
  const title = navItem?.label || section;

  if (loading) return <p className="loading">Cargando...</p>;

  if (data.length > 0 && data[0].contenido) {
    return (
      <div className="page-section">
        <h2>{title}</h2>
        <div className="section-paragraphs">
          {data.map((item, i) => (
            <p key={i} className="section-paragraph">{item.contenido}</p>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="page-section">
      <h2>{title}</h2>
      {data.length === 0 && <p className="empty">No hay contenido disponible</p>}
      <div className="list-grid">
        {data.map((item, i) => (
          <div key={i} className="list-card">
            <h3>{item.nombre}</h3>
            <p>{item.descripcion}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
