import { useEffect, useState } from "react";

import { getAvailableInterviewers, bookSlot, getMyBookings, cancelBooking } from "../api/bookingApi";
import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";
import PageHeader from "../components/layout/PageHeader.jsx";
import usePageMeta from "../hooks/usePageMeta";
import BookingFilters from "../components/booking/BookingFilters";
import InterviewerList from "../components/booking/InterviewerList";
import BookingConfirmModal from "../components/booking/BookingConfirmModal";
import MyBookingsList from "../components/booking/MyBookingsList";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

const TABS = [
  { value: "find", label: "Find a slot" },
  { value: "mine", label: "My bookings" },
];

function SlotBookingPage() {
  usePageMeta("Book a Mock Interview", "Find a peer interviewer by domain and book a free practice slot.");

  const { token } = useAuth();

  const [tab, setTab] = useState("find");

  const [filters, setFilters] = useState({
    domain: "",
    subDomain: "",
    fromDate: todayIso(),
    toDate: "",
    timeOfDay: "any",
  });

  const [interviewers, setInterviewers] = useState([]);
  const [loadingInterviewers, setLoadingInterviewers] = useState(false);
  const [interviewersError, setInterviewersError] = useState("");

  const [bookings, setBookings] = useState([]);
  const [loadingBookings, setLoadingBookings] = useState(false);
  const [bookingsError, setBookingsError] = useState("");
  const [cancellingId, setCancellingId] = useState("");

  const [pendingBooking, setPendingBooking] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [bookingError, setBookingError] = useState("");

  useEffect(() => {
    if (!filters.domain) {
      return;
    }

    let cancelled = false;

    getAvailableInterviewers(filters, token)
      .then((data) => {
        if (cancelled) return;
        setInterviewers(data);
        setInterviewersError("");
        setLoadingInterviewers(false);
      })
      .catch(() => {
        if (cancelled) return;
        setInterviewersError("Failed to load interviewers.");
        setLoadingInterviewers(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filters, token]);

  useEffect(() => {
    if (tab !== "mine") {
      return;
    }

    let cancelled = false;

    getMyBookings(token)
      .then((data) => {
        if (cancelled) return;
        setBookings(data);
        setBookingsError("");
        setLoadingBookings(false);
      })
      .catch(() => {
        if (cancelled) return;
        setBookingsError("Failed to load your bookings.");
        setLoadingBookings(false);
      });

    return () => {
      cancelled = true;
    };
  }, [tab, token]);

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    if (newFilters.domain) {
      setLoadingInterviewers(true);
    }
  };

  const handleTabChange = (value) => {
    setTab(value);
    if (value === "mine") {
      setLoadingBookings(true);
    }
  };

  const handleRequestBook = (interviewer, slot) => {
    setBookingError("");
    setPendingBooking({ interviewer, slot });
  };

  const handleConfirmBooking = async () => {
    if (!pendingBooking) return;

    try {
      setSubmitting(true);
      setBookingError("");

      await bookSlot(
        { interviewerId: pendingBooking.interviewer.id, slotId: pendingBooking.slot.id },
        token
      );

      setInterviewers((prev) =>
        prev
          .map((interviewer) =>
            interviewer.id === pendingBooking.interviewer.id
              ? { ...interviewer, slots: interviewer.slots.filter((slot) => slot.id !== pendingBooking.slot.id) }
              : interviewer
          )
          .filter((interviewer) => interviewer.slots.length > 0)
      );

      setPendingBooking(null);
    } catch (err) {
      setBookingError(err?.message || "Failed to book this slot.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelBooking = async (bookingId) => {
    try {
      setCancellingId(bookingId);
      await cancelBooking(bookingId, token);
      setBookings((prev) => prev.filter((booking) => booking.id !== bookingId));
    } catch {
      setBookingsError("Failed to cancel this booking.");
    } finally {
      setCancellingId("");
    }
  };

  return (
    <div className="booking-page">
      <Navbar />

      <PageHeader
        eyebrow="BOOK MOCK INTERVIEW"
        title="Book a mock interview"
        subtitle="Pick a domain, find an available interviewer, and lock in a slot."
        right={
          <div className="segmented-control">
            {TABS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`segmented-control__option ${
                  tab === option.value ? "segmented-control__option--active" : ""
                }`}
                onClick={() => handleTabChange(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        }
      />

      <main className="booking-container">
        {tab === "find" ? (
          <>
            <BookingFilters filters={filters} onChange={handleFiltersChange} />
            <InterviewerList
              interviewers={interviewers}
              loading={loadingInterviewers}
              error={interviewersError}
              hasSearched={Boolean(filters.domain)}
              onRequestBook={handleRequestBook}
            />
          </>
        ) : (
          <MyBookingsList
            bookings={bookings}
            loading={loadingBookings}
            error={bookingsError}
            onCancel={handleCancelBooking}
            cancellingId={cancellingId}
          />
        )}
      </main>

      {pendingBooking && (
        <BookingConfirmModal
          interviewer={pendingBooking.interviewer}
          slot={pendingBooking.slot}
          submitting={submitting}
          error={bookingError}
          onConfirm={handleConfirmBooking}
          onDismiss={() => setPendingBooking(null)}
        />
      )}
    </div>
  );
}

export default SlotBookingPage;
