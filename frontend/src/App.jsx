import { Navigate, Route, Routes } from 'react-router-dom';

import { useAuth } from './context/useAuth.js';
import AssessmentPage from './pages/AssessmentPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import LoginPage from './pages/LoginPage.jsx';

function ProtectedRoute({ allowedRoles, children }) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={user.role === 'candidate' ? '/assessment' : '/dashboard'} replace />;
  }
  return children;
}

export default function App() {
  const { isAuthenticated, user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to={user.role === 'candidate' ? '/assessment' : '/dashboard'} replace />
          ) : (
            <LoginPage />
          )
        }
      />
      <Route
        path="/assessment"
        element={
          <ProtectedRoute allowedRoles={['candidate']}>
            <AssessmentPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute allowedRoles={['admin', 'reviewer']}>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/"
        element={
          <Navigate
            to={isAuthenticated ? (user.role === 'candidate' ? '/assessment' : '/dashboard') : '/login'}
            replace
          />
        }
      />
    </Routes>
  );
}
