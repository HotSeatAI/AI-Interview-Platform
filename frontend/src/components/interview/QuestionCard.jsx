import { useEffect, useState } from "react";

import { speak, stopSpeaking, isSpeechSupported } from "../../utils/questionSpeech";

const TTS_PREFERENCE_KEY = "hotseat_read_questions_aloud";

function getStoredPreference() {
  if (typeof window === "undefined") return true;
  const stored = window.localStorage.getItem(TTS_PREFERENCE_KEY);
  return stored === null ? true : stored === "true";
}

function QuestionCard({ questionText, isFollowUp, ttsEnabled = true }) {
  const [readAloud, setReadAloud] = useState(getStoredPreference);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // ttsEnabled is deliberately a dependency here (not just a guard) -
  // it starts false while the delivery consent/calibration overlay is
  // up, then flips to true once that resolves. Including it in the
  // deps means the effect re-fires at that exact moment even though
  // questionText hasn't changed, so the first question gets spoken
  // then instead of the instant the page mounted.
  useEffect(() => {
    if (!readAloud || !ttsEnabled) return;

    speak(questionText, {
      onStart: () => setIsSpeaking(true),
      onEnd: () => setIsSpeaking(false),
    });

    return () => stopSpeaking();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questionText, isFollowUp, ttsEnabled]);

  useEffect(() => {
    return () => stopSpeaking();
  }, []);

  const handleToggleReadAloud = () => {
    const next = !readAloud;
    setReadAloud(next);
    window.localStorage.setItem(TTS_PREFERENCE_KEY, String(next));

    if (!next) {
      stopSpeaking();
      setIsSpeaking(false);
    }
  };

  const handleReplayOrStop = () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
    } else {
      speak(questionText, {
        onStart: () => setIsSpeaking(true),
        onEnd: () => setIsSpeaking(false),
      });
    }
  };

  return (
    <article className="question-card">
      {isFollowUp && (
        <div className="follow-up-banner">
          <span className="follow-up-banner__tag">FOLLOW-UP</span>
          <span className="follow-up-banner__text">
            The interviewer is digging deeper into your previous answer.
          </span>
        </div>
      )}

      <div className="question-card__header">
        {isSpeaking && (
          <span className="recording-badge">
            <span className="recording-dot" />
            Speaking…
          </span>
        )}
      </div>

      <p className="question-card__text">{questionText}</p>

      {isSpeechSupported() && (
        <div className="question-card__voice-controls">
          <button
            type="button"
            className="button button--ghost button--sm"
            onClick={handleReplayOrStop}
          >
            {isSpeaking ? "Stop" : "Replay question"}
          </button>

          <label className="question-card__voice-toggle">
            <input
              type="checkbox"
              checked={readAloud}
              onChange={handleToggleReadAloud}
            />
            Read questions aloud
          </label>
        </div>
      )}
    </article>
  );
}

export default QuestionCard;
