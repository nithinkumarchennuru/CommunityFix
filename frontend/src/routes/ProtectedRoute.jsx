import { Navigate } from 'react-router-dom'

import Loading from '../components/common/Loading'
import { useAuth } from '../context/useAuth'

export default function ProtectedRoute({ children, redirectTo = '/login' }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <Loading message="Checking your session..." />
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />
  }

  return children
}
