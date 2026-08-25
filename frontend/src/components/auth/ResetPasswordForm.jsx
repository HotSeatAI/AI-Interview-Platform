import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { resetPassword } from "../../api/authApi";

function ResetPasswordForm() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tokenError, setTokenError] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!token) {
    return (
      <div className="verify-card">
        <span className="verify-card__tag verify-card__tag--error">ERROR</span>
        <span className="verify-card__icon verify-card__icon--error" />
        <h3 className="verify-card__title">Invalid reset link</h3>
        <p className="verify-card__body">
          This password reset link is missing or malformed.
        </p>
        <Link to="/forgot-password" className="button button--secondary">
          Request a new link
        </Link>
      </div>
    );
  }

  if (success) {
    return (
      <div className="verify-card">
        <span className="verify-card__tag verify-card__tag--success">SUCCESS</span>
        <span className="verify-card__icon verify-card__icon--success" />
        <h3 className="verify-card__title">Password reset successfully</h3>
        <p className="verify-card__body">
          You can now log in with your new password.
        </p>
        <Link to="/login" className="button button--primary">
          Go to login
        </Link>
      </div>
    );
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setTokenError(false);

    if (!newPassword || !confirmPassword) {
      setError("Please fill in both password fields.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await resetPassword({ token, newPassword });
      setSuccess(true);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        "Unable to reset your password.";

      setError(message);
      // A non-2xx response here always means the token itself was
      // rejected (invalid/expired) - client-side validation never
      // reaches the API call.
      setTokenError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="form-field">
        <span>New Password</span>
        <input
          type="password"
          name="newPassword"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          placeholder="Enter a new password"
          required
        />
      </label>

      <label className="form-field">
        <span>Confirm New Password</span>
        <input
          type="password"
          name="confirmPassword"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          placeholder="Re-enter your new password"
          required
        />
      </label>

      {error && <p className="error-text">{error}</p>}

      <button
        className="button button--primary button--lg button--wide"
        type="submit"
        disabled={loading}
      >
        {loading ? "Resetting..." : "Reset Password"}
      </button>

      {tokenError && (
        <p className="auth-form-footer">
          Link expired or invalid?{" "}
          <Link to="/forgot-password">Request a new one</Link>
        </p>
      )}
    </form>
  );
}

export default ResetPasswordForm;
