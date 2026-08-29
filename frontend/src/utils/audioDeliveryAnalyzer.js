// Audio delivery signal analyzer.
//
// Computes delivery/nervousness PROXIES (pauses, short-pause/disfluency
// count, voiced-time ratio) purely from raw microphone signal energy
// over time - never from speech-to-text transcript content. This is
// deliberate: a mis-transcribed accented answer must never be able to
// influence delivery feedback the way it once poisoned technical
// scoring (see Answer.delivery_signals in the backend). Everything
// here reads only RMS amplitude from the Web Audio API, nothing about
// words.
//
// Runs independently of the existing Web Speech API transcript capture
// (VoiceInput.jsx) - both read the same physical microphone, via
// separate getUserMedia streams.

const DEFAULT_SILENCE_RMS_THRESHOLD = 0.02;
const SHORT_PAUSE_MIN_MS = 150;
const LONG_PAUSE_MIN_MS = 600;
const SAMPLE_INTERVAL_MS = 50;

// How far above the calibrated noise floor a sample must be to count
// as speech, and how much weight new "confirmed silence" samples get
// when slowly drifting the floor during normal tracking (e.g. if the
// room gets noisier mid-interview).
const NOISE_FLOOR_MARGIN = 0.01;
const NOISE_FLOOR_EMA_ALPHA = 0.02;

const MAX_TRACKED_EVENTS = 3;

// Pitch is only sampled while speaking, and only every this many RMS
// ticks - autocorrelation is far more expensive than an RMS read, and
// pitch doesn't need 50ms resolution to characterize overall variety.
const PITCH_SAMPLE_EVERY_N_TICKS = 4;
// Typical human speaking range - anything outside this is treated as
// a detection error (octave error, noise) rather than real pitch.
const MIN_VALID_PITCH_HZ = 70;
const MAX_VALID_PITCH_HZ = 400;
const MIN_PITCH_SAMPLES_FOR_SIGNAL = 5;

function createEmptyCounters() {
  return {
    // Sum of sample ticks while actively recording (see `active` flag
    // below) - NOT wall-clock time since reset. Idle time before the
    // user clicks "Start recording", or after they stop/finish and
    // before clicking Submit, must never count as elapsed answering
    // time or dilute voiced_ratio / get misread as a trailing pause.
    activeMs: 0,
    voicedMs: 0,
    // { duration_ms, position_pct } per pause - position_pct is how
    // far into the answer (so far) the pause started, so feedback can
    // reference roughly *when* it happened without ever touching
    // transcript content.
    pauseEvents: [],
    shortPauseCount: 0,
    pitchSamplesHz: [],
    ticksSinceLastPitchSample: 0,
  };
}

// Estimates fundamental frequency (Hz) via autocorrelation - a
// standard, well-established pitch-detection technique (not ML,
// no transcript involved). Returns -1 if the buffer is too quiet or
// no clear periodicity is found.
function autoCorrelatePitch(buffer, sampleRate) {
  const size = buffer.length;

  let rms = 0;
  for (let i = 0; i < size; i++) rms += buffer[i] * buffer[i];
  rms = Math.sqrt(rms / size);
  if (rms < 0.01) return -1;

  let start = 0;
  let end = size - 1;
  const trimThreshold = 0.2;
  while (start < size / 2 && Math.abs(buffer[start]) < trimThreshold) start++;
  while (end > size / 2 && Math.abs(buffer[end]) < trimThreshold) end--;

  const trimmed = buffer.slice(start, end);
  const trimmedSize = trimmed.length;
  if (trimmedSize < 2) return -1;

  const correlations = new Array(trimmedSize).fill(0);
  for (let lag = 0; lag < trimmedSize; lag++) {
    for (let i = 0; i < trimmedSize - lag; i++) {
      correlations[lag] += trimmed[i] * trimmed[i + lag];
    }
  }

  let d = 0;
  while (d + 1 < correlations.length && correlations[d] > correlations[d + 1]) d++;

  let maxValue = -1;
  let maxLag = -1;
  for (let lag = d; lag < correlations.length; lag++) {
    if (correlations[lag] > maxValue) {
      maxValue = correlations[lag];
      maxLag = lag;
    }
  }

  if (maxLag <= 0) return -1;

  // Parabolic interpolation around the peak for sub-sample precision.
  const x1 = correlations[maxLag - 1] ?? correlations[maxLag];
  const x2 = correlations[maxLag];
  const x3 = correlations[maxLag + 1] ?? correlations[maxLag];
  const a = (x1 + x3 - 2 * x2) / 2;
  const b = (x3 - x1) / 2;
  const refinedLag = a ? maxLag - b / (2 * a) : maxLag;

  return refinedLag > 0 ? sampleRate / refinedLag : -1;
}

function topEvents(events) {
  return [...events]
    .sort((a, b) => b.duration_ms - a.duration_ms)
    .slice(0, MAX_TRACKED_EVENTS)
    .map((event) => ({
      duration_ms: Math.round(event.duration_ms),
      position_pct: Math.round(event.position_pct),
    }));
}

export function createAudioDeliveryAnalyzer() {
  let audioContext = null;
  let analyser = null;
  let source = null;
  let stream = null;
  let intervalId = null;
  let timeDomainData = null;
  let floatTimeDomainData = null;

  let isSpeaking = false;
  let silenceStartedAt = null;

  // Only true between the user clicking "Start recording" and
  // "Stop recording" (or submitting) - see setActive(). Sampling is a
  // no-op while inactive, so idle time never pollutes the signals.
  let active = false;

  // Calibrated per-session, per-room noise floor - replaces the fixed
  // constant once calibrate() has run. Falls back to the default so
  // the analyzer still works if calibrate() is never called.
  let silenceThreshold = DEFAULT_SILENCE_RMS_THRESHOLD;

  let counters = createEmptyCounters();

  function readRms() {
    analyser.getByteTimeDomainData(timeDomainData);

    let sumSquares = 0;
    for (let i = 0; i < timeDomainData.length; i++) {
      const normalized = (timeDomainData[i] - 128) / 128;
      sumSquares += normalized * normalized;
    }
    return Math.sqrt(sumSquares / timeDomainData.length);
  }

  function sampleOnce() {
    if (!active) return;

    const rms = readRms();

    const now = performance.now();
    const speakingNow = rms >= silenceThreshold;

    counters.activeMs += SAMPLE_INTERVAL_MS;

    if (speakingNow) {
      counters.voicedMs += SAMPLE_INTERVAL_MS;

      if (!isSpeaking && silenceStartedAt !== null) {
        const pauseMs = now - silenceStartedAt;

        if (pauseMs >= SHORT_PAUSE_MIN_MS) {
          const elapsedSoFar = counters.activeMs;
          const pauseStartActiveMs = elapsedSoFar - pauseMs;

          counters.pauseEvents.push({
            duration_ms: pauseMs,
            position_pct: elapsedSoFar
              ? (pauseStartActiveMs / elapsedSoFar) * 100
              : 0,
          });

          if (pauseMs < LONG_PAUSE_MIN_MS) {
            counters.shortPauseCount += 1;
          }
        }

        silenceStartedAt = null;
      }

      isSpeaking = true;

      counters.ticksSinceLastPitchSample += 1;
      if (counters.ticksSinceLastPitchSample >= PITCH_SAMPLE_EVERY_N_TICKS) {
        counters.ticksSinceLastPitchSample = 0;

        analyser.getFloatTimeDomainData(floatTimeDomainData);
        const pitchHz = autoCorrelatePitch(
          floatTimeDomainData,
          audioContext.sampleRate
        );

        if (pitchHz >= MIN_VALID_PITCH_HZ && pitchHz <= MAX_VALID_PITCH_HZ) {
          counters.pitchSamplesHz.push(pitchHz);
        }
      }
    } else {
      if (isSpeaking) {
        silenceStartedAt = now;
      }

      isSpeaking = false;

      // We're confident this sample is silence (below the current
      // threshold already) - let it slowly pull the noise floor
      // toward the room's actual ambient level, so a mid-interview
      // change (AC turning on, etc.) doesn't get stuck on the
      // one-time calibration reading.
      silenceThreshold =
        (1 - NOISE_FLOOR_EMA_ALPHA) * silenceThreshold +
        NOISE_FLOOR_EMA_ALPHA * (rms + NOISE_FLOOR_MARGIN);
    }
  }

  return {
    // Starts continuous tracking on the given MediaStream (a
    // getUserMedia audio stream owned by the caller). Safe to call
    // once per interview - keeps running across questions.
    async start(mediaStream) {
      stream = mediaStream;

      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      source = audioContext.createMediaStreamSource(stream);

      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      timeDomainData = new Uint8Array(analyser.fftSize);
      floatTimeDomainData = new Float32Array(analyser.fftSize);

      source.connect(analyser);

      counters = createEmptyCounters();
      isSpeaking = false;
      silenceStartedAt = null;
      active = false;

      intervalId = setInterval(sampleOnce, SAMPLE_INTERVAL_MS);
    },

    // Turns sampling on/off - wire this to the "Start/Stop recording"
    // button (see VoiceInput.jsx), not to the interview/question
    // lifecycle. Nothing is measured while inactive: not the silence
    // before the user starts talking, and not the gap between
    // finishing and clicking Submit.
    setActive(isActive) {
      if (active === isActive) return;

      if (!isActive && isSpeaking === false) {
        // Drop any in-progress (unresolved) silence rather than let it
        // bridge across a stop/resume boundary - it's no longer part
        // of an active recording window.
        silenceStartedAt = null;
      }

      active = isActive;
    },

    // Samples ambient room/mic noise for durationMs (caller should
    // ask the user to stay quiet) and sets the noise-floor threshold
    // from it, instead of relying on the fixed default. Call once,
    // right after start(), before any question is being answered.
    async calibrate(durationMs) {
      const samples = [];
      const sampleCount = Math.max(1, Math.round(durationMs / SAMPLE_INTERVAL_MS));

      for (let i = 0; i < sampleCount; i++) {
        samples.push(readRms());
        await new Promise((resolve) => setTimeout(resolve, SAMPLE_INTERVAL_MS));
      }

      samples.sort((a, b) => a - b);
      const p90 = samples[Math.floor(samples.length * 0.9)] ?? 0;

      silenceThreshold = Math.max(
        DEFAULT_SILENCE_RMS_THRESHOLD * 0.25,
        p90 + NOISE_FLOOR_MARGIN
      );
    },

    // Returns a plain, numeric-only summary of signals accumulated
    // since the last reset() - safe to send to the backend as-is.
    getSignalsSinceReset() {
      const elapsedMs = counters.activeMs;
      const elapsedMin = elapsedMs / 60000;

      const pauseCount = counters.pauseEvents.length;
      const avgPauseMs = pauseCount
        ? counters.pauseEvents.reduce((sum, e) => sum + e.duration_ms, 0) / pauseCount
        : 0;
      const longestPauseMs = pauseCount
        ? Math.max(...counters.pauseEvents.map((e) => e.duration_ms))
        : 0;

      const pitchSamples = counters.pitchSamplesHz;
      let pitchMeanHz = null;
      let pitchStddevHz = null;

      if (pitchSamples.length >= MIN_PITCH_SAMPLES_FOR_SIGNAL) {
        pitchMeanHz = pitchSamples.reduce((a, b) => a + b, 0) / pitchSamples.length;
        const variance =
          pitchSamples.reduce((sum, hz) => sum + (hz - pitchMeanHz) ** 2, 0) /
          pitchSamples.length;
        pitchStddevHz = Math.sqrt(variance);
      }

      return {
        elapsed_ms: Math.round(elapsedMs),
        voiced_ratio: elapsedMs
          ? Math.min(1, counters.voicedMs / elapsedMs)
          : 0,
        pause_count: pauseCount,
        avg_pause_ms: Math.round(avgPauseMs),
        longest_pause_ms: Math.round(longestPauseMs),
        pause_events: topEvents(counters.pauseEvents),
        short_pause_count: counters.shortPauseCount,
        short_pauses_per_min:
          elapsedMin > 0
            ? Math.round((counters.shortPauseCount / elapsedMin) * 10) / 10
            : 0,
        pitch_mean_hz: pitchMeanHz !== null ? Math.round(pitchMeanHz) : null,
        pitch_stddev_hz: pitchStddevHz !== null ? Math.round(pitchStddevHz) : null,
      };
    },

    // Clears accumulated counters (call between questions) without
    // tearing down the mic stream/AudioContext or the calibrated
    // noise floor.
    reset() {
      counters = createEmptyCounters();
      isSpeaking = false;
      silenceStartedAt = null;
      active = false;
    },

    // Fully tears down - stop mic tracks and close the AudioContext.
    // Call once when leaving the interview.
    stop() {
      if (intervalId) clearInterval(intervalId);
      intervalId = null;

      source?.disconnect();
      audioContext?.close();

      stream?.getTracks().forEach((track) => track.stop());

      audioContext = null;
      analyser = null;
      source = null;
      stream = null;
    },
  };
}
