import { useEffect, useRef, useState } from "react";

const MARGIN = 16;

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

// Small live self-view so the candidate always knows the camera is
// on. Purely a preview - detection itself runs on its own detached
// video element inside videoDeliveryAnalyzer.js, not this one.
// Draggable, clamped so it always stays fully within the page.
function WebcamMonitor({ stream }) {
  const videoRef = useRef(null);
  const boxRef = useRef(null);
  const dragRef = useRef(null);

  const [position, setPosition] = useState(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  useEffect(() => {
    if (!stream || !boxRef.current) return;

    const { width, height } = boxRef.current.getBoundingClientRect();

    setPosition((prev) =>
      prev || {
        x: window.innerWidth - width - MARGIN,
        y: window.innerHeight - height - MARGIN,
      }
    );
  }, [stream]);

  useEffect(() => {
    const clampToViewport = () => {
      if (!boxRef.current) return;

      const { width, height } = boxRef.current.getBoundingClientRect();

      setPosition((prev) =>
        prev
          ? {
              x: clamp(prev.x, MARGIN, window.innerWidth - width - MARGIN),
              y: clamp(prev.y, MARGIN, window.innerHeight - height - MARGIN),
            }
          : prev
      );
    };

    window.addEventListener("resize", clampToViewport);
    return () => window.removeEventListener("resize", clampToViewport);
  }, []);

  const handlePointerDown = (event) => {
    if (!boxRef.current) return;

    const rect = boxRef.current.getBoundingClientRect();

    dragRef.current = {
      offsetX: event.clientX - rect.left,
      offsetY: event.clientY - rect.top,
    };

    event.target.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event) => {
    if (!dragRef.current || !boxRef.current) return;

    const { width, height } = boxRef.current.getBoundingClientRect();

    const nextX = event.clientX - dragRef.current.offsetX;
    const nextY = event.clientY - dragRef.current.offsetY;

    setPosition({
      x: clamp(nextX, MARGIN, window.innerWidth - width - MARGIN),
      y: clamp(nextY, MARGIN, window.innerHeight - height - MARGIN),
    });
  };

  const handlePointerUp = (event) => {
    dragRef.current = null;
    event.target.releasePointerCapture(event.pointerId);
  };

  if (!stream) return null;

  return (
    <div
      ref={boxRef}
      className="webcam-monitor"
      style={
        position
          ? { left: position.x, top: position.y, right: "auto", bottom: "auto" }
          : undefined
      }
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
    >
      <video
        ref={videoRef}
        className="webcam-monitor__video"
        muted
        autoPlay
        playsInline
      />
      <span className="recording-badge webcam-monitor__badge">
        <span className="recording-dot" />
        Camera active
      </span>
    </div>
  );
}

export default WebcamMonitor;
