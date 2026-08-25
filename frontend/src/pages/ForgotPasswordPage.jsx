import AuthLayout from "../components/auth/AuthLayout.jsx";
import ForgotPasswordForm from "../components/auth/ForgotPasswordForm.jsx";

function ForgotPasswordPage() {
  return (
    <AuthLayout
      eyebrow="ACCOUNT RECOVERY"
      headline="It happens to everyone."
      body="Enter the email on your account and we'll send you a link to get back in."
    >
      <div className="eyebrow">FORGOT PASSWORD</div>
      <h1 className="auth-form-col__headline">Forgot Password?</h1>
      <p className="auth-form-col__sub">
        We'll email you a link to reset your password.
      </p>
      <ForgotPasswordForm />
    </AuthLayout>
  );
}

export default ForgotPasswordPage;
