import apiClient from "./client";

export const signup = async (userData) => {
  const response = await apiClient.post("/signup", userData);
  return response.data;
};

export const login = async ({ email, password }) => {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await apiClient.post("/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
};

export const googleLogin = async (idToken) => {
  const response = await apiClient.post("/auth/google", {
    id_token: idToken,
  });

  return response.data;
};

export const getMe = async (token) => {
  const response = await apiClient.get("/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const resendVerificationEmail = async (email) => {
  const response = await apiClient.post(
    "/auth/resend-verification",
    { email }
  );

  return response.data;
};

export const forgotPassword = async (email) => {
  const response = await apiClient.post(
    "/auth/forgot-password",
    { email }
  );

  return response.data;
};

export const resetPassword = async ({ token, newPassword }) => {
  const response = await apiClient.post(
    "/auth/reset-password",
    { token, new_password: newPassword }
  );

  return response.data;
};