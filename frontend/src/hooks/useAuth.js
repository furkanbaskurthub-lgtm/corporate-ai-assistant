import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { authService } from '../services/authService'
import toast from 'react-hot-toast'

export function useAuth() {
  const navigate = useNavigate()
  const { user, token, isAuthenticated, setToken, setAuth, logout: storeLogout } = useAuthStore()

  const login = useCallback(async (email, password) => {
    try {
      const tokenData = await authService.login(email, password)
      // Token'ı önce store'a kaydet ki getMe() Authorization header'ı gönderebilsin
      setToken(tokenData.access_token)
      const userData = await authService.getMe()
      setAuth(userData, tokenData.access_token)
      toast.success('Giriş başarılı!')
      navigate('/')
    } catch (error) {
      const msg = error.response?.data?.detail || 'Giriş başarısız'
      toast.error(msg)
      throw error
    }
  }, [setAuth, navigate])

  const register = useCallback(async (data) => {
    try {
      await authService.register(data)
      toast.success('Kayıt başarılı! Giriş yapabilirsiniz.')
      navigate('/login')
    } catch (error) {
      const msg = error.response?.data?.detail || 'Kayıt başarısız'
      toast.error(msg)
      throw error
    }
  }, [navigate])

  const logout = useCallback(() => {
    storeLogout()
    navigate('/login')
    toast.success('Çıkış yapıldı')
  }, [storeLogout, navigate])

  return { user, token, isAuthenticated, login, register, logout }
}
