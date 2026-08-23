import { useEffect, useRef, useState } from "react";
import { FaTrash } from "react-icons/fa";
import { Link } from "react-router-dom";
import {
  getResumes,
  uploadResume,
  deleteResume,
} from "../../api/resumeApi";

import useAuth from "../../hooks/useAuth";
import useResumeAnalysis from "../../hooks/useResumeAnalysis";

import AnalysisProgress from "../resume-analysis/AnalysisProgress";
function ResumeUploadCard() {
  const { token } = useAuth();
  const fileInputRef = useRef(null);
  const jdFileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchingResumes, setFetchingResumes] = useState(true);
  const [deletingResumeId, setDeletingResumeId] = useState(null);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  // Resume <-> JD analysis: this task's state/lifecycle is owned by
  // ResumeAnalysisProvider (mounted in App.jsx) so it survives navigating
  // away from this page instead of resetting on every mount.
  const {
    resumeId: analysisResumeId,
    jobDescription,
    jobDescriptionFile,
    status: analysisStatus,
    starting: analysisStarting,
    analysisId,
    progress: analysisProgress,
    currentStage: analysisCurrentStage,
    errorMessage: analysisError,
    setResumeId: setAnalysisResumeId,
    setJobDescription,
    setJobDescriptionFile,
    setErrorMessage: setAnalysisError,
    startAnalysis,
    resetAnalysis,
  } = useResumeAnalysis();

  const loadResumes = async () => {
    try {
      setFetchingResumes(true);
      const data = await getResumes(token);
      setResumes(data);
    } catch {
      setError("Failed to load resumes");
    } finally {
      setFetchingResumes(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadResumes();
    }
  }, [token]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setSuccess("");
    setError("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed");
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a PDF resume first");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setSuccess("");

      await uploadResume(selectedFile, token);

      setSuccess(
        `${selectedFile.name} has been uploaded successfully`
      );

      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadResumes();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Resume upload failed"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (resume) => {
    const confirmed = window.confirm(
      `Are you sure you want to permanently delete "${resume.original_filename}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingResumeId(resume.id);

      setSuccess("");
      setError("");

      await deleteResume(resume.id, token);

      setSuccess("Resume deleted successfully.");

      await loadResumes();
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to delete resume."
      );
    } finally {
      setDeletingResumeId(null);
    }
  };

  const handleJdFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const allowedTypes = [
      "application/pdf",
      "image/png",
      "image/jpeg",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setAnalysisError("Please upload a PDF, PNG, JPG or WEBP file.");
      event.target.value = "";
      return;
    }

    setAnalysisError("");
    setJobDescriptionFile(file);
  };

  const handleRemoveJdFile = () => {
    setJobDescriptionFile(null);
    if (jdFileInputRef.current) {
      jdFileInputRef.current.value = "";
    }
  };

  const latestResumeId = resumes.length
    ? resumes.reduce((latest, resume) =>
        new Date(resume.created_at) > new Date(latest.created_at) ? resume : latest
      ).id
    : null;

  const analysisBusy =
    analysisStarting || analysisStatus === "analyzing" || analysisStatus === "restoring";

  return (
    <>
      <section className="resume-section">
        <div className="section-header">
          <div className="eyebrow">YOUR RESUME</div>
          <h1>This is what grounds your interview</h1>
          <p>Every question HotSeat generates is built from the resume you upload here.</p>
        </div>

        <div className="dropzone">
          <div className="dropzone__text">
            <div className="dropzone__label">DROP A PDF OR BROWSE</div>
            <div className="dropzone__hint">PDF only, up to 10MB</div>
            {selectedFile && (
              <div className="file-preview">
                Selected file: <strong>{selectedFile.name}</strong>
              </div>
            )}
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            hidden
          />
          <button
            type="button"
            className="button button--secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            Choose file
          </button>
          <button
            type="button"
            className="button button--primary"
            onClick={handleUpload}
            disabled={loading || !selectedFile}
          >
            {loading ? "Uploading..." : "Upload resume"}
          </button>
        </div>

        {success && <p className="success-text">{success}</p>}
        {error && <p className="error-text">{error}</p>}

        <div className="resume-list">
          {fetchingResumes ? (
            <p className="form-hint">Loading resumes...</p>
          ) : resumes.length === 0 ? (
            <p className="empty-state">No resumes uploaded yet.</p>
          ) : (
            resumes.map((resume) => (
              <div className="resume-list__item" key={resume.id}>
                <div className="resume-list__info">
                  <div className="resume-list__name">{resume.original_filename}</div>
                  <div className="resume-list__date">
                    Uploaded {new Date(resume.created_at).toLocaleString()}
                  </div>
                </div>
                {resume.id === latestResumeId && (
                  <span className="difficulty-pill">Active</span>
                )}
                <button
                  type="button"
                  className="resume-list__delete"
                  title="Delete resume"
                  disabled={deletingResumeId === resume.id}
                  onClick={() => handleDelete(resume)}
                >
                  {deletingResumeId === resume.id ? "…" : <FaTrash />}
                </button>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="resume-section">
        <div className="section-header">
          <div className="eyebrow">RESUME INTELLIGENCE</div>
          <h2>Check your resume against a job description</h2>
          <p>See what you already cover, what's missing, and what to fix before you apply.</p>
        </div>

        {analysisStatus === "completed" && analysisId && (
          <div className="analysis-complete-banner">
            <div>
              <div className="analysis-complete-banner__label">
                RESUME INTELLIGENCE · COMPLETE
              </div>
              <p className="analysis-complete-banner__text">
                Your resume ↔ JD analysis has finished.
              </p>
            </div>
            <div className="analysis-complete-banner__actions">
              <Link
                className="button button--primary button--sm"
                to={`/resume-analysis/${analysisId}`}
              >
                View results
              </Link>
              <button type="button" className="button button--ghost" onClick={resetAnalysis}>
                Start a new analysis
              </button>
            </div>
          </div>
        )}

        {!analysisBusy && analysisStatus !== "completed" && (
          <div className="analysis-form-card">
            <label className="form-field">
              <span>Resume to evaluate</span>
              <select
                value={analysisResumeId}
                onChange={(event) => setAnalysisResumeId(event.target.value)}
                disabled={fetchingResumes || resumes.length === 0}
              >
                <option value="">Select a resume</option>
                {resumes.map((resume) => (
                  <option key={resume.id} value={resume.id}>
                    {resume.original_filename}
                  </option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span>Job description</span>
              <textarea
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the complete job description here..."
                rows={6}
              />
            </label>

            <div className="jd-file-row">
              <span className="form-hint">or upload the job description as PDF / image</span>
              <label className="button button--ghost jd-file-row__button">
                Choose file
                <input
                  ref={jdFileInputRef}
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.webp"
                  hidden
                  onChange={handleJdFileChange}
                />
              </label>
            </div>

            {jobDescriptionFile && (
              <p className="file-preview">
                Selected JD: <strong>{jobDescriptionFile.name}</strong>
                <button
                  type="button"
                  className="file-preview__remove"
                  title="Remove JD file"
                  onClick={handleRemoveJdFile}
                >
                  <FaTrash />
                </button>
              </p>
            )}

            {analysisError && <p className="error-text">{analysisError}</p>}

            <button
              type="button"
              className="button button--primary button--lg button--wide"
              onClick={startAnalysis}
              disabled={
                !analysisResumeId ||
                (!jobDescription.trim() && !jobDescriptionFile)
              }
            >
              Analyze resume against JD
            </button>
          </div>
        )}

        {analysisBusy && (
          <>
            {analysisStatus === "restoring" && (
              <p className="form-hint">Restoring your in-progress analysis…</p>
            )}
            <AnalysisProgress progress={analysisProgress} currentStage={analysisCurrentStage} />
          </>
        )}
      </section>
    </>
  );
}

export default ResumeUploadCard;
