import { useState, useRef, useEffect } from "react";
import client from "../api/client";

export function Chat({ sessionId = "default", gameSlug = "dnd" }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError("");
    setLoading(true);

    client.post("/api/metrics/chat-query", { texto: userMessage.content, game_slug: gameSlug }).catch(() => {});

    try {
      const res = await client.post("/api/chat", {
        message: userMessage.content,
        session_id: sessionId,
        game_slug: gameSlug,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.response },
      ]);
    } catch (err) {
      setError("Error al conectar con el agente. Inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">
            ¡Bienvenido, aventurero! Pregúntame sobre reglas del juego, contenido, o haz una tirada de dados.
          </p>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg chat-msg--${msg.role}`}>
            <div className="chat-msg__label">
              {msg.role === "user" ? "🧙 Tú" : "🐉 Asistente"}
            </div>
            <div className="chat-msg__content">{msg.content}</div>
          </div>
        ))}

        {loading && (
          <div className="chat-msg chat-msg--assistant chat-msg--typing">
            <div className="chat-msg__label">🐉 Asistente</div>
            <div className="chat-msg__content">···</div>
          </div>
        )}

        {error && <p className="chat-error">{error}</p>}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendMessage} className="chat-input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ej: tira 1d20, busca bola de fuego, qué es cegado..."
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "..." : "Enviar"}
        </button>
      </form>
    </div>
  );
}
