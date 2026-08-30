export default function MatchOverview({
  score,
  matchingReport,
  atsReport,
}) {
  const summary =
    matchingReport?.summary;

  const missingAndReview =
    (summary?.missing_matches ?? 0) +
    (summary?.ambiguous_matches ?? 0);

  return (
    <div className="match-overview">

      {matchingReport && (
        <div className="score-card">
          <span>
            JD Match Score
          </span>

          <strong>
            {score ?? 0}
          </strong>

          <small>
            / 100
          </small>
        </div>
      )}

      {atsReport && (
        <div
          className={
            atsReport.parseability_capped
              ? "score-card score-card--capped"
              : "score-card"
          }
        >
          <span>
            ATS Score
          </span>

          <strong>
            {Math.round(atsReport.ats_score ?? 0)}
          </strong>

          <small>
            / 100
          </small>

          {atsReport.parseability_capped && (
            <span className="score-card__warning">
              Capped — parseability issue
            </span>
          )}
        </div>
      )}

      {matchingReport && (
        <>
          <div className="match-stat match-stat--positive">
            <strong>
              {summary?.strong_matches ?? 0}
            </strong>

            <span>
              Strong matches
            </span>
          </div>

          <div className="match-stat match-stat--info">
            <strong>
              {summary?.partial_matches ?? 0}
            </strong>

            <span>
              Partial matches
            </span>
          </div>

          <div className="match-stat match-stat--warning">
            <strong>
              {missingAndReview}
            </strong>

            <span>
              Missing / needs review
            </span>
          </div>

          <div className="match-stat">
            <strong>
              {summary?.required_matched ?? 0}
              /
              {summary?.required_requirements ?? 0}
            </strong>

            <span>
              Required matched
            </span>
          </div>

          <div className="match-stat">
            <strong>
              {summary?.preferred_matched ?? 0}
              /
              {summary?.preferred_requirements ?? 0}
            </strong>

            <span>
              Preferred matched
            </span>
          </div>
        </>
      )}

    </div>
  );
}
