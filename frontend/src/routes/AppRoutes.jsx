import { Navigate, Outlet, Route, Routes } from 'react-router-dom'

import AppLayout from '../components/layout/AppLayout'
import LoginPage from '../pages/auth/LoginPage'
import RegisterPage from '../pages/auth/RegisterPage'
import AdminPage from '../pages/admin/AdminPage'
import AdminIssuesPage from '../pages/admin/AdminIssuesPage'
import AdminIssueDetailsPage from '../pages/admin/AdminIssueDetailsPage'
import AdminWorkersPage from '../pages/admin/AdminWorkersPage'
import AdminWorkerDetailsPage from '../pages/admin/AdminWorkerDetailsPage'
import AdminUsersPage from '../pages/admin/AdminUsersPage'
import AdminUserDetailsPage from '../pages/admin/AdminUserDetailsPage'
import AdminNotFoundPage from '../pages/admin/AdminNotFoundPage'
import DiagnosticsPage from '../pages/DiagnosticsPage'
import ResidentPage from '../pages/resident/ResidentPage'
import ReportProblemPage from '../pages/resident/ReportProblemPage'
import MyProblemsPage from '../pages/resident/MyProblemsPage'
import ProblemDetailsPage from '../pages/resident/ProblemDetailsPage'
import WorkerPage from '../pages/worker/WorkerPage'
import MyJobsPage from '../pages/worker/MyJobsPage'
import WorkerAvailabilityPage from '../pages/worker/WorkerAvailabilityPage'
import JobDetailsPage from '../pages/worker/JobDetailsPage'
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
              <Outlet />
            </AppLayout>
          </ProtectedRoute>
        }
      >
        <Route index element={<WorkerPage />} />
        <Route path="jobs" element={<MyJobsPage />} />
        <Route path="jobs/:jobId" element={<JobDetailsPage />} />
        <Route path="availability" element={<WorkerAvailabilityPage />} />
      </Route>
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AppLayout><Outlet /></AppLayout>
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminPage />} />
        <Route path="issues" element={<AdminIssuesPage />} />
        <Route path="issues/:issueId" element={<AdminIssueDetailsPage />} />
        <Route path="workers" element={<AdminWorkersPage />} />
        <Route path="workers/:workerId" element={<AdminWorkerDetailsPage />} />
        <Route path="users" element={<AdminUsersPage />} />
        <Route path="users/:userId" element={<AdminUserDetailsPage />} />
        <Route path="*" element={<AdminNotFoundPage />} />
      </Route>
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
