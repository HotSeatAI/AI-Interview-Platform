import { Link } from "react-router-dom";
import BrandLogo from "../components/layout/BrandLogo";
import usePageMeta from "../hooks/usePageMeta";
import { PRIVACY_LAST_UPDATED, PRIVACY_SECTIONS } from "../constants/privacyContent";

function PrivacyPolicyPage() {
  usePageMeta("Privacy Policy", "How HotSeat collects, uses, and protects your data.");

  return (
    <div className="legal-page">
      <header className="legal-page__header">
        <Link to="/" className="legal-page__brand">
          <BrandLogo />
        </Link>
      </header>

      <main className="legal-page__container">
        <div className="eyebrow">LEGAL</div>
        <h1>Privacy Policy</h1>
        <p className="terms-modal-updated">Last updated: {PRIVACY_LAST_UPDATED}</p>

        <div className="terms-modal-body legal-page__body">
          {PRIVACY_SECTIONS.map((section) => (
            <div className="terms-modal-section" key={section.heading}>
              <h3>{section.heading}</h3>
              <p>{section.body}</p>
            </div>
          ))}
        </div>

        <Link to="/" className="legal-page__back">
          ← Back to home
        </Link>
      </main>
    </div>
  );
}

export default PrivacyPolicyPage;
