import { useState } from 'react'

import { login as loginRequest, logout as logoutRequest, register as registerRequest } from '../services/authService'
import { AuthContext } from './AuthContextValue'

const validRoles = new Set(['resident', 'worker', 'admin'])
const initialSession = { user: null, isAuthenticated: false, role: null, loading: false }

export function AuthProvider({ children }) {
  const [session, setSession] = useState(initialSession)

  const login = async (credentials) => {
    setSession((current) => ({ ...current, loading: true }))

    try {
      const result = await loginRequest(credentials)
      setSession({ ...initialSession, isAuthenticated: true })
      return result
    } catch (error) {
      setSession((current) => ({ ...current, loading: false }))
      throw error
    }
  }

  const register = async (details) => {
    setSession((current) => ({ ...current, loading: true }))

    try {
      return await registerRequest(details)
    } finally {
      setSession((current) => ({ ...current, loading: false }))
    }
  }

  const logout = async () => {
    setSession((current) => ({ ...current, user: null, isAuthenticated: false, role: null, loading: true }))

    try {
      await logoutRequest()
      return true
    } catch {
      return false
    } finally {
      setSession((current) => ({ ...current, loading: false }))
    }
  }

  const setRole = (role) => {
    if (!validRoles.has(role)) {
      throw new Error('Unsupported account role.')
    }

    setSession((current) => current.isAuthenticated ? { ...current, role } : current)
  }

  return (
    <AuthContext.Provider value={{ ...session, login, register, logout, setRole }}>
      {children}
    </AuthContext.Provider>
  )
}