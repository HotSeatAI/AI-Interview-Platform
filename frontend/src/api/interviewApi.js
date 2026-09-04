import apiClient from "./client";

export const generateInterview = async (payload, token) => {
  const response = await apiClient.post("/interview/generate-questions", payload, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const getInterviewRounds = async (role, token) => {
  const response = await apiClient.get("/interview/rounds", {
    params: { role },
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const getInterviewSession = async (sessionId, token) => {
  const response = await apiClient.get(`/interview/${sessionId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const getInterviewHistory = async (token) => {
  const response = await apiClient.get("/interview/history", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const finishInterviewSession = async (sessionId, token) => {
  const response = await apiClient.post(
    `/interview/${sessionId}/finish`,
    {},
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};