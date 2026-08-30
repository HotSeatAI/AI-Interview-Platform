import { useEffect, useState , useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getInterviewSession, finishInterviewSession } from "../api/interviewApi";
import useAuth from "../hooks/useAuth";

import QuestionCard from "../components/interview/QuestionCard";
import AnswerBox from "../components/interview/AnswerBox";
import FeedbackCard from "../components/interview/FeedbackCard";
import BrandLogo from "../components/layout/BrandLogo";
import ThemeToggle from "../components/layout/ThemeToggle";
import DeliveryConsentModal from "../components/interview/DeliveryConsentModal";
import DeliveryCalibrationScreen from "../components/interview/DeliveryCalibrationScreen";
import WebcamMonitor from "../components/interview/WebcamMonitor";
import { createAudioDeliveryAnalyzer } from "../utils/audioDeliveryAnalyzer";
import { createVideoDeliveryAnalyzer } from "../utils/videoDeliveryAnalyzer";

const CALIBRATION_MS = 3000;

function InterviewSessionPage() {
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
  const [readyForNext, setReadyForNext] = useState(false);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [nextIsFollowUp, setNextIsFollowUp] =
  useState(false);

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

    if (token) {
      fetchSession();
    }
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
  const interviewReady = deliveryConsent !== null && !calibrating;

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
      score: response.score,
      feedback: response.feedback,
      strengths: response.strengths,
      improvements: response.improvements,
      deliveryFeedback: response.delivery_feedback,
      modelAnswer: response.model_answer,
      deliverySignals: response.delivery_signals,
    },
  }));

  setAnsweredQuestions((prev) => {
    const updated = new Set(prev);
    updated.add(currentQuestion.id);
    return updated;
  });

  if (response.has_follow_up && response.follow_up) {
    setSession((prevSession) => {
      const updatedQuestions = [...prevSession.questions];

      updatedQuestions.splice(
        currentQuestionIndex + 1,
        0,
        {
          id: response.follow_up.question_id,
          question_text:
            response.follow_up.question_text,
          question_type:
            response.follow_up.question_type,
          follow_up_depth:
            response.follow_up.follow_up_depth,
          is_follow_up: true,
          answered: false,
        }
      );

      return {
        ...prevSession,
        questions: updatedQuestions,
      };
    });
    setNextIsFollowUp(true);
  }else{
    setNextIsFollowUp(false);
  }

  setReadyForNext(true);
};

const handlePrevious = () => {
  if (currentQuestionIndex > 0) {

    setCurrentQuestionIndex((prev) => prev - 1);

    setReadyForNext(false);
    setNextIsFollowUp(false);

  }
};

const handleNext = () => {
  if (currentQuestionIndex < session.questions.length - 1) {

    setCurrentQuestionIndex((prev) => prev + 1);

    setReadyForNext(false);
    setNextIsFollowUp(false);

  }
};

const handleFinishInterview = async () => {
  const unanswered =
    session.questions.length -
    answeredQuestions.size;

  if (unanswered > 0) {
    const confirmFinish = window.confirm(
      `You still have ${unanswered} unanswered question(s).\n\nDo you want to finish the interview?`
    );

    if (!confirmFinish) return;
  }

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
      createdAt: session.created_at,
      questions: session.questions,
      feedbackMap,
    },
  });
};

const isLastQuestion = currentQuestionIndex === session.questions.length - 1;

return (
  <div className="workspace">
    {deliveryConsent === null && !calibrating && (
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
        <Link to="/dashboard" className="workspace-topbar__exit">
          Exit interview
        </Link>
      </div>
    </header>

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
        {!isLastQuestion ? (
          readyForNext ? (
            <button className="button button--primary" onClick={handleNext}>
              {nextIsFollowUp ? "Continue to Follow-up →" : "Next Question →"}
            </button>
          ) : (
            <>
              <button className="button button--secondary" onClick={handleNext}>
                Next / Skip
              </button>
              <button
                className="button button--primary"
                onClick={() => answerBoxRef.current?.submit()}
                disabled={answeredQuestions.has(currentQuestion.id) || isSubmittingAnswer}
              >
                {isSubmittingAnswer ? "Submitting..." : "Submit answer"}
              </button>
            </>
          )
        ) : (
          <>
            {!readyForNext && (
              <button
                className="button button--secondary"
                onClick={() => answerBoxRef.current?.submit()}
                disabled={answeredQuestions.has(currentQuestion.id) || isSubmittingAnswer}
              >
                {isSubmittingAnswer ? "Submitting..." : "Submit answer"}
              </button>
            )}
            <button className="button button--primary" onClick={handleFinishInterview}>
              Finish Interview
            </button>
          </>
        )}
      </div>
    </footer>
  </div>
);
}

export default InterviewSessionPage;
