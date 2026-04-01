import Header from '../components/Layout/Header'
import ChatWindow from '../components/Chat/ChatWindow'
import { useChatStore } from '../stores/chatStore'

export default function ChatPage() {
  const { activeSessionId, sessions } = useChatStore()
  const activeSession = sessions.find((s) => s.id === activeSessionId)

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header title={activeSession?.title || 'Sohbet'} />
      <ChatWindow />
    </div>
  )
}
