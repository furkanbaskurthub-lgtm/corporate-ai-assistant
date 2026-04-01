import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Bot, User, FileText, Clock, Zap } from 'lucide-react'
import clsx from 'clsx'

export default function MessageBubble({ message, isStreaming }) {
  const isUser = message.role === 'user'

  return (
    <div className={clsx('message-appear flex gap-3 px-4 py-4', isUser ? 'bg-dark-900' : 'bg-dark-800/50')}>
      {/* Avatar */}
      <div className={clsx(
        'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5',
        isUser ? 'bg-primary-600' : 'bg-emerald-600'
      )}>
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-semibold text-slate-300">
            {isUser ? 'Sen' : 'AI Asistan'}
          </span>
          {message.latency_ms && (
            <span className="flex items-center gap-1 text-xs text-slate-600">
              <Clock size={10} />
              {message.latency_ms}ms
            </span>
          )}
          {message.model_used && (
            <span className="flex items-center gap-1 text-xs text-slate-600">
              <Zap size={10} />
              {message.model_used}
            </span>
          )}
        </div>

        {/* Message Text */}
        <div className="prose-dark text-sm leading-relaxed">
          {isStreaming ? (
            <span>{message.content}<span className="typing-dots"><span>.</span><span>.</span><span>.</span></span></span>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-1.5">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Kaynaklar</p>
            {message.sources.map((source, idx) => (
              <div key={idx} className="bg-dark-900 border border-slate-700/50 rounded-lg p-2.5">
                <div className="flex items-center gap-2 mb-1">
                  <FileText size={12} className="text-primary-500" />
                  <span className="text-xs font-medium text-primary-400">{source.filename}</span>
                  {source.page && (
                    <span className="text-xs text-slate-600">Sayfa {source.page}</span>
                  )}
                  <span className="text-xs text-slate-600 ml-auto">
                    Skor: {(source.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-xs text-slate-500 line-clamp-2">{source.chunk_text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
