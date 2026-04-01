import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentService } from '../services/documentService'
import toast from 'react-hot-toast'

export function useDocuments() {
  const queryClient = useQueryClient()

  const documentsQuery = useQuery({
    queryKey: ['documents'],
    queryFn: documentService.getAll,
    refetchInterval: 5000,
  })

  const uploadMutation = useMutation({
    mutationFn: (file) => documentService.upload(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('Dosya yüklendi! İşleniyor...')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Yükleme başarısız')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (docId) => documentService.remove(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      toast.success('Doküman silindi')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Silme başarısız')
    },
  })

  return {
    documents: documentsQuery.data?.documents || [],
    totalDocs: documentsQuery.data?.total || 0,
    isLoading: documentsQuery.isLoading,
    upload: uploadMutation.mutate,
    isUploading: uploadMutation.isPending,
    remove: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
    refetch: documentsQuery.refetch,
  }
}
