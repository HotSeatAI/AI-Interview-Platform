import apiClient from "./client";

/**
 * Start a resume ↔ JD analysis.
 *
 * JD can be supplied as:
 * - plain text
 * - PDF
 * - image
 */
export async function startResumeAnalysis({
  resumeId,
  jobDescription,
  jobDescriptionFile,
  token,
}) {
  const formData = new FormData();

  formData.append(
    "resume_id",
    String(resumeId)
  );

  if (jobDescription?.trim()) {
    formData.append(
      "job_description",
      jobDescription.trim()
    );
  }

  if (jobDescriptionFile) {
    formData.append(
      "job_description_file",
      jobDescriptionFile
    );
  }

  const response = await apiClient.post(
    "/resume-analysis/start",
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}


/**
 * Get current analysis progress.
 */
export async function getResumeAnalysisStatus(
  analysisId,
  token
) {
  const response = await apiClient.get(
    `/resume-analysis/${analysisId}/status`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}


/**
 * Get completed analysis.
 */
export async function getResumeAnalysisResult(
  analysisId,
  token
) {
  const response = await apiClient.get(
    `/resume-analysis/${analysisId}/result`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}


/**
 * Standalone ATS-compatibility check — no job description
 * required. Runs synchronously (deterministic, no Gemini call),
 * so unlike startResumeAnalysis this resolves with the finished
 * result directly, no polling needed.
 */
export async function getAtsScore({ resumeId, token }) {
  const formData = new FormData();

  formData.append(
    "resume_id",
    String(resumeId)
  );

  const response = await apiClient.post(
    "/resume-analysis/ats-score",
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}


/**
 * Get the current user's past resume ↔ JD analyses,
 * most recent first.
 */
export async function getResumeAnalysisHistory(
  token
) {
  const response = await apiClient.get(
    "/resume-analysis/history",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}