import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { useGames } from "../context/GameContext";

const PREDEFINED_CATEGORIES = [
  { key: "hechizos", label: "Hechizos", icono: "✨" },
  { key: "reglas_combate", label: "Combate", icono: "⚔️" },
  { key: "condiciones", label: "Condiciones", icono: "⚡" },
  { key: "clases_y_razas", label: "Clases y Razas", icono: "📚" },
  { key: "enemigos", label: "Enemigos", icono: "👹" },
  { key: "objetos_y_equipo", label: "Objetos", icono: "🛡️" },
  { key: "reglas_basicas", label: "Reglas", icono: "📖" },
  { key: "trasfondo_y_escenarios", label: "Trasfondo", icono: "🌍" },
];

export function AddGamePage() {
  const navigate = useNavigate();
  const { fetchGames, selectGame } = useGames();
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [icono, setIcono] = useState("🎮");
  const [archivo, setArchivo] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [selectedCats, setSelectedCats] = useState([]);
  const [customCat, setCustomCat] = useState("");
  const fileRef = useRef(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0] || e.target?.files?.[0];
    if (file) {
      const ext = file.name.split(".").pop().toLowerCase();
      if (!["pdf", "txt", "md"].includes(ext)) {
        setError("Solo se aceptan archivos PDF, TXT o MD");
        return;
      }
      setArchivo(file);
      setError("");
    }
  };

  const toggleCategory = (key) => {
    setSelectedCats((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const addCustomCategory = () => {
    const val = customCat.trim().toLowerCase().replace(/\s+/g, "_").replace(/[^a-z0-9_]/g, "");
    if (val && !selectedCats.includes(val)) {
      setSelectedCats((prev) => [...prev, val]);
    }
    setCustomCat("");
  };

  const removeCustomCategory = (key) => {
    setSelectedCats((prev) => prev.filter((k) => k !== key));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nombre.trim()) return;
    if (!archivo) {
      setError("Debes subir un archivo con las reglas del juego");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("nombre", nombre.trim());
      formData.append("descripcion", descripcion.trim());
      formData.append("icono", icono);
      formData.append("archivo", archivo);
      formData.append("categorias", JSON.stringify(selectedCats));
      const res = await client.post("/api/games/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await fetchGames();
      selectGame(res.data.slug, res.data);
      navigate(`/games/${res.data.slug}/chat`);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al crear el juego");
    } finally {
      setSaving(false);
    }
  };

  const ICONOS = ["🎮", "🎲", "⚔️", "🐉", "🔮", "🕵️", "🌌", "🧙", "🏰"];

  const customCats = selectedCats.filter((k) => !PREDEFINED_CATEGORIES.find((c) => c.key === k));

  return (
    <div className="page-add-game">
      <h2>Añadir nuevo juego</h2>
      <form className="add-game-form" onSubmit={handleSubmit}>
        <label>
          Nombre
          <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Ej: Pathfinder" required />
        </label>
        <label>
          Descripción
          <textarea value={descripcion} onChange={(e) => setDescripcion(e.target.value)} placeholder="Breve descripción del juego" rows={3} />
        </label>
        <label>
          Icono
          <div className="icono-picker">
            {ICONOS.map((ic) => (
              <span key={ic} className={`icono-opt ${icono === ic ? "selected" : ""}`} onClick={() => setIcono(ic)}>
                {ic}
              </span>
            ))}
          </div>
        </label>
        <fieldset className="cat-fieldset">
          <legend>Categorías del juego</legend>
          <div className="cat-checkboxes">
            {PREDEFINED_CATEGORIES.map((cat) => (
              <label key={cat.key} className="cat-checkbox">
                <input
                  type="checkbox"
                  checked={selectedCats.includes(cat.key)}
                  onChange={() => toggleCategory(cat.key)}
                />
                <span>{cat.icono}</span> {cat.label}
              </label>
            ))}
          </div>
          <div className="cat-custom">
            <input
              value={customCat}
              onChange={(e) => setCustomCat(e.target.value)}
              placeholder="Escribe una categoría personalizada..."
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addCustomCategory(); } }}
            />
            <button type="button" className="btn-secondary" onClick={addCustomCategory}>Añadir</button>
          </div>
          {customCats.length > 0 && (
            <div className="cat-tags">
              {customCats.map((k) => (
                <span key={k} className="cat-tag">
                  📋 {k.replace(/_/g, " ")}
                  <button type="button" onClick={() => removeCustomCategory(k)}>✕</button>
                </span>
              ))}
            </div>
          )}
        </fieldset>
        <label>
          Archivo de reglas <span className="required">*</span>
          <div
            className={`file-dropzone ${dragOver ? "drag-over" : ""} ${archivo ? "has-file" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileRef.current?.click()}
          >
            {archivo ? (
              <div className="file-preview">
                <span className="file-icon">{archivo.name.endsWith(".pdf") ? "📄" : "📝"}</span>
                <span className="file-name">{archivo.name}</span>
                <span className="file-size">({(archivo.size / 1024).toFixed(1)} KB)</span>
                <button type="button" className="file-remove" onClick={(e) => { e.stopPropagation(); setArchivo(null); }}>
                  ✕
                </button>
              </div>
            ) : (
              <div className="file-placeholder">
                <span className="file-drop-icon">📂</span>
                <p>Arrastra un archivo aquí o haz clic para seleccionar</p>
                <p className="file-hint">PDF, TXT o MD</p>
              </div>
            )}
          </div>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.md"
            style={{ display: "none" }}
            onChange={handleFileDrop}
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <div className="add-game-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate("/games")}>Cancelar</button>
          <button type="submit" className="btn-primary" disabled={saving || !nombre.trim() || !archivo}>
            {saving ? "Procesando..." : "Crear juego"}
          </button>
        </div>
      </form>
    </div>
  );
}
