import Header from '../components/Layout/Header'
import DocumentUpload from '../components/Documents/DocumentUpload'
import DocumentList from '../components/Documents/DocumentList'
import { useDocuments } from '../hooks/useDocuments'
import { FileText, Loader2 } from 'lucide-react'

export default function DocumentsPage() {
  const { documents, totalDocs, isLoading, upload, isUploading, remove, isDeleting } = useDocuments()

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header title="Dokümanlar" />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Stats */}
          <div className="flex items-center gap-4">
            <div className="card flex items-center gap-3 flex-1">
              <div className="w-10 h-10 bg-primary-600/10 rounded-lg flex items-center justify-center">
                <FileText size={20} className="text-primary-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-100">{totalDocs}</p>
                <p className="text-xs text-slate-500">Toplam Doküman</p>
              </div>
            </div>
            <div className="card flex items-center gap-3 flex-1">
              <div className="w-10 h-10 bg-emerald-600/10 rounded-lg flex items-center justify-center">
                <FileText size={20} className="text-emerald-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-100">
                  {documents.filter((d) => d.status === 'ready').length}
                </p>
                <p className="text-xs text-slate-500">Hazır</p>
              </div>
            </div>
          </div>

          {/* Upload */}
          <DocumentUpload onUpload={upload} isUploading={isUploading} />

          {/* List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="text-primary-500 animate-spin" />
            </div>
          ) : (
            <DocumentList documents={documents} onDelete={remove} isDeleting={isDeleting} />
          )}
        </div>
      </div>
    </div>
  )
}
