import { useEffect, useRef, useState } from "react";
import { FiHelpCircle } from "react-icons/fi";

const SUPPORT_EMAIL = "hotseat.hello@gmail.com";

function HelpButton() {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!open) return;

    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <div className="help-button-container" ref={containerRef}>
      {open && (
        <div className="help-popover" role="dialog" aria-label="Help and support">
          <p className="help-popover__text">Need help? Contact us at</p>
          <a className="help-popover__link" href={`mailto:${SUPPORT_EMAIL}`}>
            {SUPPORT_EMAIL}
          </a>
        </div>
      )}

      <button
        type="button"
        className="help-button"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Help and support"
        aria-expanded={open}
      >
        <FiHelpCircle size={18} />
      </button>
    </div>
  );
}

export default HelpButton;
