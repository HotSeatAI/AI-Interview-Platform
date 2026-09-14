import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { getSessionResults } from "../api/answerApi";
import { submitSessionFeedback } from "../api/interviewApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";
import PageHeader from "../components/layout/PageHeader.jsx";
import DeliveryTrend from "../components/interview/DeliveryTrend.jsx";
import SessionFeedbackForm from "../components/interview/SessionFeedbackForm.jsx";
import { ROUND_LABELS } from "../constants/interviewRounds";

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

  const handleFeedbackSubmit = async (payload) => {
    await submitSessionFeedback(sessionId, payload, token);
    setResults((prev) => ({ ...prev, ...payload }));
  };

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

  if (!results.is_finished) {
    return (
      <>
        <Navbar />
        <div className="delivery-consent-overlay delivery-consent-overlay--static">
          <div className="delivery-consent-card">
            <h2>Interview not finished yet</h2>
            <p>
              You haven&apos;t finished this interview yet. Finish the
              remaining questions, or skip ahead to the last question and
              click &quot;Finish Interview&quot;, to see your results.
            </p>
            <div className="delivery-consent-actions">
              <Link className="button button--secondary" to="/dashboard">
                Back to dashboard
              </Link>
              <Link
                className="button button--primary"
                to={`/interview/${sessionId}`}
              >
                Continue interview
              </Link>
            </div>
          </div>
        </div>
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
        deliveryFeedback: feedback.deliveryFeedback,
        deliverySignals: feedback.deliverySignals,
        modelAnswer: feedback.modelAnswer,
      };
    });

  const deliveryTrendEntries = questionBreakdown
    .filter((q) => q.deliverySignals)
    .map((q) => ({
      id: q.id,
      label: q.tagLabel,
      signals: q.deliverySignals,
    }));

  return (
    <div className="results-page">
      <Navbar />

      <PageHeader
        eyebrow="SESSION SUMMARY"
        title={`${navState.role || "Interview"}${
          navState.difficulty ? ` · ${navState.difficulty}` : ""
        }${
          navState.round && navState.round !== "full"
            ? ` · ${ROUND_LABELS[navState.round] || navState.round}`
            : ""
        }`}
        subtitle={
          navState.createdAt
            ? `Completed ${new Date(navState.createdAt).toLocaleString()}`
            : undefined
        }
        stats={[
          { value: `${results.average_score}/10`, label: "AVERAGE SCORE", accent: true },
          { value: results.questions_attempted, label: "QUESTIONS ATTEMPTED" },
        ]}
      />

      <main className="results-container">
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

        {deliveryTrendEntries.length > 1 && (
          <DeliveryTrend entries={deliveryTrendEntries} />
        )}

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
                    {q.modelAnswer && (
                      <p className="results-question-row__model-answer">
                        {q.modelAnswer}
                      </p>
                    )}
                    {q.deliveryFeedback && (
                      <p className="results-question-row__delivery">
                        {q.deliveryFeedback}
                      </p>
                    )}
                  </div>
                  <span
                    className={`results-question-row__score ${
                      q.score >= 8
                        ? "results-question-row__score--good"
                        : q.score < 5
                        ? "results-question-row__score--weak"
                        : ""
                    }`}
                  >
                    {q.score}/10
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {results.rating ? (
          <div className="session-feedback-card session-feedback-card--done">
            <p className="success-text">Thanks for your feedback!</p>
          </div>
        ) : (
          <SessionFeedbackForm onSubmit={handleFeedbackSubmit} />
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
