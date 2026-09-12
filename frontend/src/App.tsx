import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { ApplicationsPage } from "./pages/Applications";
import { DashboardPage } from "./pages/Dashboard";
import { InterviewPage } from "./pages/Interview";
import { JobDetailPage } from "./pages/JobDetail";
import { JobFormPage } from "./pages/JobForm";
import { JobsPage } from "./pages/Jobs";
import { LoginPage } from "./pages/Login";
import { RegisterPage } from "./pages/Register";
import { ResumePage } from "./pages/Resume";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<Layout />}>
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/jobs"
            element={
              <ProtectedRoute>
                <JobsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/jobs/new"
            element={
              <ProtectedRoute allowedRoles={["recruiter", "admin"]}>
                <JobFormPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/jobs/:id"
            element={
              <ProtectedRoute>
                <JobDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/resume"
            element={
              <ProtectedRoute allowedRoles={["candidate"]}>
                <ResumePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/applications"
            element={
              <ProtectedRoute>
                <ApplicationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/applications/:applicationId/interview"
            element={
              <ProtectedRoute allowedRoles={["candidate"]}>
                <InterviewPage />
              </ProtectedRoute>
            }
          />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
