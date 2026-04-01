import { Settings, Cpu } from 'lucide-react'
import { useChatStore } from '../../stores/chatStore'

const MODELS = [
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
  { id: 'gpt-4', name: 'GPT-4' },
  { id: 'gpt-4-turbo-preview', name: 'GPT-4 Turbo' },
]

export default function Header({ title }) {
  const { selectedModel, setSelectedModel } = useChatStore()

  return (
    <header className="h-14 bg-dark-900 border-b border-slate-800 flex items-center justify-between px-6">
      <h2 className="text-lg font-semibold text-slate-100">{title || 'Sohbet'}</h2>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Cpu size={16} className="text-slate-500" />
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-dark-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            {MODELS.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  )
}
