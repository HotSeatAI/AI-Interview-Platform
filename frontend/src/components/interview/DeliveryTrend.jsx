// Session-level delivery trend - did pauses/eye-contact/pitch variety
// improve or worsen across the interview? Purely a visualization over
// the numeric delivery_signals already captured per answer (see
// audioDeliveryAnalyzer.js / videoDeliveryAnalyzer.js) - no new
// tracking, no transcript involved.

const METRICS = [
  {
    key: "eye_contact_pct",
    label: "Eye contact",
    unit: "%",
    higherIsBetter: true,
  },
  {
    key: "pause_count",
    label: "Pauses",
    unit: "",
    higherIsBetter: false,
  },
  {
    key: "short_pauses_per_min",
    label: "Hesitation rate",
    unit: "/min",
    higherIsBetter: false,
  },
  {
    key: "pitch_stddev_hz",
    label: "Vocal variety",
    unit: "Hz",
    higherIsBetter: true,
  },
];

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

      {availableMetrics.map((metric) => {
        const values = entries.map((entry) => entry.signals?.[metric.key]);
        const maxValue = Math.max(1, ...values.filter((v) => v != null));

        return (
          <div className="delivery-trend__row" key={metric.key}>
            <div className="delivery-trend__label">{metric.label}</div>

            <div className="delivery-trend__bars">
              {entries.map((entry, index) => {
                const value = values[index];
                const heightPct =
                  value != null ? Math.max(4, (value / maxValue) * 100) : 0;

                return (
                  <div className="delivery-trend__bar-col" key={entry.id}>
                    <div className="delivery-trend__bar-track">
                      {value != null && (
                        <div
                          className={`delivery-trend__bar delivery-trend__bar--${
                            metric.higherIsBetter ? "good" : "watch"
                          }`}
                          style={{ height: `${heightPct}%` }}
                          title={`${entry.label}: ${value}${metric.unit}`}
                        />
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

      <p className="form-hint">
        Patterns observed from voice/camera signals across your answers -
        not a diagnosis, just a rough trend to help you notice change.
      </p>
    </div>
  );
}

export default DeliveryTrend;
