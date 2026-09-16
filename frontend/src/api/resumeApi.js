import apiClient from "./client";

export const uploadResume = async (file, token) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/resume/upload", formData, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const getResumes = async (token) => {
  const response = await apiClient.get("/resume", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const deleteResume = async (resumeId, token) => {
  const response = await apiClient.delete(`/resume/${resumeId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};