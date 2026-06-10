import { useParams } from "react-router-dom";
import { Chat } from "../components/Chat";

export function ChatPage() {
  const { slug } = useParams();
  return (
    <div className="page-chat">
      <Chat sessionId={`sesion-${Date.now()}`} gameSlug={slug || "dnd"} />
    </div>
  );
}
