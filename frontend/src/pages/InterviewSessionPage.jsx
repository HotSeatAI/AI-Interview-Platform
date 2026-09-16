import { useEffect, useState , useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getInterviewSession, finishInterviewSession, submitSessionFeedback } from "../api/interviewApi";
import { generateFollowUp } from "../api/answerApi";
import useAuth from "../hooks/useAuth";

import QuestionCard from "../components/interview/QuestionCard";
import AnswerBox from "../components/interview/AnswerBox";
import FeedbackCard from "../components/interview/FeedbackCard";
import BrandLogo from "../components/layout/BrandLogo";
import ThemeToggle from "../components/layout/ThemeToggle";
import DeliveryConsentModal from "../components/interview/DeliveryConsentModal";
import PreInterviewDisclaimerModal from "../components/interview/PreInterviewDisclaimerModal";
import ExitFeedbackModal from "../components/interview/ExitFeedbackModal";
import DeliveryCalibrationScreen from "../components/interview/DeliveryCalibrationScreen";
import WebcamMonitor from "../components/interview/WebcamMonitor";
import { createAudioDeliveryAnalyzer } from "../utils/audioDeliveryAnalyzer";
import { createVideoDeliveryAnalyzer } from "../utils/videoDeliveryAnalyzer";
import usePageMeta from "../hooks/usePageMeta";

const CALIBRATION_MS = 3000;

function InterviewSessionPage() {
  usePageMeta("Live Interview", "Answer live interview questions by voice, text, or code and get evaluated.");

  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const answerBoxRef = useRef(null);

  const [session, setSession] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [answeredQuestions, setAnsweredQuestions] = useState(new Set());
  const [feedbackMap, setFeedbackMap] = useState({});
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [disclaimerAcknowledged, setDisclaimerAcknowledged] = useState(false);
  const [showExitFeedback, setShowExitFeedback] = useState(false);
  // True while the on-demand follow-up check/generation triggered by
  // "Next"/"Finish" is in flight - see maybeGenerateFollowUp. Whether
  // a follow-up exists isn't known until this resolves (it's no
  // longer generated synchronously during answer submission).
  const [generatingFollowUp, setGeneratingFollowUp] = useState(false);

  // null = undecided (show consent modal), true/false once decided.
  const [deliveryConsent, setDeliveryConsent] = useState(null);
  const [calibrating, setCalibrating] = useState(false);
  const [webcamStream, setWebcamStream] = useState(null);
  const audioAnalyzerRef = useRef(null);
  const videoAnalyzerRef = useRef(null);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        setLoading(true);

        const data = await getInterviewSession(sessionId, token);

        setSession(data);

        const answered = new Set();
        const feedbacks = {};

        data.questions.forEach((question) => {
          if (question.answered) {
            answered.add(question.id);

            feedbacks[question.id] = {
              score: question.score,
              feedback: question.feedback,
              strengths: question.strengths,
              improvements: question.improvements,
            };
          }
        });

        setAnsweredQuestions(answered);
        setFeedbackMap(feedbacks);

        const firstUnanswered = data.questions.findIndex(
          (question) => !question.answered
        );

        if (firstUnanswered !== -1) {
          setCurrentQuestionIndex(firstUnanswered);
        }

      } catch (err) {

        setError(
          err?.response?.data?.detail ||
          "Failed to load interview session."
        );

      } finally {

        setLoading(false);

      }
    };

    fetchSession();
  }, [sessionId, token]);

  useEffect(() => {
    return () => {
      audioAnalyzerRef.current?.stop();
      audioAnalyzerRef.current = null;

      videoAnalyzerRef.current?.stop();
      videoAnalyzerRef.current = null;

      setWebcamStream(null);
    };
  }, []);

  // Delivery signals are scoped per-question - clear counters whenever
  // the visible question changes (submitted, skipped, or navigated
  // back), so one question's pauses never bleed into the next.
  useEffect(() => {
    audioAnalyzerRef.current?.reset();
    videoAnalyzerRef.current?.reset();
  }, [currentQuestionIndex]);

  const handleContinueDelivery = async ({ audioEnabled, videoEnabled }) => {
    let anyEnabled = false;

    if (audioEnabled) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

        const analyzer = createAudioDeliveryAnalyzer();
        await analyzer.start(stream);

        audioAnalyzerRef.current = analyzer;
        anyEnabled = true;
      } catch (err) {
        console.log("Delivery-analysis mic access failed:", err);
      }
    }

    if (videoEnabled) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });

        const analyzer = createVideoDeliveryAnalyzer();
        await analyzer.start(stream);

        videoAnalyzerRef.current = analyzer;
        setWebcamStream(stream);
        anyEnabled = true;
      } catch (err) {
        console.log("Delivery-analysis camera access failed:", err);
      }
    }

    if (anyEnabled) {
      setCalibrating(true);

      await Promise.all(
        [audioAnalyzerRef.current, videoAnalyzerRef.current]
          .filter(Boolean)
          .map((analyzer) => analyzer.calibrate(CALIBRATION_MS))
      );

      setCalibrating(false);
    }

    setDeliveryConsent(anyEnabled);
  };

  const handleDeclineDelivery = () => {
    setDeliveryConsent(false);
  };

  const handleRecordingStateChange = (isActive) => {
    audioAnalyzerRef.current?.setActive(isActive);
  };

  // Called once, synchronously, right as the user clicks Submit (see
  // AnswerBox.handleSubmit) - snapshots signals for this answer, then
  // stops audio tracking so any time spent AFTER submitting never
  // leaks into the next question's counters. isCoding excludes audio
  // entirely: while writing code the candidate isn't expected to be
  // talking continuously, so pause/pitch signals would just be noise
  // (a real gap while coding gets misread as a "long pause").
  const getDeliverySignals = (isCoding) => {
    if (!deliveryConsent) return null;

    const audioSignals = isCoding
      ? undefined
      : audioAnalyzerRef.current?.getSignalsSinceReset();
    const videoSignals = videoAnalyzerRef.current?.getSignalsSinceReset();

    audioAnalyzerRef.current?.setActive(false);

    if (!audioSignals && !videoSignals) return null;

    return { ...audioSignals, ...videoSignals };
  };

  if (loading) {
    return <div className="page-loading">Loading interview…</div>;
  }

  if (error) {
    return <div className="page-error">{error}</div>;
  }

  // True the instant the consent/calibration gate resolves either way
  // (declined outright, or calibration finished after accepting) -
  // questions should never be spoken aloud while that overlay is up.
  const interviewReady = disclaimerAcknowledged && deliveryConsent !== null && !calibrating;

  const currentQuestion =
    session.questions[currentQuestionIndex];

  const currentFeedback =
    feedbackMap[currentQuestion.id];

  const mainQuestions = session.questions.filter(
    (question) => !question.is_follow_up
  );

  const totalMainQuestions = mainQuestions.length;

  const currentMainQuestionNumber =
    session.questions
      .slice(0, currentQuestionIndex + 1)
      .filter(
        (question) => !question.is_follow_up
      ).length;

  const currentMainIndex = currentMainQuestionNumber - 1;

      const handleAnswerSubmitted = (response) => {
  setFeedbackMap((prev) => ({
    ...prev,
    [currentQuestion.id]: {
      answerId: response.answer_id,
      score: response.score,
      feedback: response.feedback,
      strengths: response.strengths,
      improvements: response.improvements,
      deliveryFeedback: response.delivery_feedback,
      modelAnswer: response.model_answer,
      deliverySignals: response.delivery_signals,
      // Whether this question qualifies for a follow-up - the
      // follow-up question itself isn't generated yet. It's
      // generated on demand in maybeGenerateFollowUp, triggered by
      // "Next Question"/"Finish Interview", so that latency lands
      // after the user has already seen their score/feedback
      // instead of adding to it.
      eligibleForFollowUp: response.eligible_for_follow_up,
    },
  }));

  setAnsweredQuestions((prev) => {
    const updated = new Set(prev);
    updated.add(currentQuestion.id);
    return updated;
  });
};

// Generates the follow-up for the just-answered current question, if
// it's eligible, and splices it into the live question list right
// after the current one. Returns true if a follow-up was added, so
// callers know a "next question" now definitely exists even though
// `session`/`currentQuestionIndex` in their own closure may still be
// stale (React state updates from the splice above aren't visible
// until the next render). Soft-fails like every other bonus-content
// call in this app - a failure here must never block the user from
// moving on.
const maybeGenerateFollowUp = async () => {
  const feedback = feedbackMap[currentQuestion.id];

  if (!feedback?.eligibleForFollowUp) return false;

  setGeneratingFollowUp(true);

  try {
    const followUp = await generateFollowUp(feedback.answerId, token);

    setSession((prevSession) => {
      const updatedQuestions = [...prevSession.questions];

      updatedQuestions.splice(
        currentQuestionIndex + 1,
        0,
        {
          id: followUp.question_id,
          question_text: followUp.question_text,
          question_type: followUp.question_type,
          follow_up_depth: followUp.follow_up_depth,
          is_follow_up: true,
          answered: false,
        }
      );

      return {
        ...prevSession,
        questions: updatedQuestions,
      };
    });

    setFeedbackMap((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        ...prev[currentQuestion.id],
        eligibleForFollowUp: false,
      },
    }));

    return true;
  } catch (err) {
    console.log("Follow-up generation failed:", err);
    return false;
  } finally {
    setGeneratingFollowUp(false);
  }
};

const handlePrevious = () => {
  if (currentQuestionIndex > 0) {

    setCurrentQuestionIndex((prev) => prev - 1);

  }
};

// `session.questions.length` read after the await may be stale (see
// maybeGenerateFollowUp) - `followUpAdded` is the source of truth
// when it's true, since the splice guarantees a question now exists
// right after this one regardless of what the stale closure shows.
const handleNext = async () => {
  const followUpAdded = await maybeGenerateFollowUp();

  if (followUpAdded || currentQuestionIndex < session.questions.length - 1) {

    setCurrentQuestionIndex((prev) => prev + 1);

  }
};

// Bound to the "Finish Interview" button - that button only ever
// renders on what looked like the last question, but a follow-up can
// still turn out to be eligible for it. Check/generate first; only
// actually finish if nothing was added.
const handleFinishOrContinue = async () => {
  const followUpAdded = await maybeGenerateFollowUp();

  if (followUpAdded) {
    setCurrentQuestionIndex((prev) => prev + 1);
    return;
  }

  await handleFinishInterview();
};

const handleFinishInterview = async () => {
  try {
    await finishInterviewSession(sessionId, token);
  } catch (err) {
    // Fail-soft - a network hiccup here shouldn't block the user from
    // seeing their results; worst case the results page later shows
    // the "not finished" warning if this never actually landed.
    console.log("Failed to mark interview as finished:", err);
  }

  navigate(`/results/${sessionId}`, {
    state: {
      role: session.role,
      difficulty: session.difficulty,
      round: session.round,
      createdAt: session.created_at,
      questions: session.questions,
      feedbackMap,
    },
  });
};

const isLastQuestion = currentQuestionIndex === session.questions.length - 1;
const isCurrentAnswered = answeredQuestions.has(currentQuestion.id);

const handleExitFeedbackSubmit = async (payload) => {
  await submitSessionFeedback(sessionId, payload, token);
  navigate("/dashboard");
};

const handleExitSkip = () => {
  navigate("/dashboard");
};

return (
  <div className="workspace">
    {!disclaimerAcknowledged && (
      <PreInterviewDisclaimerModal
        onAcknowledge={() => setDisclaimerAcknowledged(true)}
      />
    )}

    {disclaimerAcknowledged && deliveryConsent === null && !calibrating && (
      <DeliveryConsentModal
        onContinue={handleContinueDelivery}
        onDecline={handleDeclineDelivery}
      />
    )}

    {calibrating && (
      <DeliveryCalibrationScreen durationMs={CALIBRATION_MS} />
    )}

    <WebcamMonitor stream={webcamStream} />

    <header className="workspace-topbar">
      <Link to="/dashboard" className="workspace-topbar__brand">
        <BrandLogo />
      </Link>

      <div className="workspace-topbar__progress">
        <div className="workspace-topbar__progress-text">
          Question {currentMainQuestionNumber} of {totalMainQuestions} · {session.role} ·{" "}
          {session.difficulty}
        </div>
        <div className="workspace-topbar__dots">
          {mainQuestions.map((question, index) => {
            let state = "open";
            if (index === currentMainIndex) {
              state = "current";
            } else if (answeredQuestions.has(question.id)) {
              state = "done";
            }
            return (
              <span
                key={question.id}
                className={`workspace-dot workspace-dot--${state}`}
              />
            );
          })}
        </div>
      </div>

      <div className="workspace-topbar__actions">
        <ThemeToggle />
        <button
          type="button"
          className="workspace-topbar__exit"
          onClick={() => setShowExitFeedback(true)}
        >
          Exit interview
        </button>
      </div>
    </header>

    {showExitFeedback && (
      <ExitFeedbackModal
        onSubmit={handleExitFeedbackSubmit}
        onSkip={handleExitSkip}
      />
    )}

    <main className="workspace-main">
      <QuestionCard
        questionText={currentQuestion.question_text}
        isFollowUp={currentQuestion.is_follow_up}
        ttsEnabled={interviewReady}
      />

      <AnswerBox
        ref={answerBoxRef}
        key={currentQuestion.id}
        questionId={currentQuestion.id}
        isCoding={currentQuestion.question_type === "coding"}
        disabled={answeredQuestions.has(currentQuestion.id)}
        onAnswerSubmitted={handleAnswerSubmitted}
        onSubmittingChange={setIsSubmittingAnswer}
        getDeliverySignals={getDeliverySignals}
        onRecordingStateChange={handleRecordingStateChange}
      />

      {currentFeedback && (
        <FeedbackCard {...currentFeedback} />
      )}
    </main>

    <footer className="workspace-actionbar">
      <button
        className="button button--secondary"
        onClick={handlePrevious}
        disabled={currentQuestionIndex === 0}
      >
        ← Previous
      </button>

      <div className="workspace-actionbar__right">
        {!isCurrentAnswered ? (
          <button
            className="button button--primary"
            onClick={() => answerBoxRef.current?.submit()}
            disabled={isSubmittingAnswer}
          >
            {isSubmittingAnswer ? "Submitting..." : "Submit answer"}
          </button>
        ) : isLastQuestion ? (
          <button
            className="button button--primary"
            onClick={handleFinishOrContinue}
            disabled={generatingFollowUp}
          >
            {generatingFollowUp ? "Checking for follow-up..." : "Finish Interview"}
          </button>
        ) : (
          <button
            className="button button--primary"
            onClick={handleNext}
            disabled={generatingFollowUp}
          >
            {generatingFollowUp ? "Checking for follow-up..." : "Next Question →"}
          </button>
        )}
      </div>
    </footer>
  </div>
);
}

export default InterviewSessionPage;
