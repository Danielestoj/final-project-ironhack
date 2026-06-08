import { Chat } from "../components/Chat";

export function ChatPage() {
  return (
    <div className="page-chat">
      <Chat sessionId={`sesion-${Date.now()}`} />
    </div>
  );
}
