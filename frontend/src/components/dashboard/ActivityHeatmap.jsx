const WEEKS = 53;
const DAYS_PER_WEEK = 7;
const MONTH_LABELS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];
const DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""];

function toDateKey(date) {
  return date.toISOString().slice(0, 10);
}

function bucketFor(count) {
  if (count <= 0) return 0;
  if (count === 1) return 1;
  if (count === 2) return 2;
  if (count === 3) return 3;
  return 4;
}

// Builds a full WEEKS x DAYS_PER_WEEK grid ending today, columns are
// weeks (Sun-Sat), so it always renders clean full weeks like GitHub's
// contribution graph - regardless of how sparse the activity array is.
function buildGrid(activity) {
  const countsByDate = new Map(
    (activity || []).map((entry) => [entry.date, entry.count])
  );

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const totalDays = WEEKS * DAYS_PER_WEEK;
  const startOffset = totalDays - 1 - today.getDay();
  const gridStart = new Date(today);
  gridStart.setDate(gridStart.getDate() - startOffset);

  const weeks = [];

  for (let week = 0; week < WEEKS; week++) {
    const days = [];

    for (let dow = 0; dow < DAYS_PER_WEEK; dow++) {
      const date = new Date(gridStart);
      date.setDate(date.getDate() + week * DAYS_PER_WEEK + dow);

      if (date > today) {
        days.push(null);
        continue;
      }

      const key = toDateKey(date);
      days.push({
        date,
        key,
        count: countsByDate.get(key) || 0,
      });
    }

    weeks.push(days);
  }

  return weeks;
}

function monthLabelsFor(weeks) {
  const labels = [];
  let lastMonth = null;

  weeks.forEach((week, index) => {
    const firstRealDay = week.find(Boolean);
    if (!firstRealDay) return;

    const month = firstRealDay.date.getMonth();
    if (month !== lastMonth) {
      labels.push({ index, text: MONTH_LABELS[month] });
      lastMonth = month;
    }
  });

  return labels;
}

function ActivityHeatmap({ activity }) {
  const weeks = buildGrid(activity);
  const monthLabels = monthLabelsFor(weeks);
  const total = (activity || []).reduce((sum, entry) => sum + entry.count, 0);

  return (
    <section className="activity-heatmap">
      <div className="eyebrow">ACTIVITY</div>
      <h2 className="activity-heatmap__title">
        {total} {total === 1 ? "activity" : "activities"} in the last year
      </h2>

      <div className="activity-heatmap__scroll">
        <div className="activity-heatmap__body">
          <div className="activity-heatmap__day-labels">
            {DAY_LABELS.map((label, index) => (
              <span key={index}>{label}</span>
            ))}
          </div>

          <div className="activity-heatmap__main">
            <div className="activity-heatmap__months">
              {monthLabels.map(({ index, text }) => (
                <span
                  key={`${text}-${index}`}
                  style={{ gridColumnStart: index + 1 }}
                >
                  {text}
                </span>
              ))}
            </div>

            <div className="activity-heatmap__grid">
              {weeks.map((week, weekIndex) => (
                <div className="activity-heatmap__week" key={weekIndex}>
                  {week.map((day, dayIndex) =>
                    day ? (
                      <div
                        key={day.key}
                        className={`activity-heatmap__cell activity-heatmap__cell--${bucketFor(
                          day.count
                        )}`}
                        data-tooltip={`${day.count} ${
                          day.count === 1 ? "activity" : "activities"
                        } on ${day.date.toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}`}
                      />
                    ) : (
                      <div
                        key={dayIndex}
                        className="activity-heatmap__cell activity-heatmap__cell--empty"
                      />
                    )
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="activity-heatmap__legend">
        <span>Less</span>
        {[0, 1, 2, 3, 4].map((bucket) => (
          <div
            key={bucket}
            className={`activity-heatmap__cell activity-heatmap__cell--${bucket}`}
          />
        ))}
        <span>More</span>
      </div>
    </section>
  );
}

export default ActivityHeatmap;
