import { useEffect, useRef, useCallback, useState } from 'react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import { useChatStore } from '../../stores/chatStore'
import { chatService } from '../../services/chatService'

export default function ChatWindow() {
  const wsRef = useRef(null)
  const [streamingMessage, setStreamingMessage] = useState(null)
  const {
    activeSessionId,
    messages,
    isStreaming,
    selectedModel,
    setMessages,
    addMessage,
    setStreaming,
  } = useChatStore()

  const sessionMessages = messages[activeSessionId] || []

  useEffect(() => {
    if (!activeSessionId) return
    loadMessages()
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [activeSessionId])

  const loadMessages = async () => {
    try {
      const data = await chatService.getMessages(activeSessionId)
      setMessages(activeSessionId, data.messages)
    } catch {
      // ignore
    }
  }

  const connectWS = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return wsRef.current

    const ws = chatService.connectWebSocket(activeSessionId)
    wsRef.current = ws

    ws.onclose = () => {
      wsRef.current = null
    }

    ws.onerror = () => {
      wsRef.current = null
    }

    return ws
  }, [activeSessionId])

  const handleSend = useCallback(async (text) => {
    if (!activeSessionId || isStreaming) return

    // Kullanıcı mesajını ekle
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    }
    addMessage(activeSessionId, userMsg)
    setStreaming(true)
    setStreamingMessage({ role: 'assistant', content: '', sources: [] })

    const ws = connectWS()

    const waitForOpen = () =>
      new Promise((resolve, reject) => {
        if (ws.readyState === WebSocket.OPEN) return resolve()
        ws.onopen = () => resolve()
        ws.onerror = () => reject(new Error('WebSocket bağlantı hatası'))
        setTimeout(() => reject(new Error('WebSocket timeout')), 5000)
      })

    try {
      await waitForOpen()

      let fullContent = ''
      let sources = []

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === 'token') {
          fullContent += data.content
          setStreamingMessage((prev) => ({
            ...prev,
            content: fullContent,
          }))
        } else if (data.type === 'sources') {
          sources = data.sources || []
          setStreamingMessage((prev) => ({
            ...prev,
            sources,
          }))
        } else if (data.type === 'done') {
          const assistantMsg = {
            id: data.message_id || Date.now() + 1,
            role: 'assistant',
            content: fullContent,
            sources,
            latency_ms: data.latency_ms,
            created_at: new Date().toISOString(),
          }
          addMessage(activeSessionId, assistantMsg)
          setStreamingMessage(null)
          setStreaming(false)
        } else if (data.type === 'error') {
          setStreamingMessage(null)
          setStreaming(false)
        }
      }

      ws.send(JSON.stringify({ content: text, model: selectedModel }))
    } catch {
      setStreamingMessage(null)
      setStreaming(false)
    }
  }, [activeSessionId, isStreaming, selectedModel, connectWS, addMessage, setStreaming])

  if (!activeSessionId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-dark-900">
        <div className="text-center text-slate-500">
          <p className="text-lg font-medium">Bir sohbet seçin veya yeni sohbet başlatın</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-dark-900 overflow-hidden">
      <MessageList messages={sessionMessages} streamingMessage={streamingMessage} />
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  )
}
