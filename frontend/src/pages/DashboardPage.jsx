import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getDashboard } from "../api/dashboardApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";
import PageHeader from "../components/layout/PageHeader.jsx";
import ActivityHeatmap from "../components/dashboard/ActivityHeatmap.jsx";
import Button from "../components/ui/Button.jsx";
import usePageMeta from "../hooks/usePageMeta";

function DashboardPage() {
  usePageMeta("Dashboard", "View your interview activity, stats, and progress on HotSeat.");

  const { token } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const dashboardData = await getDashboard(token);
        setDashboard(dashboardData);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load dashboard."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [token]);

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="page-loading">Loading dashboard…</div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="page-error">{error}</div>
      </>
    );
  }

  const latestInterview = dashboard.latest_interview;

  return (
    <div className="dashboard-page">
      <Navbar />

      <PageHeader
        eyebrow="DASHBOARD"
        title={`Welcome back, ${dashboard.username}`}
        subtitle={dashboard.email}
        stats={[
          { value: dashboard.total_interviews, label: "TOTAL INTERVIEWS" },
          { value: dashboard.completed_interviews, label: "COMPLETED" },
          { value: dashboard.in_progress_interviews, label: "IN PROGRESS", accent: true },
        ]}
      />

      <main className="dashboard-container">
        <ActivityHeatmap activity={dashboard.activity} />

        <div className="dashboard-grid">
          <Link to="/generate-interview" className="dashboard-cta-card">
            <div className="eyebrow">READY WHEN YOU ARE</div>
            <h2>Start your next interview</h2>
            <p>
              Configure a role and difficulty, and HotSeat will build a session around
              your latest resume.
            </p>
            <span className="dashboard-cta-card__button">Enter the HotSeat</span>
          </Link>

          <div className="dashboard-side-col">
            <Link to="/resume" className="dashboard-side-card">
              <div className="dashboard-side-card__label">RESUME</div>
              <div className="dashboard-side-card__title">
                {dashboard.latest_resume ?? "No resume yet"}
              </div>
              <div className="dashboard-side-card__meta">Manage resumes &amp; JD match →</div>
            </Link>
            <Link to="/history" className="dashboard-side-card">
              <div className="dashboard-side-card__label">HISTORY</div>
              <div className="dashboard-side-card__title">
                {dashboard.total_interviews} past sessions
              </div>
              <div className="dashboard-side-card__meta">Review scores &amp; feedback →</div>
            </Link>
            <Link to="/topics" className="dashboard-side-card">
              <div className="dashboard-side-card__label">STUDY PLAN</div>
              <div className="dashboard-side-card__title">Weak topics</div>
              <div className="dashboard-side-card__meta">Practice and track progress →</div>
            </Link>
          </div>
        </div>

        <div className="dashboard-latest">
          <div className="eyebrow">MOST RECENT SESSION</div>
          {latestInterview ? (
            <div className="dashboard-latest__card">
              <div className="dashboard-latest__info">
                <h3 className="dashboard-latest__role">{latestInterview.role}</h3>
                <div className="dashboard-latest__meta-row">
                  <span className="difficulty-pill">{latestInterview.difficulty}</span>
                  <span className="dashboard-latest__date">
                    {new Date(latestInterview.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
              <Button to="/history" variant="secondary">
                View in history
              </Button>
            </div>
          ) : (
            <div className="dashboard-latest__card">
              <p className="dashboard-latest__empty">
                No interviews yet — start your first session to see it here.
              </p>
              <Button to="/generate-interview">Generate an interview</Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
