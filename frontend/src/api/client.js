import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

let unauthorizedHandler = null;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = handler;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 429) {
      const retryAfter = error.response.headers?.["retry-after"];
      const seconds = Number(retryAfter);

      error.friendlyMessage = Number.isFinite(seconds) && seconds > 0
        ? `Too many requests — please try again in ${seconds}s.`
        : "Too many requests — please wait a moment and try again.";
    }

    if (error?.response?.status === 401 && unauthorizedHandler) {
      unauthorizedHandler();
    }

    return Promise.reject(error);
  }
);

export default apiClient;