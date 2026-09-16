import apiClient from "./client";

export const submitAnswer = async (payload, token) => {
  const response = await apiClient.post("/answer", payload, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const generateFollowUp = async (answerId, token) => {
  const response = await apiClient.post(
    `/answer/${answerId}/follow-up`,
    {},
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }
  );

  return response.data;
};

export const getAnswer = async (answerId, token) => {
  const response = await apiClient.get(`/answer/${answerId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const getSessionResults = async (sessionId, token) => {
  const response = await apiClient.get(`/answer/session/${sessionId}/results`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};