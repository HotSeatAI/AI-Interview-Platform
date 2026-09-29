// Mock-backed booking API. Every function's signature/shape mirrors what
// a real backend endpoint would return, so swapping these bodies for
// apiClient calls later is a one-file change - no caller elsewhere in
// the app needs to change.
import { MOCK_INTERVIEWERS } from "../mocks/interviewers";
import { getTimeOfDayBucket } from "../utils/formatSlot";
import {
  loadBookings,
  saveBookings,
  loadBookedSlotIds,
  saveBookedSlotIds,
} from "../utils/bookingStorage";

const FAKE_LATENCY_MS = 300;

function delay(value) {
  return new Promise((resolve) => setTimeout(() => resolve(value), FAKE_LATENCY_MS));
}

/**
 * Get interviewers matching the given filters, each with only their
 * matching, not-yet-booked slots attached. Mirrors
 * GET /booking/interviewers?domain=&sub_domain=&from_date=&to_date=&time_of_day=
 */
// eslint-disable-next-line no-unused-vars
export async function getAvailableInterviewers({ domain, subDomain, fromDate, toDate, timeOfDay } = {}, token) {
  const bookedSlotIds = new Set(loadBookedSlotIds());

  const results = MOCK_INTERVIEWERS
    .filter((interviewer) => !domain || interviewer.domain === domain)
    .filter((interviewer) => !subDomain || interviewer.sub_domains.includes(subDomain))
    .map((interviewer) => {
      const matchingSlots = interviewer.slots
        .filter((slot) => !bookedSlotIds.has(slot.id))
        .filter((slot) => !fromDate || slot.date >= fromDate)
        .filter((slot) => !toDate || slot.date <= toDate)
        .filter((slot) => !timeOfDay || timeOfDay === "any" || getTimeOfDayBucket(slot.start_time) === timeOfDay)
        .sort((a, b) => `${a.date}${a.start_time}`.localeCompare(`${b.date}${b.start_time}`));

      return { ...interviewer, slots: matchingSlots };
    })
    .filter((interviewer) => interviewer.slots.length > 0)
    .sort((a, b) => {
      const aKey = `${a.slots[0].date}${a.slots[0].start_time}`;
      const bKey = `${b.slots[0].date}${b.slots[0].start_time}`;
      return aKey.localeCompare(bKey);
    });

  return delay(results);
}

/** Book a specific slot with a specific interviewer. Mirrors POST /booking/book. */
// eslint-disable-next-line no-unused-vars
export async function bookSlot({ interviewerId, slotId }, token) {
  const bookedSlotIds = loadBookedSlotIds();

  if (bookedSlotIds.includes(slotId)) {
    throw new Error("That slot was just booked by someone else.");
  }

  const interviewer = MOCK_INTERVIEWERS.find((entry) => entry.id === interviewerId);
  const slot = interviewer?.slots.find((entry) => entry.id === slotId);

  if (!interviewer || !slot) {
    throw new Error("That slot is no longer available.");
  }

  const booking = {
    id: `booking_${Date.now()}`,
    interviewer_id: interviewer.id,
    interviewer_name: interviewer.name,
    domain: interviewer.domain,
    sub_domains: interviewer.sub_domains,
    slot,
    booked_at: new Date().toISOString(),
  };

  saveBookedSlotIds([...bookedSlotIds, slotId]);
  saveBookings([...loadBookings(), booking]);

  return delay(booking);
}

/** Get the current user's bookings, most recent first. Mirrors GET /booking/mine. */
// eslint-disable-next-line no-unused-vars
export async function getMyBookings(token) {
  return delay(loadBookings().slice().reverse());
}

/** Cancel a booking, freeing its slot back up. Mirrors DELETE /booking/{id}. */
// eslint-disable-next-line no-unused-vars
export async function cancelBooking(bookingId, token) {
  const bookings = loadBookings();
  const booking = bookings.find((entry) => entry.id === bookingId);

  saveBookings(bookings.filter((entry) => entry.id !== bookingId));

  if (booking) {
    saveBookedSlotIds(loadBookedSlotIds().filter((slotId) => slotId !== booking.slot.id));
  }

  return delay({ cancelled: true });
}
