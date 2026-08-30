const PRIORITY_TONE = {
  critical: "critical",
  high: "warning",
  medium: "info",
  low: "neutral",
};

const FIX_TYPE_LABELS = {
  layout: "Layout",
  section: "Section",
  contact: "Contact Info",
  bullet_quality: "Bullet Quality",
};

export default function AtsFindingsTable({ findings }) {
  const items = findings || [];

  if (!items.length) {
    return (
      <section className="analysis-section">

        <div className="section-heading">
          <span>ATS Findings</span>
          <h2>No issues found</h2>
        </div>

        <p className="empty-state">
          Your resume passed every ATS parseability, section, and
          content-quality check we run.
        </p>

      </section>
    );
  }

  return (
    <section className="analysis-section">

      <div className="section-heading">
        <span>ATS Findings</span>
        <h2>What to fix to raise your ATS score</h2>
        <p>
          Ordered by priority — fixing the critical/high items
          first has the biggest effect on your score.
        </p>
      </div>

      <div className="requirement-table">

        <div className="requirement-table-header review-table-header">
          <span>Priority</span>
          <span>Type</span>
          <span>Recommendation</span>
        </div>

        {items.map((finding, index) => (
          <div
            key={index}
            className="requirement-row review-row"
          >
            <div
              className="requirement-cell"
              data-label="Priority"
            >
              <span
                className={`badge badge--${
                  PRIORITY_TONE[finding.priority] || "neutral"
                }`}
              >
                {finding.priority}
              </span>
            </div>

            <div
              className="requirement-cell"
              data-label="Type"
            >
              {FIX_TYPE_LABELS[finding.fix_type] || finding.fix_type}
            </div>

            <div
              className="requirement-cell requirement-cell--name"
              data-label="Recommendation"
            >
              {finding.message}
            </div>
          </div>
        ))}

      </div>

    </section>
  );
}
