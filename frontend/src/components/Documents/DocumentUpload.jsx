import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Loader2 } from 'lucide-react'
import clsx from 'clsx'

export default function DocumentUpload({ onUpload, isUploading }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      acceptedFiles.forEach((file) => onUpload(file))
    },
    [onUpload]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt', '.log'],
    },
    maxSize: 52428800,
    disabled: isUploading,
  })

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
        isDragActive
          ? 'border-primary-500 bg-primary-500/10'
          : 'border-slate-700 hover:border-slate-500 bg-dark-800/50',
        isUploading && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        {isUploading ? (
          <Loader2 size={40} className="text-primary-500 animate-spin" />
        ) : isDragActive ? (
          <Upload size={40} className="text-primary-500" />
        ) : (
          <FileText size={40} className="text-slate-500" />
        )}
        <div>
          <p className="text-sm font-medium text-slate-300">
            {isUploading
              ? 'Yükleniyor...'
              : isDragActive
              ? 'Dosyayı buraya bırakın'
              : 'Dosya yüklemek için tıklayın veya sürükleyin'}
          </p>
          <p className="text-xs text-slate-600 mt-1">PDF, TXT, LOG - Maks 50MB</p>
        </div>
      </div>
    </div>
  )
}
