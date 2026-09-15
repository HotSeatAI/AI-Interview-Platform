import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";

import useAuth from "../hooks/useAuth";
import { confirmEmailChange } from "../api/profileApi";

function ConfirmEmailChangePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [status, setStatus] = useState("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("error");
      setMessage("Invalid confirmation link.");
      return;
    }

    async function confirm() {
      try {
        const response = await confirmEmailChange(token);

        setStatus("success");
        setMessage(response.message);

        // The JWT's sub claim is the old email - it can no longer
        // resolve this user, so the current session is already
        // dead. Clear it locally and send the user to log back in.
        logout();
      } catch (error) {
        setStatus("error");

        setMessage(
          error.response?.data?.detail || "Unable to confirm email change."
        );
      }
    }

    confirm();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div className="verify-page">
      <div className="verify-page__header">
        <div className="eyebrow">EMAIL CHANGE</div>
        <h2>Confirming your new email</h2>
      </div>

      {status === "loading" && (
        <div className="verify-card">
          <p className="verify-card__body">Please wait while we confirm your new email…</p>
        </div>
      )}

      {status === "success" && (
        <div className="verify-card">
          <span className="verify-card__tag verify-card__tag--success">SUCCESS</span>
          <span className="verify-card__icon verify-card__icon--success" />
          <h3 className="verify-card__title">Email updated</h3>
          <p className="verify-card__body">{message}</p>
          <button
            type="button"
            className="button button--primary"
            onClick={() => navigate("/login", { replace: true })}
          >
            Go to login
          </button>
        </div>
      )}

      {status === "error" && (
        <div className="verify-card">
          <span className="verify-card__tag verify-card__tag--error">ERROR</span>
          <span className="verify-card__icon verify-card__icon--error" />
          <h3 className="verify-card__title">Confirmation failed</h3>
          <p className="verify-card__body">{message}</p>
          <Link to="/settings" className="button button--secondary">
            Back to settings
          </Link>
        </div>
      )}
    </div>
  );
}

export default ConfirmEmailChangePage;
