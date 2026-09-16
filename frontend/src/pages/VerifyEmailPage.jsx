import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import apiClient from "../api/client";
import usePageMeta from "../hooks/usePageMeta";

function VerifyEmailPage() {
  usePageMeta("Verify Email", "Verify your email address to activate your HotSeat account.");

  const [searchParams] = useSearchParams();

  const [status, setStatus] = useState("loading");

  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setStatus("error");
      setMessage("Invalid verification link.");
      return;
    }

    async function verifyEmail() {
      try {
        const response = await apiClient.get(
          `/auth/verify-email?token=${token}`
        );

        setStatus("success");
        setMessage(response.data.message);
      } catch (error) {
        setStatus("error");

        setMessage(
          error.response?.data?.detail ||
          "Unable to verify email."
        );
      }
    }

    verifyEmail();

  }, [searchParams]);

  return (
    <div className="verify-page">
      <div className="verify-page__header">
        <div className="eyebrow">EMAIL VERIFICATION</div>
        <h2>Confirming your account</h2>
      </div>

      {status === "loading" && (
        <div className="verify-card">
          <p className="verify-card__body">Please wait while we verify your email…</p>
        </div>
      )}

      {status === "success" && (
        <div className="verify-card">
          <span className="verify-card__tag verify-card__tag--success">SUCCESS</span>
          <span className="verify-card__icon verify-card__icon--success" />
          <h3 className="verify-card__title">Email verified</h3>
          <p className="verify-card__body">{message}</p>
          <Link to="/login" className="button button--primary">
            Go to login
          </Link>
        </div>
      )}

      {status === "error" && (
        <div className="verify-card">
          <span className="verify-card__tag verify-card__tag--error">ERROR</span>
          <span className="verify-card__icon verify-card__icon--error" />
          <h3 className="verify-card__title">Verification failed</h3>
          <p className="verify-card__body">{message}</p>
          <Link to="/signup" className="button button--secondary">
            Back to signup
          </Link>
        </div>
      )}
    </div>
  );
}

export default VerifyEmailPage;
