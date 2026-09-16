import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import BrandLogo from "../components/layout/BrandLogo";
import Button from "../components/ui/Button";
import ThemeToggle from "../components/layout/ThemeToggle";
import MobileNavToggle from "../components/layout/MobileNavToggle";
import usePageMeta from "../hooks/usePageMeta";
import heroPhotoWebp from "../assets/landing-hero.webp";
import heroPhotoJpg from "../assets/landing-hero.jpg";
import ctaPhotoWebp from "../assets/landing-cta.webp";
import ctaPhotoJpg from "../assets/landing-cta.jpg";

const FEATURES = [
  {
    num: "01",
    title: "Questions built from your resume",
    body: "Upload a PDF and HotSeat parses it — your projects, your stack, your experience — then generates questions that could only be asked of you, not a generic candidate.",
    visual: (
      <div className="mini-card">
        <div className="mini-card__label">RESUME.PDF</div>
        <div className="mini-card__tags">
          <span className="mini-tag">React</span>
          <span className="mini-tag">PostgreSQL</span>
          <span className="mini-tag">FastAPI</span>
        </div>
        <div className="mini-card__arrow">↓ generates</div>
        <p className="mini-card__question">
          "Tell me about the FastAPI service you scaled last summer."
        </p>
      </div>
    ),
  },
  {
    num: "02",
    title: "Follow-ups when it counts",
    body: "Score below the bar on any answer, and HotSeat digs in with a targeted follow-up before moving on — the same way a sharp interviewer would.",
    visual: (
      <div className="mini-card">
        <div className="follow-chain">
          <span className="follow-node follow-node--primary">Q3 · Primary</span>
          <span className="follow-line" />
          <span className="follow-node follow-node--followup">Q3a · Follow-up</span>
        </div>
        <p className="mini-card__question">
          "You said it was O(n log n) — can you prove that bound?"
        </p>
      </div>
    ),
  },
  {
    num: "03",
    title: "Voice, text and code — one answer",
    body: "Explain your reasoning out loud, add notes in writing, then implement it in a full Monaco editor with real execution. All three are graded as a single response.",
    visual: (
      <div className="mini-card">
        <div className="mini-card__modes">
          <span className="mode-pill">Voice</span>
          <span className="mode-pill">Text</span>
          <span className="mode-pill">Code</span>
        </div>
        <div className="mini-card__arrow">↓ combined &amp; evaluated</div>
        <p className="mini-card__question">One score. One set of strengths and gaps.</p>
      </div>
    ),
  },
  {
    num: "04",
    title: "Every session, tracked",
    body: "Full history of past interviews, question-by-question feedback, and scores over time — so you can see exactly what's improving before the real thing.",
    visual: (
      <div className="mini-card">
        <div className="mini-history-row">
          <span>Backend Engineer</span>
          <span className="mini-history-score">78</span>
        </div>
        <div className="mini-history-row">
          <span>Backend Engineer</span>
          <span className="mini-history-score">85</span>
        </div>
        <div className="mini-history-row">
          <span>Backend Engineer</span>
          <span className="mini-history-score">91</span>
        </div>
      </div>
    ),
  },
  {
    num: "05",
    title: "Know where your resume falls short",
    body: "Paste a job description and HotSeat scores your resume against it requirement by requirement — what you already cover, what's missing, and exactly what to add or rewrite before you apply.",
    visual: (
      <div className="mini-card">
        <div className="mini-card__match-score">
          <span className="mini-card__match-num">74%</span>
          <span className="mini-card__match-label">MATCH TO JOB DESCRIPTION</span>
        </div>
        <div className="mini-match-list">
          <div className="mini-match-row">
            <span>System design experience</span>
            <span className="mini-badge mini-badge--met">Covered</span>
          </div>
          <div className="mini-match-row">
            <span>Kubernetes / container orchestration</span>
            <span className="mini-badge mini-badge--gap">Add this</span>
          </div>
          <div className="mini-match-row">
            <span>Led a team of engineers</span>
            <span className="mini-badge mini-badge--met">Covered</span>
          </div>
        </div>
      </div>
    ),
  },
];

const STEPS = [
  { num: "01", title: "Upload your resume", body: "Drop a PDF. HotSeat extracts your projects, stack and experience." },
  { num: "02", title: "Configure the interview", body: "Choose a role and difficulty. Software, finance, consulting, sales or marketing." },
  { num: "03", title: "Enter the HotSeat", body: "Get a live session built around what you actually said you did." },
  { num: "04", title: "Answer and adapt", body: "Speak, write, or code your answer. Weak spots get a follow-up on the spot." },
  { num: "05", title: "Review your report", body: "Scores, strengths and gaps for every question, saved to your history." },
];

function LandingPage() {
  usePageMeta(
    "AI Interview Platform",
    "HotSeat is an AI-powered platform for practicing job interviews and getting instant feedback."
  );

  const heroRef = useRef(null);
  const [showStickyCta, setShowStickyCta] = useState(false);

  useEffect(() => {
    const hero = heroRef.current;
    if (!hero) return;

    const observer = new IntersectionObserver(
      ([entry]) => setShowStickyCta(!entry.isIntersecting),
      { threshold: 0 }
    );

    observer.observe(hero);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="landing">
      <header className="landing__nav">
        <a href="#top" className="landing__brand">
          <BrandLogo />
        </a>
        <MobileNavToggle>
          <nav className="landing__nav-links">
            <a href="#features" className="landing__nav-link">
              Product
            </a>
            <a href="#how-it-works" className="landing__nav-link">
              How it works
            </a>
            <Link to="/login" className="landing__nav-link">
              Log in
            </Link>
            <Button to="/signup" variant="primary" size="sm">
              Start practicing
            </Button>
            <ThemeToggle />
          </nav>
        </MobileNavToggle>
      </header>

      <section id="top" className="landing__hero" ref={heroRef}>
        <picture>
          <source srcSet={heroPhotoWebp} type="image/webp" />
          <img src={heroPhotoJpg} alt="" className="landing__hero-photo" />
        </picture>
        <div className="landing__hero-scrim" />

        <div className="landing__hero-grid">
          <div className="landing__hero-copy">
            <div className="eyebrow">AI INTERVIEW PREPARATION</div>
            <h1 className="landing__headline">
              The interview platform built from your actual resume.
            </h1>
            <p className="landing__sub">
              Real questions on your projects and stack, follow-ups that probe when
              you're vague, and a live coding editor that grades the work.
            </p>
            <div className="landing__actions">
              <Button to="/signup" variant="primary">
                Start practicing free
              </Button>
              <Button href="#how-it-works" variant="secondary">
                See how it works
              </Button>
            </div>
            <div className="landing__meta">
              Resume-tailored · Voice, text &amp; code · Adaptive follow-ups
            </div>
          </div>
        </div>
      </section>

      <div className="landing__mono-strip">
        RESUME-TAILORED &nbsp;·&nbsp; VOICE, TEXT &amp; CODE &nbsp;·&nbsp; ADAPTIVE FOLLOW-UPS
      </div>

      <section id="features" className="landing__features">
        <div className="section-header">
          <div className="eyebrow">THE INTERVIEW LOOP</div>
          <h2>Five ways the interview adapts to you.</h2>
        </div>

        {FEATURES.map((feature, index) => (
          <div
            key={feature.num}
            className={`feature-row ${index % 2 === 1 ? "feature-row--reverse" : ""}`}
          >
            <div className="feature-row__num">{feature.num}</div>
            <div className="feature-row__text">
              <h3>{feature.title}</h3>
              <p>{feature.body}</p>
            </div>
            <div className="feature-row__visual">{feature.visual}</div>
          </div>
        ))}
      </section>

      <section id="how-it-works" className="landing__how">
        <div className="section-header section-header--centered">
          <div className="eyebrow">BUILT FOR PRACTICE</div>
          <h2>From resume to report in five steps.</h2>
        </div>
        <div className="landing__steps-grid">
          {STEPS.map((step) => (
            <div key={step.num} className="step-card">
              <div className="step-card__num">{step.num}</div>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="landing__final-cta">
        <div className="landing__final-cta-copy">
          <div className="eyebrow">READY WHEN YOU ARE</div>
          <h2>Your next interview starts here.</h2>
          <p>Upload a resume, pick a role, and take a full interview in the next ten minutes.</p>
          <Button to="/signup" variant="primary" className="landing__cta--large landing__cta--lime">
            Enter the HotSeat
          </Button>
        </div>
        <picture>
          <source srcSet={ctaPhotoWebp} type="image/webp" />
          <img src={ctaPhotoJpg} alt="" className="landing__final-cta-photo" />
        </picture>
      </section>

      <footer className="landing__footer">
        <span className="landing__footer-brand">
          <BrandLogo />
        </span>
        <span className="landing__footer-beta">
          HotSeat is in BETA — features and scoring are still being tuned.
        </span>
        <span className="landing__footer-copy">
          © 2026 HotSeat. Practice with intent. · <Link to="/privacy">Privacy Policy</Link>
        </span>
      </footer>

      <div
        className={`landing__sticky-cta ${
          showStickyCta ? "landing__sticky-cta--visible" : ""
        }`}
      >
        <Button to="/signup" variant="primary" fullWidth>
          Start practicing free
        </Button>
      </div>
    </div>
  );
}

export default LandingPage;
