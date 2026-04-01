import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px'
    }
  }, [text])

  const handleSubmit = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="border-t border-slate-800 bg-dark-900 p-4">
      <div className="max-w-4xl mx-auto flex items-end gap-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Dokümanlarınız hakkında bir soru sorun..."
            disabled={disabled}
            rows={1}
            className="input-field resize-none pr-4 min-h-[44px] max-h-[160px]"
          />
        </div>
        <button
          onClick={handleSubmit}
          disabled={!text.trim() || disabled}
          className="btn-primary h-[44px] px-4 flex items-center justify-center shrink-0"
        >
          {disabled ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </div>
      <p className="text-xs text-slate-600 text-center mt-2">
        Enter ile gönder, Shift+Enter ile yeni satır
      </p>
    </div>
  )
}
