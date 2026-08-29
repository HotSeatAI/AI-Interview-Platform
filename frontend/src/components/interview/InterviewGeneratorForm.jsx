import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { generateInterview } from "../../api/interviewApi";
import { getResumes, uploadResume } from "../../api/resumeApi";
import useAuth from "../../hooks/useAuth";

const UPLOAD_NEW_VALUE = "__upload_new__";

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

function InterviewGeneratorForm() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    role: "",
    difficulty: "Medium",
    resume_id: "",
  });

  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingResumes, setLoadingResumes] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const fetchResumes = async () => {
    try {
      const data = await getResumes(token);
      setResumes(data);
      return data;
    } catch {
      setError("Failed to load resumes.");
      return [];
    }
  };

  useEffect(() => {
    const loadInitialResumes = async () => {
      const data = await fetchResumes();

      if (data.length > 0) {
        setFormData((prev) => ({
          ...prev,
          resume_id: data[0].id,
        }));
      }

      setLoadingResumes(false);
    };

    loadInitialResumes();
  }, [token]);

  const handleChange = (event) => {
    if (event.target.name === "resume_id" && event.target.value === UPLOAD_NEW_VALUE) {
      fileInputRef.current?.click();
      return;
    }

    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleResumeFileChange = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";

    if (!file) {
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed");
      return;
    }

    try {
      setUploading(true);
      setError("");

      const uploaded = await uploadResume(file, token);
      const data = await fetchResumes();

      setFormData((prev) => ({
        ...prev,
        resume_id: uploaded.resume_id ?? data[data.length - 1]?.id ?? prev.resume_id,
      }));
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Resume upload failed"
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDifficultySelect = (difficulty) => {
    setFormData((prev) => ({ ...prev, difficulty }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!formData.role.trim()) {
      setError("Please enter a role.");
      return;
    }


    try {
      setLoading(true);

      const response = await generateInterview(
        {
          role: formData.role.trim(),
          difficulty: formData.difficulty,
          resume_id:formData.resume_id
          ? Number(formData.resume_id)
          : null,
        },
        token
      );

      navigate(`/interview/${response.session_id}`);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Failed to generate interview."
      );
    } finally {
      setLoading(false);
    }
  };

  if (loadingResumes) {
    return <p className="form-hint">Loading resumes...</p>;
  }

  return (
    <form className="generator-form" onSubmit={handleSubmit}>
      <label className="form-field">
        <span>Resume</span>

        <select
          name="resume_id"
          value={formData.resume_id}
          onChange={handleChange}
          disabled={uploading}
        >
          <option value="">No Resume</option>
          {resumes.map((resume) => (
            <option key={resume.id} value={resume.id}>
              {resume.original_filename}
            </option>
          ))}
          <option value={UPLOAD_NEW_VALUE}>Upload new resume...</option>
        </select>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleResumeFileChange}
          hidden
        />
        <span className="form-hint">
          {uploading ? "Uploading resume..." : "Questions will be tailored to this resume."}
        </span>
      </label>

      <label className="form-field">
        <span>Role</span>
        <input
          type="text"
          name="role"
          placeholder="e.g. Backend Engineer"
          value={formData.role}
          onChange={handleChange}
        />
      </label>

      <div className="form-field">
        <span>Difficulty</span>
        <div className="segmented-control">
          {DIFFICULTIES.map((difficulty) => (
            <button
              key={difficulty}
              type="button"
              className={`segmented-control__option ${
                formData.difficulty === difficulty ? "segmented-control__option--active" : ""
              }`}
              onClick={() => handleDifficultySelect(difficulty)}
            >
              {difficulty}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}

      <button className="button button--primary button--xl button--wide" type="submit" disabled={loading}>
        {loading ? "Generating..." : "Enter the HotSeat"}
      </button>
    </form>
  );
}

export default InterviewGeneratorForm;
