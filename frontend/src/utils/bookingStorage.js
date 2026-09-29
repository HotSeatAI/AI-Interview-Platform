const BOOKINGS_KEY = "hotseat.myBookings.v1";
const BOOKED_SLOT_IDS_KEY = "hotseat.bookedSlotIds.v1";

export function loadBookings() {
  try {
    const raw = localStorage.getItem(BOOKINGS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveBookings(bookings) {
  try {
    localStorage.setItem(BOOKINGS_KEY, JSON.stringify(bookings));
  } catch {
    // localStorage unavailable (private mode / quota) - in-memory state still works
  }
}

export function loadBookedSlotIds() {
  try {
    const raw = localStorage.getItem(BOOKED_SLOT_IDS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveBookedSlotIds(slotIds) {
  try {
    localStorage.setItem(BOOKED_SLOT_IDS_KEY, JSON.stringify(slotIds));
  } catch {
    // ignore
  }
}
