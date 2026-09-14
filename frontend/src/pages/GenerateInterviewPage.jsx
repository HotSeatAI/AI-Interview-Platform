import InterviewGeneratorForm from "../components/interview/InterviewGeneratorForm.jsx";
import Navbar from "../components/layout/Navbar.jsx";

const STEPS = [
  "Pick the role you want to practice for - HotSeat tailors questions to it.",
  "Attach a resume so questions probe your actual projects and stack.",
  "Choose a difficulty; you can adjust it on your next session anytime.",
];

function GenerateInterviewPage() {
  return (
    <div className="generate-page">
      <Navbar />
      <main className="generate-container">
        <div className="auth-screen__left">
          <div className="auth-screen__left-content">
            <div className="eyebrow" style={{ color: "var(--slab-accent)" }}>
              INTERVIEW SETUP
            </div>
            <h1 className="auth-screen__headline">Configure your session</h1>
            <p className="auth-screen__body">
              HotSeat will generate a resume-tailored interview for the role
              and difficulty you choose below.
            </p>

            <ol className="slab-explainer-list">
              {STEPS.map((step, index) => (
                <li className="slab-explainer-item" key={step}>
                  <span className="slab-explainer-index">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="slab-explainer-text">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>

        <div className="auth-screen__right">
          <div className="generate-card">
            <InterviewGeneratorForm />
          </div>
        </div>
      </main>
    </div>
  );
}

export default GenerateInterviewPage;
