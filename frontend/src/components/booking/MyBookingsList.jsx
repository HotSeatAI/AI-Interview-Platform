import { getDomainLabel, getSubDomainLabel } from "../../constants/interviewDomains";
import { formatSlotLabel } from "../../utils/formatSlot";

function MyBookingsList({ bookings, loading, error, onCancel, cancellingId }) {
  if (loading) {
    return <p className="form-hint">Loading your bookings...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (bookings.length === 0) {
    return <p className="empty-state">You haven't booked any mock interviews yet.</p>;
  }

  return (
    <div className="list-row-group">
      {bookings.map((booking) => (
        <article key={booking.id} className="list-row">
          <div className="list-row__info">
            <div className="list-row__title">{booking.interviewer_name}</div>
            <div className="list-row__meta">
              <span className="badge badge--info">{getDomainLabel(booking.domain)}</span>
              {booking.sub_domains.map((subDomain) => (
                <span key={subDomain} className="badge badge--neutral">
                  {getSubDomainLabel(booking.domain, subDomain)}
                </span>
              ))}
              <span>{formatSlotLabel(booking.slot)}</span>
            </div>
          </div>

          <div className="list-row__actions">
            <button
              type="button"
              className="button button--secondary button--sm"
              disabled={cancellingId === booking.id}
              onClick={() => onCancel(booking.id)}
            >
              {cancellingId === booking.id ? "Cancelling..." : "Cancel booking"}
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}

export default MyBookingsList;
