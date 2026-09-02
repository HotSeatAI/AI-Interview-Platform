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

export const requestEmailChange = async (
  { current_password, new_email },
  token
) => {
  const response = await apiClient.post(
    "/me/email-change/request",
    { current_password, new_email },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data;
};

export const confirmEmailChange = async (emailChangeToken) => {
  const response = await apiClient.get(
    `/me/email-change/confirm?token=${emailChangeToken}`
  );
  return response.data;
};

export const changePassword = async (
  { current_password, new_password },
  token
) => {
  const response = await apiClient.post(
    "/me/change-password",
    { current_password, new_password },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data;
};
