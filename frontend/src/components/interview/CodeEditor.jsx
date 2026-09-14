import Editor from "@monaco-editor/react";
import LanguageSelector from "./LanguageSelector";
import useTheme from "../../hooks/useTheme";
import {
  PROGRAMMING_LANGUAGES,
} from "../../constants/programmingLanguages";

function CodeEditor({
  value,
  onChange,
  language,
  disabled = false,
  onRunCode = () => {},
  isRunning = false,
  onLanguageChange = () => {},
}) {
  const { theme } = useTheme();

  return (
    <div className="mode-block">
      <div className="mode-block__header">
        <span className="mode-block__label">CODE</span>
        <div className="code-controls">
          <LanguageSelector
            languages={PROGRAMMING_LANGUAGES}
            selectedLanguage={language}
            onLanguageChange={onLanguageChange}
          />
          <button
            type="button"
            className="run-button"
            onClick={onRunCode}
            disabled={disabled || isRunning}
          >
            {isRunning ? "Running…" : "▶ Run code"}
          </button>
        </div>
      </div>

      <div className="editor-shell">
        <Editor
          height="360px"
          language={language.monacoLanguage}
          value={value}
          onChange={(newValue) => onChange(newValue || "")}
          theme={theme === "dark" ? "vs-dark" : "vs"}
          options={{
            readOnly: disabled,

            fontSize: 13,

            fontFamily:
              "'JetBrains Mono', SFMono-Regular, Consolas, Monaco, Menlo, monospace",

            minimap: {
              enabled: false,
            },

            automaticLayout: true,

            scrollBeyondLastLine: false,

            wordWrap: "on",

            lineNumbers: "on",

            roundedSelection: true,

            tabSize: 4,

            insertSpaces: true,

            autoIndent: "advanced",

            formatOnPaste: true,

            formatOnType: true,

            autoClosingBrackets: "always",

            autoClosingQuotes: "always",

            matchBrackets: "always",

            folding: true,
          }}
        />
      </div>
    </div>
  );
}

export default CodeEditor;
