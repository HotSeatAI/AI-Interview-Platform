import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { getSessionResults } from "../api/answerApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";

function SessionResultsPage() {
  const { sessionId } = useParams();
  const { token } = useAuth();
  const location = useLocation();
  const navState = location.state || {};

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getSessionResults(sessionId, token);
        setResults(data);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load session results."
        );
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchResults();
    }
  }, [sessionId, token]);

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="page-loading">Loading results…</div>
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

  const questionBreakdown = (navState.questions || [])
    .filter((question) => navState.feedbackMap?.[question.id])
    .map((question, index, answeredList) => {
      const feedback = navState.feedbackMap[question.id];
      const mainNumber = answeredList
        .slice(0, index + 1)
        .filter((q) => !q.is_follow_up).length;

      return {
        id: question.id,
        tagLabel: question.is_follow_up ? `Q${mainNumber} · Follow-up` : `Q${mainNumber || index + 1}`,
        isFollowUp: question.is_follow_up,
        text: question.question_text,
        feedback: feedback.feedback,
        score: feedback.score,
      };
    });

  return (
    <div className="results-page">
      <Navbar />

      <main className="results-container">
        <div className="section-header">
          <div className="eyebrow">SESSION SUMMARY</div>
          <h1>
            {navState.role || "Interview"}
            {navState.difficulty ? ` · ${navState.difficulty}` : ""}
          </h1>
          {navState.createdAt && (
            <p>Completed {new Date(navState.createdAt).toLocaleString()}</p>
          )}
        </div>

        <div className="results-score-row">
          <div className="results-score-block">
            <div className="results-score-num">
              {results.average_score}
              <span className="results-score-outof">/10</span>
            </div>
            <div className="results-score-label">AVERAGE SCORE</div>
          </div>
          <div className="results-score-divider" />
          <div className="results-score-block">
            <div className="results-meta-num">{results.questions_attempted}</div>
            <div className="results-score-label">QUESTIONS ATTEMPTED</div>
          </div>
        </div>

        <div className="results-topics-grid">
          <div className="results-topics-col">
            <div className="results-topics-label">STRONG TOPICS</div>
            <div className="results-topic-pills">
              {results.strong_topics.length === 0 ? (
                <span className="form-hint">None yet</span>
              ) : (
                results.strong_topics.map((topic) => (
                  <span key={topic} className="topic-pill topic-pill--strong">
                    {topic}
                  </span>
                ))
              )}
            </div>
          </div>
          <div className="results-topics-col">
            <div className="results-topics-label">WEAK TOPICS</div>
            <div className="results-topic-pills">
              {results.weak_topics.length === 0 ? (
                <span className="form-hint">None yet</span>
              ) : (
                results.weak_topics.map((topic) => (
                  <span key={topic} className="topic-pill topic-pill--weak">
                    {topic}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="results-topics-col">
          <div className="results-topics-label">SKIPPED QUESTIONS</div>
          <div className="results-topic-pills">
            {results.skipped_questions.length === 0 ? (
              <span className="form-hint">No questions were skipped.</span>
            ) : (
              results.skipped_questions.map((skipped) => (
                <span
                  key={skipped.question_number}
                  className="topic-pill topic-pill--skipped"
                >
                  Question {skipped.question_number} — {skipped.topic}
                </span>
              ))
            )}
          </div>
        </div>

        {questionBreakdown.length > 0 && (
          <div className="results-questions">
            <div className="eyebrow">QUESTION-BY-QUESTION</div>
            <div className="list-row-group">
              {questionBreakdown.map((q) => (
                <div className="results-question-row" key={q.id}>
                  <div className="results-question-row__info">
                    <div className="results-question-row__tags">
                      <span
                        className={`results-question-tag ${
                          q.isFollowUp ? "results-question-tag--followup" : ""
                        }`}
                      >
                        {q.tagLabel}
                      </span>
                    </div>
                    <p className="results-question-row__text">{q.text}</p>
                    <p className="results-question-row__feedback">{q.feedback}</p>
                  </div>
                  <span className="results-question-row__score">{q.score}/10</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="results-actions">
          <Link className="button button--secondary" to="/dashboard">
            Back to dashboard
          </Link>
          <Link className="button button--primary" to="/generate-interview">
            Start a new interview
          </Link>
        </div>
      </main>
    </div>
  );
}

export default SessionResultsPage;
