function PreInterviewDisclaimerModal({ onAcknowledge }) {
  return (
    <div className="delivery-consent-overlay">
      <div className="delivery-consent-card">
        <h2>Before you begin</h2>

        <p>
          This interview may feel tough — that&apos;s intentional. Questions
          are designed to push you a little past your comfort zone so you
          walk away having actually learned something, not just passed a
          quiz.
        </p>

        <p>
          If a question is hard or the feedback is blunt, don&apos;t get
          discouraged. Every practice run is a chance to improve, and the
          only way to get better is to keep going.
        </p>

        <div className="delivery-consent-actions">
          <button
            type="button"
            className="button button--primary"
            onClick={onAcknowledge}
          >
            OK, let&apos;s go
          </button>
        </div>
      </div>
    </div>
  );
}

export default PreInterviewDisclaimerModal;
