import AuthLayout from "../components/auth/AuthLayout.jsx";
import SignupForm from "../components/auth/SignupForm.jsx";
import usePageMeta from "../hooks/usePageMeta";

const MATCH_ROWS = [
  { label: "System design experience", badge: "Covered", tone: "met" },
  { label: "Kubernetes / containers", badge: "Add this", tone: "gap" },
];

function SignupPage() {
  usePageMeta("Sign Up", "Create a free HotSeat account and start practicing interviews today.");

  return (
    <AuthLayout
      eyebrow="GETTING STARTED"
      headline="Built from what you've built."
      body="Upload a resume once. Every interview after that is generated around your actual experience."
      preview={
        <div className="auth-preview-card">
          <div className="auth-preview-card__row">
            <span className="auth-preview-card__role">Resume match</span>
            <span className="auth-preview-card__score">74%</span>
          </div>
          <div className="auth-match-list">
            {MATCH_ROWS.map((row) => (
              <div key={row.label} className="auth-match-row">
                <span>{row.label}</span>
                <span className={`auth-badge auth-badge--${row.tone}`}>{row.badge}</span>
              </div>
            ))}
          </div>
          <div className="auth-preview-card__meta">against target job description</div>
        </div>
      }
    >
      <div className="eyebrow">CREATE ACCOUNT</div>
      <h1 className="auth-form-col__headline">Set up your workspace</h1>
      <p className="auth-form-col__sub">
        Get set up for resume-based interview practice in under a minute.
      </p>
      <SignupForm />
    </AuthLayout>
  );
}

export default SignupPage;
