import { Navigate, Outlet, Route, Routes } from 'react-router-dom'

import AppLayout from '../components/layout/AppLayout'
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import AdminPage from '../pages/admin/AdminPage'
import DiagnosticsPage from '../pages/DiagnosticsPage'
import ResidentPage from '../pages/resident/ResidentPage'
import ReportProblemPage from '../pages/resident/ReportProblemPage'
import MyProblemsPage from '../pages/resident/MyProblemsPage'
import ProblemDetailsPage from '../pages/resident/ProblemDetailsPage'
import WorkerPage from '../pages/worker/WorkerPage'
import ProtectedRoute from './ProtectedRoute'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/resident"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Outlet />
            </AppLayout>
          </ProtectedRoute>
        }
      >
        <Route index element={<ResidentPage />} />
        <Route path="report" element={<ReportProblemPage />} />
        <Route path="problems" element={<MyProblemsPage />} />
        <Route path="problems/:problemId" element={<ProblemDetailsPage />} />
      </Route>
      <Route
        path="/worker"
        element={
          <ProtectedRoute>
            <AppLayout>
              <WorkerPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AppLayout>
              <AdminPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/diagnostics"
        element={
          <ProtectedRoute>
            <AppLayout>
              <DiagnosticsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
