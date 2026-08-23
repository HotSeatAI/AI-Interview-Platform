export default function ResumeSelector({
  resumes,
  selectedResumeId,
  onSelect,
}) {
  if (!resumes?.length) {
    return (
      <div className="resume-selector empty">
        <h3>No resumes available</h3>

        <p>
          Upload a resume before starting a
          Job Description analysis.
        </p>
      </div>
    );
  }

  return (
    <div className="resume-selector">
      <div className="resume-selector-header">
        <div>
          <h3>Select Resume</h3>

          <p>
            Choose the resume you want to evaluate.
          </p>
        </div>
      </div>

      <div className="resume-list">
        {resumes.map((resume) => {
          const selected =
            Number(selectedResumeId) ===
            Number(resume.id);

          return (
            <button
              key={resume.id}
              type="button"
              className={
                selected
                  ? "resume-option selected"
                  : "resume-option"
              }
              onClick={() =>
                onSelect(resume.id)
              }
            >
              <div className="resume-option-icon">
                PDF
              </div>

              <div className="resume-option-info">
                <strong>
                  {resume.original_filename}
                </strong>

                {resume.created_at && (
                  <span>
                    Uploaded{" "}
                    {new Date(
                      resume.created_at
                    ).toLocaleDateString()}
                  </span>
                )}
              </div>

              <div className="resume-option-check">
                {selected ? "✓" : ""}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}