import apiClient from "./client";

export const generateInterview = async (payload, token) => {
  const response = await apiClient.post("/interview/generate-questions", payload, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const getInterviewRounds = async (role, token) => {
  const response = await apiClient.get("/interview/rounds", {
    params: { role },
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const getInterviewSession = async (sessionId, token) => {
  const response = await apiClient.get(`/interview/${sessionId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const getInterviewHistory = async (token) => {
  const response = await apiClient.get("/interview/history", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const finishInterviewSession = async (sessionId, token) => {
  const response = await apiClient.post(
    `/interview/${sessionId}/finish`,
    {},
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }
  );

  return response.data;
};

export const submitSessionFeedback = async (sessionId, payload, token) => {
  const response = await apiClient.post(
    `/interview/${sessionId}/feedback`,
    payload,
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }
  );

  return response.data;
};