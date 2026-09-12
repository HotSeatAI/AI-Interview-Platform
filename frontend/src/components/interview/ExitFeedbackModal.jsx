import SessionFeedbackForm from "./SessionFeedbackForm";

function ExitFeedbackModal({ onSubmit, onSkip }) {
  return (
    <div className="delivery-consent-overlay">
      <SessionFeedbackForm onSubmit={onSubmit} onSkip={onSkip} />
    </div>
  );
}

export default ExitFeedbackModal;
