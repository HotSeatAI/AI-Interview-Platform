// Session-level delivery trend - did pauses/eye-contact/pitch variety
// improve or worsen across the interview? Purely a visualization over
// the numeric delivery_signals already captured per answer (see
// audioDeliveryAnalyzer.js / videoDeliveryAnalyzer.js) - no new
// tracking, no transcript involved.
//
// Good/Fair/Needs work bands below are simple static heuristics for
// giving the numbers context, not a validated or clinical measurement -
// see the disclaimer text rendered at the bottom of the component.

const METRICS = [
  {
    key: "eye_contact_pct",
    label: "Eye contact",
    unit: "%",
    higherIsBetter: true,
    description:
      "How much of the time you appeared to be looking toward the camera. Higher is better.",
    thresholds: { good: 70, fair: 40 },
  },
  {
    key: "pause_count",
    label: "Pauses",
    unit: "",
    higherIsBetter: false,
    description:
      "Noticeable pauses (150ms+) across the answer. Lower is generally better, though pausing to think is normal.",
    thresholds: { good: 3, fair: 6 },
  },
  {
    key: "pitch_stddev_hz",
    label: "Vocal variety",
    unit: "Hz",
    higherIsBetter: true,
    description:
      "How much your pitch varies while speaking. Very low variety can sound flat/monotone; more variety reads as natural expressiveness.",
    thresholds: { good: 20, fair: 10 },
  },
];

const STATUS_META = {
  good: { label: "Good", badgeClass: "badge--positive" },
  fair: { label: "Fair", badgeClass: "badge--warning" },
  "needs-work": { label: "Needs work", badgeClass: "badge--critical" },
};

function getStatus(metric, value) {
  const { good, fair } = metric.thresholds;

  if (metric.higherIsBetter) {
    if (value >= good) return "good";
    if (value >= fair) return "fair";
    return "needs-work";
  }

  if (value <= good) return "good";
  if (value <= fair) return "fair";
  return "needs-work";
}

function formatValue(value, metric, { withUnit = true } = {}) {
  const rounded = Math.round(value * 10) / 10;
  const display = Number.isInteger(rounded) ? rounded : rounded.toFixed(1);
  return withUnit ? `${display}${metric.unit}` : `${display}`;
}

function DeliveryTrend({ entries }) {
  const availableMetrics = METRICS.filter((metric) =>
    entries.some(
      (entry) =>
        entry.signals?.[metric.key] !== null &&
        entry.signals?.[metric.key] !== undefined
    )
  );

  if (availableMetrics.length === 0) return null;

  return (
    <div className="delivery-trend">
      <div className="eyebrow">DELIVERY TREND</div>

      <div className="delivery-trend__grid">
        {availableMetrics.map((metric) => {
          const rawValues = entries.map((entry) => entry.signals?.[metric.key]);
          const presentValues = rawValues.filter((v) => v != null);
          const maxValue = Math.max(1, ...presentValues);
          const average =
            presentValues.reduce((sum, v) => sum + v, 0) / presentValues.length;
          const averageStatusMeta = STATUS_META[getStatus(metric, average)];

          return (
            <div className="delivery-trend__card" key={metric.key}>
              <div className="delivery-trend__card-header">
                <div className="delivery-trend__card-title">{metric.label}</div>
                <span className={`badge ${averageStatusMeta.badgeClass}`}>
                  {averageStatusMeta.label}
                </span>
              </div>

              <p className="delivery-trend__card-description">{metric.description}</p>

              <div className="delivery-trend__average">
                {formatValue(average, metric)}
                <span className="delivery-trend__average-caption">session average</span>
              </div>

              <div className="delivery-trend__bars">
                {entries.map((entry, index) => {
                  const value = rawValues[index];
                  const heightPct =
                    value != null ? Math.max(4, (value / maxValue) * 100) : 0;
                  const barStatus = value != null ? getStatus(metric, value) : null;

                  return (
                    <div className="delivery-trend__bar-col" key={entry.id}>
                      <div className="delivery-trend__bar-track">
                        {value != null && (
                          <div
                            className="delivery-trend__bar-tip-wrap"
                            style={{ height: `${heightPct}%` }}
                          >
                            <span className="delivery-trend__bar-tip">
                              {formatValue(value, metric, { withUnit: false })}
                            </span>
                            <div
                              className={`delivery-trend__bar delivery-trend__bar--${barStatus}`}
                              title={`${entry.label}: ${formatValue(value, metric)}`}
                            />
                          </div>
                        )}
                      </div>
                      <div className="delivery-trend__bar-tag">{entry.label}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <p className="form-hint">
        Patterns observed from voice/camera signals across your answers - not a diagnosis,
        just a rough trend to help you notice change. Good / Fair / Needs work bands are
        approximate heuristics, not a validated or clinical measurement.
      </p>
    </div>
  );
}

export default DeliveryTrend;
