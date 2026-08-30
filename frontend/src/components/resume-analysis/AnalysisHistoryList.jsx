import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getResumeAnalysisHistory } from "../../api/resumeAnalysisApi";
import useAuth from "../../hooks/useAuth";

function getStatusBadge(status) {
  switch (status) {
    case "completed":
      return { label: "Completed", tone: "positive" };
    case "failed":
      return { label: "Failed", tone: "critical" };
    default:
      return { label: "Processing", tone: "info" };
  }
}

function AnalysisHistoryItem({ analysis }) {
  const badge = getStatusBadge(analysis.status);
  const isStandalone = analysis.mode === "standalone";

  const createdDate = new Date(
    analysis.created_at
  ).toLocaleString();

  return (
    <article className="list-row">
      <div className="list-row__info">
        <div className="list-row__title">
          {isStandalone ? "ATS Check" : analysis.job_title || "Untitled role"}
        </div>
        <div className="list-row__meta">
          <span>{analysis.resume_filename || "Unknown resume"}</span>
          <span>·</span>
          <span>{createdDate}</span>
        </div>
      </div>

      <div className="list-row__actions">
        <span className={`badge badge--${badge.tone}`}>{badge.label}</span>

        {analysis.status === "completed" && (
          <>
            <span className="list-row__score">{analysis.ats_score ?? "—"}/100 ATS</span>
            {!isStandalone && (
              <span className="list-row__score">{analysis.overall_score ?? "—"}/100 Match</span>
            )}
            <Link className="button button--primary button--sm" to={`/resume-analysis/${analysis.analysis_id}`}>
              View results
            </Link>
          </>
        )}
      </div>
    </article>
  );
}

export default function AnalysisHistoryList() {
  const { token } = useAuth();

  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      return;
    }

    const fetchHistory = async () => {
      try {
        const data = await getResumeAnalysisHistory(token);
        setAnalyses(data);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load your past analyses."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  if (loading) {
    return <p className="form-hint">Loading your past analyses...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (analyses.length === 0) {
    return (
      <p className="empty-state">
        You haven't analyzed a resume against a job description yet.
      </p>
    );
  }

  return (
    <div className="list-row-group">
      {analyses.map((analysis) => (
        <AnalysisHistoryItem
          key={analysis.analysis_id}
          analysis={analysis}
        />
      ))}
    </div>
  );
}
