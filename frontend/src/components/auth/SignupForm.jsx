import { useState } from "react";
import { Link } from "react-router-dom";
import useAuth from "../../hooks/useAuth";
import GoogleLoginButton from "./GoogleLoginButton";
import Button from "../ui/Button";
function SignupForm() {
  const { signup } = useAuth();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    try {
      await signup(formData);

      setSuccess(true);

  } catch (err) {

      setError(
        err.friendlyMessage ||
        err.response?.data?.detail ||
        "Signup failed."
    );
  }
};

  if (success) {
    return (
      <div className="verify-card">
        <span className="verify-card__tag verify-card__tag--success">SUCCESS</span>
        <span className="verify-card__icon verify-card__icon--success" />
        <h3 className="verify-card__title">Account created</h3>
        <p className="verify-card__body">
          Check your email to verify your account before logging in.
        </p>
        <Button to="/login">Go to login</Button>
      </div>
    );
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <label className="form-field">
        <span>Name</span>
        <input
          type="text"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="Your name"
          required
        />
      </label>

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
          placeholder="Create a password"
          required
        />
      </label>

      {error && <p className="error-text">{error}</p>}

      <Button type="submit" fullWidth>
        Create account
      </Button>

      <div className="auth-divider">
        <span className="auth-divider__line" />
        <span className="auth-divider__text">OR</span>
        <span className="auth-divider__line" />
      </div>

      <GoogleLoginButton />

      <p className="auth-form-footer">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </form>
  );
}

export default SignupForm;
