// Thin wrapper around the browser's native Web Speech Synthesis API
// (the "speak text aloud" counterpart to VoiceInput.jsx's speech
// *recognition*). Fully client-side, no backend/Gemini cost, no new
// dependency - SpeechSynthesisUtterance is a native browser global.

// Default voice/dialect (matches the "en-US" already used for speech
// *recognition* in VoiceInput.jsx). Rate/pitch pulled back slightly
// from the 1.0/1.0 default for a calmer, more deliberate mentor-to-
// mentee pace rather than a flat, hurried robotic read.
const SPEECH_LANG = "en-US";
const SPEECH_RATE = 0.92;
const SPEECH_PITCH = 0.95;

export function isSpeechSupported() {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

// Cancels any in-flight utterance first, so rapid question changes
// never overlap/garble two voices at once.
export function speak(text, { onStart, onEnd } = {}) {
  if (!isSpeechSupported() || !text) return;

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = SPEECH_LANG;
  utterance.rate = SPEECH_RATE;
  utterance.pitch = SPEECH_PITCH;

  if (onStart) utterance.onstart = onStart;
  if (onEnd) utterance.onend = onEnd;
  utterance.onerror = onEnd;

  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking() {
  if (isSpeechSupported()) {
    window.speechSynthesis.cancel();
  }
}
