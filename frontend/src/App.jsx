import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import TaskPage from './pages/TaskPage';
import Dashboard from './pages/Dashboard';
import CandidateList from './pages/CandidateList';
import CandidateReport from './pages/CandidateReport';
import SessionReplay from './pages/SessionReplay';
import TaskAnalytics from './pages/TaskAnalytics';
import PilotLanding from './pages/PilotLanding';
import PilotFeedback from './pages/PilotFeedback';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Pilot (public) */}
      <Route path="/pilot" element={<PilotLanding />} />
      <Route path="/pilot/feedback" element={<PilotFeedback />} />

      {/* Candidate assessment (public — candidates use a link) */}
      <Route path="/assess" element={<TaskPage />} />

      {/* Protected hiring dashboard */}
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/dashboard/candidates" element={<ProtectedRoute><CandidateList /></ProtectedRoute>} />
      <Route path="/dashboard/candidate/:candidateId" element={<ProtectedRoute><CandidateReport /></ProtectedRoute>} />
      <Route path="/dashboard/candidate/:candidateId/session/:taskRunId" element={<ProtectedRoute><SessionReplay /></ProtectedRoute>} />
      <Route path="/dashboard/candidate/:candidateId/analytics" element={<ProtectedRoute><TaskAnalytics /></ProtectedRoute>} />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/pilot" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
