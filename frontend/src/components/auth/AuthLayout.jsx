import { Link } from "react-router-dom";
import BrandLogo from "../layout/BrandLogo";
import ThemeToggle from "../layout/ThemeToggle";

function AuthLayout({ eyebrow, headline, body, preview, children }) {
  return (
    <div className="auth-screen">
      <div className="auth-screen__left">
        <Link to="/" className="auth-screen__brand">
          <BrandLogo />
        </Link>

        <div className="auth-screen__left-content">
          <div className="eyebrow">{eyebrow}</div>
          <h2 className="auth-screen__headline">{headline}</h2>
          <p className="auth-screen__body">{body}</p>
          {preview}
        </div>

        <div className="auth-screen__left-meta">HOTSEAT · INTERVIEW WORKSPACE</div>
      </div>

      <div className="auth-screen__right">
        <ThemeToggle className="auth-screen__theme-toggle" />
        <div className="auth-form-col">{children}</div>
      </div>
    </div>
  );
}

export default AuthLayout;
