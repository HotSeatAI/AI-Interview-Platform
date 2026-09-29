import InterviewerRow from "./InterviewerRow";

function InterviewerList({ interviewers, loading, error, hasSearched, onRequestBook }) {
  if (loading) {
    return <p className="form-hint">Finding matching interviewers...</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!hasSearched) {
    return <p className="empty-state">Select a domain above to see available interviewers.</p>;
  }

  if (interviewers.length === 0) {
    return <p className="empty-state">No interviewers match these filters yet. Try widening your date range or time of day.</p>;
  }

  return (
    <div className="list-row-group">
      {interviewers.map((interviewer) => (
        <InterviewerRow key={interviewer.id} interviewer={interviewer} onRequestBook={onRequestBook} />
      ))}
    </div>
  );
}

export default InterviewerList;
