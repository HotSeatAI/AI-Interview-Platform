import { useEffect, useId, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";

// Shared hamburger behavior for both the authenticated Navbar and the
// public LandingPage nav. Renders the same DOM at every viewport -
// CSS alone decides whether `children` sit inline (desktop) or inside
// a collapsed panel gated behind the toggle button (see the
// .nav-mobile-toggle / .nav-mobile-panel rules in index.css, keyed to
// the same 760px breakpoint both navs already used before this).
function MobileNavToggle({ children }) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const toggleRef = useRef(null);
  const panelRef = useRef(null);
  const location = useLocation();
  const [prevPath, setPrevPath] = useState(location.pathname);

  // Route navigation (clicking a link inside the panel) always closes
  // it - adjusted during render (React's documented pattern for
  // resetting state on a prop change) rather than in an effect, so it
  // takes effect on the same render as the navigation instead of one
  // tick later. Uses state, not a ref, since ref reads/writes during
  // render are disallowed by this project's hooks lint rules.
  if (prevPath !== location.pathname) {
    setPrevPath(location.pathname);
    if (open) setOpen(false);
  }

  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setOpen(false);
        toggleRef.current?.focus();
      }
    };

    const handlePointerDown = (event) => {
      if (
        panelRef.current?.contains(event.target) ||
        toggleRef.current?.contains(event.target)
      ) {
        return;
      }
      setOpen(false);
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("pointerdown", handlePointerDown);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    panelRef.current?.querySelector("a, button")?.focus();

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("pointerdown", handlePointerDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  return (
    <>
      <button
        ref={toggleRef}
        type="button"
        className="nav-mobile-toggle"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={open ? "Close menu" : "Open menu"}
        onClick={() => setOpen((prev) => !prev)}
      >
        {open ? <FiX size={20} /> : <FiMenu size={20} />}
      </button>

      <div
        id={panelId}
        ref={panelRef}
        className={`nav-mobile-panel ${open ? "nav-mobile-panel--open" : ""}`}
      >
        {children}
      </div>
    </>
  );
}

export default MobileNavToggle;
