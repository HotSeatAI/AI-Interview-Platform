import apiClient from "./client";

export const getTopics = async (token) => {
  const response = await apiClient.get("/topics", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  return response.data;
};

export const startTopicPractice = async (topicId, token) => {
  const response = await apiClient.post(
    `/topics/${topicId}/practice`,
    {},
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }
  );

  return response.data;
};
