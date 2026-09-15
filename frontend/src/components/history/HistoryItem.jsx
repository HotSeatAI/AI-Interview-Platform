import { Link } from "react-router-dom";

import { ROUND_LABELS } from "../../constants/interviewRounds";

function HistoryItem({ session }) {
  const createdDate = new Date(session.created_at).toLocaleString();

  return (
    <article className="list-row">
      <div className="list-row__info">
        <div className="list-row__title">{session.role}</div>
        <div className="list-row__meta">
          <span className="difficulty-pill">{session.difficulty}</span>
          {session.round && session.round !== "full" && (
            <span className="round-pill">{ROUND_LABELS[session.round] || session.round}</span>
          )}
          <span>{createdDate}</span>
        </div>
      </div>

      <div className="list-row__actions">
        <Link className="button button--secondary button--sm" to={`/interview/${session.session_id}`}>
          Continue interview
        </Link>
        <Link className="button button--primary button--sm" to={`/results/${session.session_id}`}>
          View results
        </Link>
      </div>
    </article>
  );
}

export default HistoryItem;
