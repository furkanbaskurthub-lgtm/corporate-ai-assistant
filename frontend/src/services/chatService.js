import api from './api'
import { useAuthStore } from '../stores/authStore'

export const chatService = {
  async createSession(title) {
    const response = await api.post('/chat/sessions', { title })
    return response.data
  },

  async getSessions() {
    const response = await api.get('/chat/sessions')
    return response.data
  },

  async getMessages(sessionId) {
    const response = await api.get(`/chat/sessions/${sessionId}/messages`)
    return response.data
  },

  async deleteSession(sessionId) {
    await api.delete(`/chat/sessions/${sessionId}`)
  },

  connectWebSocket(sessionId) {
    const token = useAuthStore.getState().token
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/api/v1/chat/ws/${sessionId}?token=${token}`
    return new WebSocket(url)
  },
}
