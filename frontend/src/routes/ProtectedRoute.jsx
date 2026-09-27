import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children, redirectTo = '/login' }) {
  const isAuthenticated = false

  // Replace this placeholder with real auth state/context in the next phase.
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />
  }

  return children
}
