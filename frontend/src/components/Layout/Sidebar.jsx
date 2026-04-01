import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, FileText, Plus, Trash2, Bot, LogOut } from 'lucide-react'
import { useChatStore } from '../../stores/chatStore'
import { chatService } from '../../services/chatService'
import { useAuth } from '../../hooks/useAuth'
import { formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'
import clsx from 'clsx'
import toast from 'react-hot-toast'

export default function Sidebar() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { sessions, activeSessionId, setSessions, addSession, removeSession, setActiveSession } = useChatStore()

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const data = await chatService.getSessions()
      setSessions(data.sessions)
    } catch {
      // ignore
    }
  }

  const handleNewChat = async () => {
    try {
      const session = await chatService.createSession('Yeni Sohbet')
      addSession(session)
      setActiveSession(session.id)
      navigate('/')
    } catch {
      toast.error('Sohbet oluşturulamadı')
    }
  }

  const handleDeleteSession = async (e, sessionId) => {
    e.stopPropagation()
    try {
      await chatService.deleteSession(sessionId)
      removeSession(sessionId)
      toast.success('Sohbet silindi')
    } catch {
      toast.error('Sohbet silinemedi')
    }
  }

  const handleSelectSession = (sessionId) => {
    setActiveSession(sessionId)
    navigate('/')
  }

  return (
    <aside className="w-72 h-screen bg-dark-950 border-r border-slate-800 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center">
            <Bot size={20} />
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-100">AI Asistan</h1>
            <p className="text-xs text-slate-500">RAG Platform</p>
          </div>
        </div>
        <button onClick={handleNewChat} className="btn-primary w-full flex items-center justify-center gap-2 text-sm">
          <Plus size={16} />
          Yeni Sohbet
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-3 space-y-1">
        <button onClick={() => navigate('/')} className={clsx('sidebar-item w-full', !activeSessionId && 'sidebar-item-active')}>
          <MessageSquare size={18} />
          <span className="text-sm">Sohbet</span>
        </button>
        <button onClick={() => navigate('/documents')} className="sidebar-item w-full">
          <FileText size={18} />
          <span className="text-sm">Dokümanlar</span>
        </button>
      </nav>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        <p className="text-xs text-slate-600 uppercase tracking-wider mb-2 px-2">Sohbet Geçmişi</p>
        <div className="space-y-0.5">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => handleSelectSession(session.id)}
              className={clsx(
                'group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm transition-all',
                activeSessionId === session.id
                  ? 'bg-dark-700 text-slate-100'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-dark-800'
              )}
            >
              <MessageSquare size={14} className="shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="truncate">{session.title}</p>
                <p className="text-xs text-slate-600">
                  {formatDistanceToNow(new Date(session.created_at), { addSuffix: true, locale: tr })}
                </p>
              </div>
              <button
                onClick={(e) => handleDeleteSession(e, session.id)}
                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* User Info */}
      <div className="p-3 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 bg-dark-700 rounded-full flex items-center justify-center text-xs font-bold text-primary-500">
              {user?.username?.charAt(0).toUpperCase() || '?'}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate text-slate-200">{user?.username}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button onClick={logout} className="text-slate-500 hover:text-red-400 transition-colors" title="Çıkış Yap">
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  )
}
