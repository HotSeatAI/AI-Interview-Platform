import { useEffect, useState } from "react";

// Shown once, right after the delivery-consent modal, while
// calibrate() runs on whichever analyzer(s) were enabled. A one-time,
// interview-level step - never repeated per question.
function DeliveryCalibrationScreen({ durationMs }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const startedAt = performance.now();

    let rafId;
    const tick = () => {
      const pct = Math.min(
        100,
        ((performance.now() - startedAt) / durationMs) * 100
      );
      setProgress(pct);

      if (pct < 100) {
        rafId = requestAnimationFrame(tick);
      }
    };

    rafId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafId);
  }, [durationMs]);

  return (
    <div className="delivery-consent-overlay">
      <div className="delivery-consent-card">
        <h2>Calibrating…</h2>

        <p>
          Stay quiet and look at the camera for a moment - this helps us
          calibrate to your room and camera setup so delivery feedback is
          more accurate.
        </p>

        <div className="delivery-calibration-bar">
          <div
            className="delivery-calibration-bar__fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export default DeliveryCalibrationScreen;
