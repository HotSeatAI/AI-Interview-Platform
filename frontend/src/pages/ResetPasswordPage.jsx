import AuthLayout from "../components/auth/AuthLayout.jsx";
import ResetPasswordForm from "../components/auth/ResetPasswordForm.jsx";

function ResetPasswordPage() {
  return (
    <AuthLayout
      eyebrow="ACCOUNT RECOVERY"
      headline="Almost there."
      body="Choose a new password to get back into your workspace."
    >
      <div className="eyebrow">RESET PASSWORD</div>
      <h1 className="auth-form-col__headline">Set a new password</h1>
      <p className="auth-form-col__sub">
        Enter and confirm your new password below.
      </p>
      <ResetPasswordForm />
    </AuthLayout>
  );
}

export default ResetPasswordPage;
