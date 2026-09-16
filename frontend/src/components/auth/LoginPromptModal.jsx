import Button from "../ui/Button";

function LoginPromptModal({ onDismiss }) {
  return (
    <div className="delivery-consent-overlay" onClick={onDismiss}>
      <div
        className="delivery-consent-card"
        onClick={(event) => event.stopPropagation()}
      >
        <h2>Log in to continue</h2>
        <p>You need a HotSeat account to do that.</p>

        <div className="delivery-consent-actions">
          <Button variant="secondary" onClick={onDismiss}>
            Not now
          </Button>
          <Button to="/signup" variant="secondary" onClick={onDismiss}>
            Sign up
          </Button>
          <Button to="/login" variant="primary" onClick={onDismiss}>
            Log in
          </Button>
        </div>
      </div>
    </div>
  );
}

export default LoginPromptModal;
