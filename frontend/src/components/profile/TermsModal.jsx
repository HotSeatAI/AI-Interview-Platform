import { TERMS_LAST_UPDATED, TERMS_SECTIONS } from "../../constants/termsContent";

function TermsModal({ onAccept, onDecline, submitting, error }) {
  return (
    <div className="delivery-consent-overlay">
      <div className="delivery-consent-card terms-modal-card">
        <h2>Terms &amp; Conditions</h2>
        <p className="terms-modal-updated">Last updated: {TERMS_LAST_UPDATED}</p>

        <div className="terms-modal-body">
          {TERMS_SECTIONS.map((section) => (
            <div className="terms-modal-section" key={section.heading}>
              <h3>{section.heading}</h3>
              <p>{section.body}</p>
            </div>
          ))}
        </div>

        <p className="terms-modal-prompt">
          You must accept these Terms &amp; Conditions to continue using Hot Seat.
        </p>

        {error && <p className="error-text">{error}</p>}

        <div className="delivery-consent-actions">
          <button
            type="button"
            className="button button--secondary"
            onClick={onDecline}
            disabled={submitting}
          >
            Decline
          </button>

          <button
            type="button"
            className="button button--primary"
            onClick={onAccept}
            disabled={submitting}
          >
            {submitting ? "Saving…" : "I Accept"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default TermsModal;
