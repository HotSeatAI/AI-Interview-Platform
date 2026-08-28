function FeedbackCard({
  score,
  feedback,
  strengths = [],
  improvements = [],
  deliveryFeedback,
  modelAnswer,
}) {
  return (
    <article className="prev-feedback">
      <div className="prev-feedback__header">
        <div>
          <div className="eyebrow">AI EVALUATION · PREVIOUS QUESTION</div>
          <h3 className="prev-feedback__title">Answer feedback</h3>
        </div>
        <span className="prev-feedback__score">{score}/10</span>
      </div>

      <p className="prev-feedback__body">{feedback}</p>

      <div className="prev-feedback__grid">
        <div>
          <div className="prev-feedback__col-label">STRENGTHS</div>
          <ul className="prev-feedback__list">
            {strengths.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>

        <div>
          <div className="prev-feedback__col-label">IMPROVEMENTS</div>
          <ul className="prev-feedback__list">
            {improvements.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      {modelAnswer && (
        <div className="prev-feedback__model-answer">
          <div className="prev-feedback__col-label">MODEL ANSWER</div>
          <p className="prev-feedback__body">{modelAnswer}</p>
        </div>
      )}

      {deliveryFeedback && (
        <div className="prev-feedback__delivery">
          <div className="prev-feedback__col-label">DELIVERY PATTERNS</div>
          <p className="prev-feedback__body">{deliveryFeedback}</p>
        </div>
      )}
    </article>
  );
}

export default FeedbackCard;
