import { useState } from "react";
import { Link } from "react-router-dom";

import { forgotPassword } from "../../api/authApi";

const GENERIC_SUCCESS_MESSAGE =
  "If an eligible account exists for this email, password reset instructions have been sent.";

function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await forgotPassword(email);
      setSubmitted(true);
    } catch (err) {
      // The backend never signals whether the account exists -
      // this only fires for genuine network/server failures.
      setError(
        err.response?.data?.detail ||
        "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="auth-form">
        <p className="success-text">{GENERIC_SUCCESS_MESSAGE}</p>

        <Link to="/login" className="button button--primary button--lg button--wide">
          Back to login
        </Link>
      </div>
    );
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="form-field">
        <span>Email</span>
        <input
          type="email"
          name="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
          required
        />
      </label>

      {error && <p className="error-text">{error}</p>}

      <button
        className="button button--primary button--lg button--wide"
        type="submit"
        disabled={loading}
      >
        {loading ? "Sending..." : "Send Reset Link"}
      </button>

      <p className="auth-form-footer">
        Remembered your password? <Link to="/login">Log in</Link>
      </p>
    </form>
  );
}

export default ForgotPasswordForm;
