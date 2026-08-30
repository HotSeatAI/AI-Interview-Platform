import { useState } from "react";

function DeliveryConsentModal({ onContinue, onDecline }) {
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [videoEnabled, setVideoEnabled] = useState(true);

  return (
    <div className="delivery-consent-overlay">
      <div className="delivery-consent-card">
        <h2>Get delivery feedback too?</h2>

        <p>
          HotSeat can analyze your microphone and camera in the background
          to give you feedback on delivery - pauses, hesitation, eye
          contact, fidgeting.
        </p>

        <p>
          <strong>Nothing is recorded or stored.</strong> Only small
          summary numbers (like a pause count or eye-contact percentage)
          ever leave your device - your audio and video never do.
        </p>

        <label className="delivery-consent-toggle">
          <input
            type="checkbox"
            checked={audioEnabled}
            onChange={(e) => setAudioEnabled(e.target.checked)}
          />
          Analyze voice delivery (pauses, pacing)
        </label>

        <label className="delivery-consent-toggle">
          <input
            type="checkbox"
            checked={videoEnabled}
            onChange={(e) => setVideoEnabled(e.target.checked)}
          />
          Analyze body language via camera (eye contact, fidgeting)
        </label>

        <div className="delivery-consent-actions">
          <button
            type="button"
            className="button button--secondary"
            onClick={onDecline}
          >
            Skip, take interview as-is
          </button>

          <button
            type="button"
            className="button button--primary"
            onClick={() => onContinue({ audioEnabled, videoEnabled })}
            disabled={!audioEnabled && !videoEnabled}
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}

export default DeliveryConsentModal;
