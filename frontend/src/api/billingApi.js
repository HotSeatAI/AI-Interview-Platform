import apiClient from "./client";

export const getMyBillingStatus = async (token) => {
  const response = await apiClient.get("/billing/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};

export const createSubscriptionCheckout = async (plan, token) => {
  const response = await apiClient.post(
    "/billing/create-subscription",
    { plan },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
};
