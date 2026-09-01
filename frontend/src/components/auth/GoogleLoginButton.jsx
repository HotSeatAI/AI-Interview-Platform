import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

import useAuth from "../../hooks/useAuth";

function GoogleLoginButton() {
  const { googleLogin } = useAuth();
  const navigate = useNavigate();

  const handleSuccess = async (credentialResponse) => {
  try {
    if (!credentialResponse?.credential) {
      throw new Error("Google did not return an ID token.");
    }

    await googleLogin(credentialResponse.credential);
    navigate("/dashboard");
  } catch (error) {
    // Don't log the raw error - it can carry the Google ID token or an
    // Authorization header in its request config.
    console.error(
      "Google authentication failed:",
      error?.response?.data?.detail || error?.message
    );

    alert(
      error.friendlyMessage ||
      error.response?.data?.detail ||
      error.message ||
      "Google authentication failed."
    );
  }
};

  return (
    <div className="google-login-wrap">
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={() => {
          alert("Google Sign-In was cancelled or failed.");
        }}
        theme="filled_black"
        shape="rectangular"
        size="large"
        text="continue_with"
        width="360"
      />
    </div>
  );
}

export default GoogleLoginButton;
