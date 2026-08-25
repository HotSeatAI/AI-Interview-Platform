function CombinedPreview({
  explanationText,
  code,
}) {
  const sections = [];

  if (explanationText.trim()) {
    sections.push(
      `Explanation:\n${explanationText.trim()}`
    );
  }

  if (code.trim()) {
    sections.push(
      `Code:\n${code.trim()}`
    );
  }

  const preview = sections.length
    ? sections.join("\n\n")
    : "Your combined answer will appear here...";

  return (
    <div className="combined-preview">
      <div className="combined-preview__row">
        <span className="combined-preview__label">Combined answer preview</span>
        <span className="combined-preview__meta">
          Explanation + Code will be submitted as one response
        </span>
      </div>

      <textarea
        className="combined-preview__box"
        value={preview}
        readOnly
        rows={6}
      />
    </div>
  );
}

export default CombinedPreview;
