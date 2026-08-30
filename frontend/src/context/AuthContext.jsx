import { createContext, useEffect, useState } from "react";
import {
  getMe,
  login as loginApi,
  signup as signupApi,
  googleLogin as googleLoginApi,
  resendVerificationEmail as resendVerificationEmailApi,
} from "../api/authApi";
import { getToken, removeToken, setToken } from "../utils/token";
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setAuthToken] = useState(getToken());
  const [loading, setLoading] = useState(true);

  const login = async ({ email, password }) => {
    try {
      const data = await loginApi({ email, password });

      setToken(data.access_token);
      setAuthToken(data.access_token);

      const currentUser = await getMe(data.access_token);

      setUser(currentUser);

      return currentUser;
    } catch (error) {
      // Never log the raw error object here - for a failed login it carries
      // the axios request config, which includes the submitted password.
      console.error(
        "Login failed:",
        error?.response?.data?.detail || error?.message
      );
      throw error;
    }
};
  const resendVerificationEmail = async (email) => {
    return await resendVerificationEmailApi(email);
};
  const googleLogin = async (idToken) => {
    try {
      const data = await googleLoginApi(idToken);

      setToken(data.access_token);
      setAuthToken(data.access_token);

      const currentUser = await getMe(data.access_token);

      setUser(currentUser);

      return currentUser;
  } catch (error) {
    // Same reasoning as login(): don't log the raw error, it can carry
    // request headers/body (e.g. the Google ID token or a Bearer token).
    console.error(
      "Google login failed:",
      error?.response?.data?.detail || error?.message
    );
    throw error;
  }
};

  const signup = async ({ username, email, password }) => {
  return await signupApi({
    username,
    email,
    password,
  });
};

  const logout = () => {
    removeToken();
    setAuthToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    const savedToken = getToken();
    if (!savedToken) return null;
    const currentUser = await getMe(savedToken);
    setUser(currentUser);
    return currentUser;
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const savedToken = getToken();

      if (!savedToken) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getMe(savedToken);
        setAuthToken(savedToken);
        setUser(currentUser);
      } catch (error) {
        removeToken();
        setAuthToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user,
        login,
        googleLogin,
        signup,
        resendVerificationEmail,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;