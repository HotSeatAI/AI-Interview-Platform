import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getDashboard } from "../api/dashboardApi";
import { getMyBillingStatus } from "../api/billingApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";

function DashboardPage() {
  const { token } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [dashboardData, billingData] = await Promise.all([
          getDashboard(token),
          getMyBillingStatus(token),
        ]);
        setDashboard(dashboardData);
        setBilling(billingData);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load dashboard."
        );
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDashboard();
    }
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

      <main className="dashboard-container">
        <div className="dashboard-header">
          <div className="eyebrow">DASHBOARD</div>
          <h1 className="dashboard-greeting">Welcome back, {dashboard.username}</h1>
          <p className="dashboard-email">{dashboard.email}</p>
        </div>

        {billing && (
          <div className="usage-banner">
            <span className="usage-banner__plan">
              {billing.plan.toUpperCase()} PLAN
            </span>
            <span className="usage-banner__stat">
              {billing.interviews_used}/{billing.interviews_limit}{" "}
              interviews used
            </span>
            <span className="usage-banner__stat">
              {billing.tailorings_used}/{billing.tailorings_limit}{" "}
              resume tailorings used
            </span>
            <Link to="/pricing" className="usage-banner__upgrade">
              {billing.plan === "max" ? "Manage plan" : "Upgrade →"}
            </Link>
          </div>
        )}

        <div className="stats-strip">
          <div className="stats-strip__cell">
            <div className="stats-strip__value">{dashboard.total_interviews}</div>
            <div className="stats-strip__label">TOTAL INTERVIEWS</div>
          </div>
          <div className="stats-strip__divider" />
          <div className="stats-strip__cell">
            <div className="stats-strip__value">{dashboard.completed_interviews}</div>
            <div className="stats-strip__label">COMPLETED</div>
          </div>
          <div className="stats-strip__divider" />
          <div className="stats-strip__cell">
            <div className="stats-strip__value">{dashboard.in_progress_interviews}</div>
            <div className="stats-strip__label">IN PROGRESS</div>
          </div>
          <div className="stats-strip__divider" />
          <div className="stats-strip__cell stats-strip__cell--wide">
            <div className="stats-strip__value stats-strip__value--small">
              {dashboard.latest_resume ?? "No resume uploaded"}
            </div>
            <div className="stats-strip__label">LATEST RESUME</div>
          </div>
        </div>

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
              <Link to="/history" className="button button--secondary">
                View in history
              </Link>
            </div>
          ) : (
            <div className="dashboard-latest__card">
              <p className="dashboard-latest__empty">
                No interviews yet — start your first session to see it here.
              </p>
              <Link to="/generate-interview" className="button button--primary">
                Generate an interview
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
