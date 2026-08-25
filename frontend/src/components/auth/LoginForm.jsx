import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import GoogleLoginButton from "./GoogleLoginButton";
function LoginForm() {
  const navigate = useNavigate();
  const {
    login,
    resendVerificationEmail,
} = useAuth();
  const [showResend, setShowResend] = useState(false);
  const [isGoogleAccount, setIsGoogleAccount] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccessMessage("");
    setShowResend(false);
    setIsGoogleAccount(false);

    try {
      await login(formData);
      navigate("/dashboard");
    } catch (err) {

      const message =
        err.response?.data?.detail ||
        "Login failed.";

      setError(message);

      if (
        err.response?.status === 403 &&
        message ===
          "Please verify your email before logging in."
      ) {
          setShowResend(true);
      } else if (
        err.response?.status === 401 &&
        message ===
          "This account was created using Google Sign-In. Please continue with Google."
      ) {
          setIsGoogleAccount(true);
      } else {
          setShowResend(false);
  }
}
  };
  const handleResendVerification = async () => {

  try {

    const response =
      await resendVerificationEmail(
        formData.email
      );

    setSuccessMessage(
      response.message
    );

  } catch {

    setError(
      "Unable to resend verification email."
    );
    setSuccessMessage("");
  }

};

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="form-field">
        <span>Email</span>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="you@example.com"
          required
        />
      </label>

      <label className="form-field">
        <span>Password</span>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Enter your password"
          required
        />
      </label>

      <Link to="/forgot-password" className="auth-forgot-link">
        Forgot Password?
      </Link>

      {error && <p className="error-text">{error}</p>}

      <button className="button button--primary button--lg button--wide" type="submit">
        Log in
      </button>

      <div className="auth-divider">
        <span className="auth-divider__line" />
        <span className="auth-divider__text">OR</span>
        <span className="auth-divider__line" />
      </div>

      <GoogleLoginButton />

      <p className="auth-form-footer">
        New to HotSeat? <Link to="/signup">Create an account</Link>
      </p>

      {showResend && (
        <div className="auth-alert">
          <div className="auth-alert__label">STATE · EMAIL NOT VERIFIED</div>
          <p className="auth-alert__text">Please verify your email before logging in.</p>
          <button type="button" className="auth-alert__action" onClick={handleResendVerification}>
            Resend verification email
          </button>
        </div>
      )}

      {isGoogleAccount && (
        <div className="auth-alert">
          <div className="auth-alert__label">STATE · GOOGLE ACCOUNT</div>
          <p className="auth-alert__text">
            This account was created using Google Sign-In. Please use the
            "Continue with Google" button above to log in.
          </p>
        </div>
      )}

      {successMessage && <p className="success-text">{successMessage}</p>}
    </form>
  );
}

export default LoginForm;
