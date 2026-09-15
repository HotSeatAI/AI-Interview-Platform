import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardPage from "./pages/DashboardPage";
import ResumePage from "./pages/ResumePage";
import ResumeAnalysisPage from "./pages/ResumeAnalysisPage";
import GenerateInterviewPage from "./pages/GenerateInterviewPage";
import InterviewSessionPage from "./pages/InterviewSessionPage";
import HistoryPage from "./pages/HistoryPage";
import SessionResultsPage from "./pages/SessionResultsPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import TopicsPage from "./pages/TopicsPage";
import CompleteProfilePage from "./pages/CompleteProfilePage";
import SettingsPage from "./pages/SettingsPage";
import ConfirmEmailChangePage from "./pages/ConfirmEmailChangePage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        index: true,
        element: <LandingPage />,
      },

      {
        path: "login",
        element: <LoginPage />,
      },

      {
        path: "signup",
        element: <SignupPage />,
      },

      // Public route
      {
        path: "verify-email",
        element: <VerifyEmailPage />,
      },

      {
        path: "forgot-password",
        element: <ForgotPasswordPage />,
      },

      {
        path: "reset-password",
        element: <ResetPasswordPage />,
      },

      // Public route - the confirm link may be opened from a
      // different session/device than the one that requested the
      // change, so this must not require an active login.
      {
        path: "confirm-email-change",
        element: <ConfirmEmailChangePage />,
      },

      {
        path: "complete-profile",
        element: (
          <ProtectedRoute>
            <CompleteProfilePage />
          </ProtectedRoute>
        ),
      },

      {
        path: "dashboard",
        element: (
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "resume",
        element: (
          <ProtectedRoute>
            <ResumePage />
          </ProtectedRoute>
        ),
      },

      {
        path: "resume-analysis/:analysisId",
        element: (
          <ProtectedRoute>
            <ResumeAnalysisPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "generate-interview",
        element: (
          <ProtectedRoute>
            <GenerateInterviewPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "interview/:sessionId",
        element: (
          <ProtectedRoute>
            <InterviewSessionPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "history",
        element: (
          <ProtectedRoute>
            <HistoryPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "results/:sessionId",
        element: (
          <ProtectedRoute>
            <SessionResultsPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "topics",
        element: (
          <ProtectedRoute>
            <TopicsPage />
          </ProtectedRoute>
        ),
      },

      {
        path: "settings",
        element: (
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

export default router;