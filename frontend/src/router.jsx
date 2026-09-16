/* eslint-disable react-refresh/only-export-components --
   this file's default export is the router, not a component; the
   React.lazy() bindings below are route-table entries, not exports. */
import { lazy } from "react";
import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ResumePage = lazy(() => import("./pages/ResumePage"));
const ResumeAnalysisPage = lazy(() => import("./pages/ResumeAnalysisPage"));
const GenerateInterviewPage = lazy(() => import("./pages/GenerateInterviewPage"));
const InterviewSessionPage = lazy(() => import("./pages/InterviewSessionPage"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));
const SessionResultsPage = lazy(() => import("./pages/SessionResultsPage"));
const VerifyEmailPage = lazy(() => import("./pages/VerifyEmailPage"));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("./pages/ResetPasswordPage"));
const TopicsPage = lazy(() => import("./pages/TopicsPage"));
const CompleteProfilePage = lazy(() => import("./pages/CompleteProfilePage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const ConfirmEmailChangePage = lazy(() => import("./pages/ConfirmEmailChangePage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const PrivacyPolicyPage = lazy(() => import("./pages/PrivacyPolicyPage"));

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

      {
        path: "privacy",
        element: <PrivacyPolicyPage />,
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

      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);

export default router;
