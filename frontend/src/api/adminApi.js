import apiClient from "./client";

export const getAdminUsers = async (token) => {
  const response = await apiClient.get("/admin/users", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const setUserPlan = async (userId, plan, token) => {
  const response = await apiClient.patch(
    `/admin/users/${userId}/plan`,
    { plan },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};
