import { useState } from "react";

const STARS = [1, 2, 3, 4, 5];

function SessionFeedbackForm({ onSubmit, onSkip }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (rating === 0) {
      setError("Please select a rating.");
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      await onSubmit({ rating, feedback_text: feedbackText.trim() || null });
    } catch (err) {
      setError(
        err?.response?.data?.detail || "Failed to submit feedback. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="session-feedback-card" onSubmit={handleSubmit}>
      <div className="eyebrow">HOW WAS THIS INTERVIEW?</div>
      <h2 className="session-feedback-card__headline">Rate your experience</h2>

      <div className="session-feedback-stars">
        {STARS.map((value) => (
          <button
            key={value}
            type="button"
            className={`session-feedback-star ${
              value <= (hoverRating || rating) ? "session-feedback-star--filled" : ""
            }`}
            onMouseEnter={() => setHoverRating(value)}
            onMouseLeave={() => setHoverRating(0)}
            onClick={() => setRating(value)}
            aria-label={`Rate ${value} out of 5`}
          >
            ★
          </button>
        ))}
      </div>

      <div className="form-field">
        <span>Anything you&apos;d like to share? (optional)</span>
        <textarea
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          placeholder="What worked well, what didn't, what you'd like to see..."
        />
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="session-feedback-card__actions">
        <button type="submit" className="button button--primary" disabled={submitting}>
          {submitting ? "Submitting..." : "Submit feedback"}
        </button>

        {onSkip && (
          <button
            type="button"
            className="button button--secondary"
            onClick={onSkip}
            disabled={submitting}
          >
            Skip and exit
          </button>
        )}
      </div>
    </form>
  );
}

export default SessionFeedbackForm;
