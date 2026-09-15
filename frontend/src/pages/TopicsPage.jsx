import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getTopics, startTopicPractice } from "../api/topicsApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";
import PageHeader from "../components/layout/PageHeader.jsx";

function TopicsPage() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [startingId, setStartingId] = useState(null);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        setLoading(true);
        const result = await getTopics(token);
        setData(result);
      } catch (err) {
        setError(
          err?.response?.data?.detail || "Failed to load weak topics."
        );
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchTopics();
    }
  }, [token]);

  const handlePractice = async (topicId) => {
    try {
      setStartingId(topicId);
      const response = await startTopicPractice(topicId, token);
      navigate(`/interview/${response.session_id}`);
    } catch (err) {
      setError(
        err?.friendlyMessage || err?.response?.data?.detail || "Failed to start practice."
      );
      setStartingId(null);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="page-loading">Loading weak topics…</div>
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

  const progressPct = data.progress_pct;
  const circleStyle = {
    background: `conic-gradient(var(--slab-accent) ${progressPct * 3.6}deg, var(--slab-dot) 0deg)`,
  };

  return (
    <div className="topics-page">
      <Navbar />

      <PageHeader
        eyebrow="STUDY PLAN"
        title="Weak topics"
        subtitle="Practice a topic with a focused 3-question round (Easy, Medium, Medium). Score above 5 on all three to resolve it."
        right={
          <div className="page-slab__donut-row">
            <div className="page-slab__donut" style={circleStyle}>
              <div className="page-slab__donut-inner">{progressPct}%</div>
            </div>
            <div className="page-slab__donut-caption">
              Improvement suggestions completed
              <div className="form-hint" style={{ color: "var(--on-slab-faint)" }}>
                {data.resolved_total} resolved of {data.flagged_total} flagged
              </div>
            </div>
          </div>
        }
      />

      <main className="topics-container">
        {data.topics.length === 0 ? (
          <div className="form-hint">
            No weak topics right now - nice work. New ones will show up
            here after future interviews if any come up.
          </div>
        ) : (
          <div className="list-row-group">
            {data.topics.map((topic) => (
              <div className="topics-row" key={topic.id}>
                <div className="topics-row__info">
                  <div className="topics-row__name">{topic.topic}</div>
                  <div className="form-hint">
                    Flagged {topic.times_flagged}{" "}
                    {topic.times_flagged === 1 ? "time" : "times"}
                  </div>
                </div>
                <button
                  type="button"
                  className="button button--primary button--sm"
                  onClick={() => handlePractice(topic.id)}
                  disabled={startingId === topic.id}
                >
                  {startingId === topic.id ? "Starting…" : "Practice"}
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default TopicsPage;
