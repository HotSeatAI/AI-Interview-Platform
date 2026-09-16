import { useEffect, useState } from "react";

import { getInterviewHistory } from "../../api/interviewApi";
import useAuth from "../../hooks/useAuth";

import HistoryItem from "./HistoryItem";

function HistoryList() {
  const { token } = useAuth();

  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getInterviewHistory(token);
        setSessions(data);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            "Failed to load interview history."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [token]);

  if (loading) {
    return <p className="form-hint">Loading interview history...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (sessions.length === 0) {
    return <p className="empty-state">No interview sessions found.</p>;
  }

  return (
    <div className="list-row-group">
      {sessions.map((session) => (
        <HistoryItem
          key={session.session_id}
          session={session}
        />
      ))}
    </div>
  );
}

export default HistoryList;
