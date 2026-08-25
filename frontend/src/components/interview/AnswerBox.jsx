import {
  useState,
  forwardRef,
  useImperativeHandle,
} from "react";

import { submitAnswer } from "../../api/answerApi";
import useAuth from "../../hooks/useAuth";
import { runCode } from "../../api/codeApi";
import VoiceInput from "./VoiceInput";
import CodeEditor from "./CodeEditor";
import CombinedPreview from "./CombinedPreview";
import ConsoleOutput from "./ConsoleOutput";
import CustomInput from "./CustomInput";

import {
  PROGRAMMING_LANGUAGES,
  DEFAULT_LANGUAGE,
} from "../../constants/programmingLanguages";

const AnswerBox = forwardRef(function AnswerBox(
  {
    questionId,
    onAnswerSubmitted,
    onSubmittingChange,
    disabled = false,
  },
  ref
) {
  const { token } = useAuth();

  const [explanationText, setExplanationText] = useState("");
  const [code, setCode] = useState("");

  const [customInput, setCustomInput] = useState("");

  const [consoleOutput, setConsoleOutput] =
    useState("");

  const [executionStatus, setExecutionStatus] =
    useState("idle");

  const [selectedLanguage, setSelectedLanguage] =
    useState(DEFAULT_LANGUAGE);

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const hasContent =
    explanationText.trim() ||
    code.trim();

  const handleRunCode = async () => {
    if (executionStatus === "running") {
      return;
    }
    setError("");
    if (!code.trim()) {
      setExecutionStatus("idle");
      setConsoleOutput("Please write some code first.");
      return;
  }

  try {
    setExecutionStatus("running");
    setConsoleOutput("");

    const response = await runCode(
      {
        language: selectedLanguage.id,
        code,
        stdin: customInput,
      },
      token
    );

    setExecutionStatus(response.status);

    let output = "";

    if (response.stdout) {
      output += response.stdout;
    }

    if (response.stderr) {
      if (output) {
        output += "\n\n";
      }

      output += response.stderr;
    }

    if (output.trim()==="") {
      output = "Program executed successfully.";
    }

    setConsoleOutput(output);

  } catch (error) {

    setExecutionStatus("internal_error");

    setConsoleOutput(
      error?.response?.data?.detail ||
      error.message ||
      "Failed to execute code."
    );

  }
};

  const handleSubmit = async (event) => {
    if (event) event.preventDefault();

    if (disabled || submitting) return;

    if (!hasContent) {
      setError(
        "Please provide an explanation or code."
      );
      return;
    }

    try {
      setSubmitting(true);
      onSubmittingChange?.(true);
      setError("");

      const response = await submitAnswer(
        {
          question_id: questionId,
          voice_text: explanationText.trim(),
          // TODO(backend migration): the "Additional Notes" box was merged
          // into the voice/explanation textarea above, so typed_text is now
          // always empty from this client. Once the backend drops typed_text
          // (see TODOs in schemas/answer.py, models/answer.py and
          // ai_service.build_combined_answer), this field can be removed too.
          typed_text: "",
          code: code.trim(),
        },
        token
      );

      setExplanationText("");
      setCode("");
      setCustomInput("");
      setConsoleOutput("");
      setExecutionStatus("idle");
      setSelectedLanguage(DEFAULT_LANGUAGE);

      onAnswerSubmitted(response);

    } catch (err) {

      setError(
        err?.response?.data?.detail ||
        "Failed to submit answer."
      );

    } finally {
      setSubmitting(false);
      onSubmittingChange?.(false);
    }
  };

  useImperativeHandle(ref, () => ({
    submit: () => handleSubmit(),
  }));

  const handleLanguageChange = (languageId) => {
    const language =
      PROGRAMMING_LANGUAGES.find(
        (lang) => lang.id === languageId
      );

    if (language) {
      setSelectedLanguage(language);
    }
  };

  return (
    <form
      className="answer-card"
      onSubmit={handleSubmit}
    >
      <div className="answer-card__header">
        <div className="answer-card__label">YOUR ANSWER</div>
        <div className="answer-card__sublabel">
          Think. Explain. Write. Code. Submit — both are graded together.
        </div>
      </div>

      <VoiceInput
        value={explanationText}
        onChange={setExplanationText}
        disabled={disabled}
      />

      <CodeEditor
        value={code}
        onChange={setCode}
        language={selectedLanguage}
        disabled={disabled}
        onRunCode={handleRunCode}
        isRunning={executionStatus === "running"}
        onLanguageChange={handleLanguageChange}
      />

      <CustomInput
        value={customInput}
        onChange={setCustomInput}
        disabled={disabled}
      />

      <ConsoleOutput
        output={consoleOutput}
        status={executionStatus}
      />

      <CombinedPreview
        explanationText={explanationText}
        code={code}
      />

      {error && (
        <p className="error-text">
          {error}
        </p>
      )}
    </form>
  );
});

export default AnswerBox;
