import { FileText, Trash2, CheckCircle, AlertCircle, Loader2, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { tr } from 'date-fns/locale'
import clsx from 'clsx'

const STATUS_CONFIG = {
  pending: { icon: Clock, color: 'text-yellow-500', bg: 'bg-yellow-500/10', label: 'Bekliyor' },
  processing: { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-500/10', label: 'İşleniyor', spin: true },
  ready: { icon: CheckCircle, color: 'text-emerald-500', bg: 'bg-emerald-500/10', label: 'Hazır' },
  failed: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-500/10', label: 'Başarısız' },
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

export default function DocumentList({ documents, onDelete, isDeleting }) {
  if (!documents.length) {
    return (
      <div className="text-center py-12">
        <FileText size={48} className="text-slate-700 mx-auto mb-3" />
        <p className="text-slate-500">Henüz doküman yüklenmedi</p>
        <p className="text-xs text-slate-600 mt-1">Yukarıdan dosya yükleyerek başlayın</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => {
        const status = STATUS_CONFIG[doc.status] || STATUS_CONFIG.pending
        const StatusIcon = status.icon

        return (
          <div key={doc.id} className="card flex items-center gap-4 hover:border-slate-600 transition-colors">
            {/* Icon */}
            <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', status.bg)}>
              <StatusIcon size={20} className={clsx(status.color, status.spin && 'animate-spin')} />
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate">{doc.original_filename}</p>
              <div className="flex items-center gap-3 mt-0.5">
                <span className="text-xs text-slate-500">{formatFileSize(doc.file_size)}</span>
                <span className={clsx('text-xs font-medium', status.color)}>{status.label}</span>
                {doc.chunk_count > 0 && (
                  <span className="text-xs text-slate-600">{doc.chunk_count} parça</span>
                )}
                <span className="text-xs text-slate-600">
                  {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true, locale: tr })}
                </span>
              </div>
              {doc.error_message && (
                <p className="text-xs text-red-400 mt-1 truncate">{doc.error_message}</p>
              )}
            </div>

            {/* Delete */}
            <button
              onClick={() => onDelete(doc.id)}
              disabled={isDeleting}
              className="text-slate-600 hover:text-red-400 transition-colors p-1"
              title="Sil"
            >
              <Trash2 size={16} />
            </button>
          </div>
        )
      })}
    </div>
  )
}
