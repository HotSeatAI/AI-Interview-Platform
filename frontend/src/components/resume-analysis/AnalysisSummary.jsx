import MatchOverview from "./MatchOverview";
import {
  buildOverviewSummary,
  getStrongestArea,
  getPriorityArea,
} from "../../utils/resumeAnalysisPresentation";

export default function AnalysisSummary({
  score,
  matchingReport,
  atsReport,
}) {
  const matches = matchingReport?.matches || [];

  const summarySentence = buildOverviewSummary(matchingReport);
  const strongestArea = getStrongestArea(matches);
  const priorityArea = getPriorityArea(matches);

  return (
    <section className="analysis-section">

      <MatchOverview
        score={score}
        matchingReport={matchingReport}
        atsReport={atsReport}
      />

      {matchingReport && (
        <div className="summary-panel">

          <p className="summary-sentence">
            {summarySentence}
          </p>

          <div className="summary-highlights">

            <div className="summary-highlight summary-highlight--positive">
              <span>Strongest area</span>

              <strong>
                {strongestArea
                  ? strongestArea.requirement
                  : "Not yet established"}
              </strong>
            </div>

            <div className="summary-highlight summary-highlight--warning">
              <span>Highest-priority area to review</span>

              <strong>
                {priorityArea
                  ? priorityArea.requirement
                  : "You're in great shape — no urgent gaps found."}
              </strong>
            </div>

          </div>

        </div>
      )}

    </section>
  );
}
