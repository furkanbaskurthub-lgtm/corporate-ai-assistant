import { useEffect, useRef } from 'react'
import { Bot, MessageSquare } from 'lucide-react'
import MessageBubble from './MessageBubble'

export default function MessageList({ messages, streamingMessage }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingMessage])

  if (!messages.length && !streamingMessage) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-dark-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Bot size={32} className="text-slate-600" />
          </div>
          <h3 className="text-lg font-semibold text-slate-400 mb-1">Merhaba!</h3>
          <p className="text-sm text-slate-600 max-w-sm">
            Dokümanlarınız hakkında soru sormaya başlayın. Yüklediğiniz PDF'ler üzerinden size yardımcı olacağım.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {messages.map((msg) => (
        <MessageBubble key={msg.id || msg.created_at} message={msg} />
      ))}
      {streamingMessage && (
        <MessageBubble message={streamingMessage} isStreaming={true} />
      )}
      <div ref={endRef} />
    </div>
  )
}
