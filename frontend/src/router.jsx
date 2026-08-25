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
    ],
  },
]);

export default router;