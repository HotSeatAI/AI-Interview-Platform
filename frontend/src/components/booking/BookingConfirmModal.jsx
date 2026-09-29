import { getDomainLabel } from "../../constants/interviewDomains";
import { formatSlotLabel } from "../../utils/formatSlot";
import Button from "../ui/Button";

function BookingConfirmModal({ interviewer, slot, submitting, error, onConfirm, onDismiss }) {
  return (
    <div className="delivery-consent-overlay" onClick={onDismiss}>
      <div className="delivery-consent-card" onClick={(event) => event.stopPropagation()}>
        <h2>Confirm your booking</h2>
        <p>
          {interviewer.name} · {getDomainLabel(interviewer.domain)}
          <br />
          {formatSlotLabel(slot)}
        </p>

        {error && <p className="error-text">{error}</p>}

        <div className="delivery-consent-actions">
          <Button variant="secondary" onClick={onDismiss} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="primary" onClick={onConfirm} disabled={submitting}>
            {submitting ? "Booking..." : "Confirm booking"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default BookingConfirmModal;
