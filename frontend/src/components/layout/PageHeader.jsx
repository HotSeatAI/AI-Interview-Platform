// The slab band every authenticated page opens with - design-spec.md
// section 2, step 2. `stats` is optional; when present each entry may
// set `accent: true` to render its value in --slab-accent (e.g. an
// "in progress" count) instead of the default --on-slab. `right` is
// an escape hatch for pages whose slab holds something richer than
// plain stats (e.g. Weak topics' progress donut) - takes precedence
// over `stats` when both are passed.

function PageHeader({ eyebrow, title, subtitle, stats, right }) {
  return (
    <header className="page-slab">
      <div className="page-slab__copy">
        {eyebrow && <div className="page-slab__eyebrow">{eyebrow}</div>}
        <h1 className="page-slab__title">{title}</h1>
        {subtitle && <p className="page-slab__subtitle">{subtitle}</p>}
      </div>

      {right ? (
        right
      ) : (
        stats &&
        stats.length > 0 && (
          <div className="page-slab__stats">
            {stats.map((stat) => (
              <div className="page-slab__stat" key={stat.label}>
                <div
                  className={`page-slab__stat-value ${
                    stat.accent ? "page-slab__stat-value--accent" : ""
                  }`}
                >
                  {stat.value}
                </div>
                <div className="page-slab__stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        )
      )}
    </header>
  );
}

export default PageHeader;
