import { useEffect, useState , useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { getInterviewSession } from "../api/interviewApi";
import useAuth from "../hooks/useAuth";

import QuestionCard from "../components/interview/QuestionCard";
import AnswerBox from "../components/interview/AnswerBox";
import FeedbackCard from "../components/interview/FeedbackCard";
import BrandLogo from "../components/layout/BrandLogo";

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

  if (loading) {
    return <div className="page-loading">Loading interview…</div>;
  }

  if (error) {
    return <div className="page-error">{error}</div>;
  }

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

const handleFinishInterview = () => {
  const unanswered =
    session.questions.length -
    answeredQuestions.size;

  if (unanswered > 0) {
    const confirmFinish = window.confirm(
      `You still have ${unanswered} unanswered question(s).\n\nDo you want to finish the interview?`
    );

    if (!confirmFinish) return;
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

      <Link to="/dashboard" className="workspace-topbar__exit">
        Exit interview
      </Link>
    </header>

    <main className="workspace-main">
      <QuestionCard
        questionText={currentQuestion.question_text}
        isFollowUp={currentQuestion.is_follow_up}
      />

      <AnswerBox
        ref={answerBoxRef}
        key={currentQuestion.id}
        questionId={currentQuestion.id}
        disabled={answeredQuestions.has(currentQuestion.id)}
        onAnswerSubmitted={handleAnswerSubmitted}
        onSubmittingChange={setIsSubmittingAnswer}
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
