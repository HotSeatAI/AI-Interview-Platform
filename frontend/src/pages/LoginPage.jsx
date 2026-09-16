import AuthLayout from "../components/auth/AuthLayout.jsx";
import LoginForm from "../components/auth/LoginForm.jsx";
import usePageMeta from "../hooks/usePageMeta";

const SESSION_DOTS = [1, 1, 1, 1, 1, 1, 0, 0];

function LoginPage() {
  usePageMeta("Log In", "Log in to your HotSeat account to continue practicing interviews.");

  return (
    <AuthLayout
      eyebrow="SESSION LOG"
      headline="Every rep gets you closer."
      body="Pick up where you left off — your resume, your history, your next scheduled interview are all waiting."
      preview={
        <div className="auth-preview-card">
          <div className="auth-preview-card__row">
            <span className="auth-preview-card__role">Backend Engineer</span>
            <span className="auth-preview-card__score">85</span>
          </div>
          <div className="auth-preview-card__dots">
            {SESSION_DOTS.map((done, index) => (
              <span
                key={index}
                className={`auth-preview-dot ${done ? "auth-preview-dot--done" : ""}`}
              />
            ))}
          </div>
          <div className="auth-preview-card__meta">
            6 of 8 questions · last practiced 2 days ago
          </div>
        </div>
      }
    >
      <div className="eyebrow">WELCOME BACK</div>
      <h1 className="auth-form-col__headline">Log in to HotSeat</h1>
      <p className="auth-form-col__sub">Sign in to continue preparing for your next interview.</p>
      <LoginForm />
    </AuthLayout>
  );
}

export default LoginPage;
