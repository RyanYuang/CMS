import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AdminLayout } from '../layouts/AdminLayout'
import { AnalyticsPage } from '../pages/analytics/AnalyticsPage'
import { LoginPage } from '../pages/auth/LoginPage'
import { NotFoundPage } from '../pages/common/NotFoundPage'
import { DashboardPage } from '../pages/dashboard/DashboardPage'
import { LogsPage } from '../pages/logs/LogsPage'
import { LinksPage } from '../pages/links/LinksPage'
import { MediaPage } from '../pages/media/MediaPage'
import { MediaCategoryPage } from '../pages/media/MediaCategoryPage'
import { OrdersPage } from '../pages/orders/OrdersPage'
import { ProfilePage } from '../pages/profile/ProfilePage'
import { RolesPage } from '../pages/roles/RolesPage'
import { SettingsPage } from '../pages/settings/SettingsPage'
import { UsersPage } from '../pages/users/UsersPage'
function ProtectedRoute({ children }: { children: ReactNode }) {
  const authed = localStorage.getItem('isAuthenticated') === 'true'
  if (!authed) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="links" element={<LinksPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="media" element={<MediaPage />} />
        <Route path="media/photos" element={<MediaCategoryPage />} />
        <Route path="media/movies" element={<MediaCategoryPage />} />
        <Route path="media/music" element={<MediaCategoryPage />} />
        <Route path="media/notes" element={<MediaCategoryPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="roles" element={<RolesPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="logs" element={<LogsPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
