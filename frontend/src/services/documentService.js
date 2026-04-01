import api from './api'

export const documentService = {
  async upload(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    })
    return response.data
  },

  async getAll() {
    const response = await api.get('/documents/')
    return response.data
  },

  async remove(docId) {
    const response = await api.delete(`/documents/${docId}`)
    return response.data
  },
}
