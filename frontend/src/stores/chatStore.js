import { create } from 'zustand'

export const useChatStore = create((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: {},
  isStreaming: false,
  streamingContent: '',
  selectedModel: 'gpt-3.5-turbo',

  setSessions: (sessions) => set({ sessions }),

  addSession: (session) =>
    set((state) => ({ sessions: [session, ...state.sessions] })),

  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
      activeSessionId: state.activeSessionId === sessionId ? null : state.activeSessionId,
    })),

  updateSessionTitle: (sessionId, title) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === sessionId ? { ...s, title } : s
      ),
    })),

  setActiveSession: (sessionId) => set({ activeSessionId: sessionId }),

  setMessages: (sessionId, messages) =>
    set((state) => ({
      messages: { ...state.messages, [sessionId]: messages },
    })),

  addMessage: (sessionId, message) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [sessionId]: [...(state.messages[sessionId] || []), message],
      },
    })),

  updateLastMessage: (sessionId, updates) =>
    set((state) => {
      const sessionMsgs = state.messages[sessionId] || []
      if (!sessionMsgs.length) return state
      const updated = [...sessionMsgs]
      updated[updated.length - 1] = { ...updated[updated.length - 1], ...updates }
      return { messages: { ...state.messages, [sessionId]: updated } }
    }),

  setStreaming: (isStreaming) => set({ isStreaming }),
  setStreamingContent: (content) => set({ streamingContent: content }),
  appendStreamingContent: (token) =>
    set((state) => ({ streamingContent: state.streamingContent + token })),
  resetStreaming: () => set({ isStreaming: false, streamingContent: '' }),

  setSelectedModel: (model) => set({ selectedModel: model }),
}))
