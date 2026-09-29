function formatTime(time24) {
  const [hourStr, minute] = time24.split(":");
  const hour = Number(hourStr);
  const period = hour >= 12 ? "PM" : "AM";
  const hour12 = hour % 12 === 0 ? 12 : hour % 12;
  return `${hour12}:${minute} ${period}`;
}

export function formatSlotLabel({ date, start_time, end_time }) {
  const dateLabel = new Date(`${date}T00:00:00`).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  return `${dateLabel} · ${formatTime(start_time)}-${formatTime(end_time)}`;
}

export function getTimeOfDayBucket(time24) {
  const hour = Number(time24.split(":")[0]);
  if (hour < 12) return "morning";
  if (hour < 17) return "afternoon";
  return "evening";
}
