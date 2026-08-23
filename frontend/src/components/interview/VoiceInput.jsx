import { useEffect, useRef, useState } from "react";

function VoiceInput({
  value,
  onChange,
  disabled = false,
}) {
  const recognitionRef = useRef(null);

  const shouldContinueRef = useRef(false);

  const [supported, setSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [hasStartedOnce, setHasStartedOnce] = useState(false);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    setSupported(true);

    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let transcript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        if (event.results[i].isFinal) {
          transcript +=
            event.results[i][0].transcript + " ";
        }
      }

      transcript = transcript.trim();

      if (!transcript) return;

      onChange((previous) =>
        previous
          ? `${previous.trim()} ${transcript}`
          : transcript
      );
    };

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onend = () => {
      setIsListening(false);

      if (
        shouldContinueRef.current &&
        !disabled
      ) {
        recognition.start();
      }
    };

    recognition.onerror = (event) => {
      console.log(event);

      if (
        event.error === "no-speech"
      ) {
        return;
      }

      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      shouldContinueRef.current = false;
      recognition.stop();
    };
  }, [onChange, disabled]);

  const startListening = () => {
    if (
      !recognitionRef.current ||
      disabled ||
      isListening
    ) {
      return;
    }

    shouldContinueRef.current = true;

    recognitionRef.current.start();

    setHasStartedOnce(true);
  };

  const stopListening = () => {
    shouldContinueRef.current = false;

    recognitionRef.current?.stop();
  };

  return (
    <div className="mode-block">
      <div className="mode-block__header">
        <span className="mode-block__label">YOUR EXPLANATION</span>
        {isListening && (
          <span className="recording-badge">
            <span className="recording-dot" />
            Recording
          </span>
        )}
      </div>

      {!supported && (
        <p className="error-text">
          Speech Recognition is not supported in this browser.
        </p>
      )}

      <textarea
        className="transcript-box"
        rows={4}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Speak, or type your explanation, notes, edge cases, assumptions..."
      />

      <div className="voice-button-row">
        <button
          type="button"
          className="button button--ghost"
          onClick={startListening}
          disabled={
            disabled ||
            !supported ||
            isListening
          }
        >
          {hasStartedOnce ? "Resume recording" : "Start recording"}
        </button>

        <button
          type="button"
          className="button button--ghost button--ghost-active"
          onClick={stopListening}
          disabled={
            disabled ||
            !isListening
          }
        >
          Stop recording
        </button>
      </div>
    </div>
  );
}

export default VoiceInput;
