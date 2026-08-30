import apiClient from "./client";

export const updateProfile = async (profileData, token) => {
  const response = await apiClient.put("/me/profile", profileData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const acceptTerms = async (token) => {
  const response = await apiClient.put(
    "/me/accept-terms",
    {},
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data;
};
