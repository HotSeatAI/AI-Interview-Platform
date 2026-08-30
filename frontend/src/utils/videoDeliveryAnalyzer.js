// Video body-language signal analyzer.
//
// Computes body-language PROXIES (eye contact, fidgeting, blink rate)
// purely from face/head landmark geometry via on-device MediaPipe face
// landmark detection - runs entirely client-side (WASM), no frame is
// ever uploaded anywhere. Like audioDeliveryAnalyzer.js, this never
// touches transcript content - only geometric numbers.

import {
  FaceLandmarker,
  FilesetResolver,
} from "@mediapipe/tasks-vision";

const WASM_BASE_URL =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";

const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

// Tolerance (radians) around the calibrated baseline head orientation
// that still counts as "facing the camera."
const ON_CAMERA_ANGLE_THRESHOLD = 0.35;

// A look-away shorter than this is treated as a normal glance, not a
// reportable event (mirrors SHORT_PAUSE_MIN_MS in the audio analyzer).
const LOOK_AWAY_MIN_MS = 500;
const MAX_TRACKED_EVENTS = 3;

// Validated against real reference photos: closed-eye shots measured
// 0.50-0.73, open-eye shots topped out at 0.35 - 0.4 sits with margin
// on both sides (the old 0.5 default left almost none against the
// lowest closed-eye sample).
const DEFAULT_BLINK_THRESHOLD = 0.4;

// A closed-eyes stretch shorter than this is a normal (or slow) blink,
// not a reportable event.
const SUSTAINED_EYES_CLOSED_MIN_MS = 1500;

// Face-scale (inter-eye distance) ratio vs the calibrated baseline
// that counts as a real posture shift (leaning notably closer/further
// from the camera), rather than ordinary small movement.
// Validated against real reference photos: lean-in shots measured
// scale ratios of 1.23-1.52 against baseline - 1.25 missed the lowest
// (a real, if modest, lean-in), so lowered to 1.2. Lean-back shots
// measured 0.52-0.53, well clear of 0.8 - left unchanged.
const POSTURE_LEAN_IN_RATIO = 1.2;
const POSTURE_LEAN_BACK_RATIO = 0.8;
const POSTURE_SHIFT_MIN_MS = 2000;

// Landmark indices (MediaPipe FaceLandmarker 478-point mesh) used for
// the fidgeting/movement proxy - nose tip, both eye corners, chin.
// Averaging several stable points (instead of just the nose tip)
// makes the score less sensitive to any single noisy landmark.
const MOVEMENT_LANDMARK_INDICES = [1, 33, 263, 152];
// Outer eye corners, used purely to estimate face size in-frame so
// movement can be normalized against distance-from-camera.
const LEFT_EYE_OUTER = 33;
const RIGHT_EYE_OUTER = 263;

function rotationFromMatrix(matrixData) {
  // matrixData is a column-major 4x4 transform. Column 2 (indices
  // 8, 9, 10) is the face's local Z axis (its forward/gaze direction)
  // expressed in world space - this is what actually tells us which
  // way the face is pointing, unlike row-based elements which barely
  // move under a real head turn.
  const m = matrixData;
  const fx = m[8];
  const fy = m[9];
  const fz = m[10];

  const yaw = Math.atan2(fx, fz);
  const pitch = Math.atan2(-fy, Math.sqrt(fx * fx + fz * fz));

  return { yaw, pitch };
}

function blinkScoreFrom(result) {
  if (!result.faceBlendshapes?.length) return null;

  const categories = result.faceBlendshapes[0].categories;
  const left = categories.find((c) => c.categoryName === "eyeBlinkLeft");
  const right = categories.find((c) => c.categoryName === "eyeBlinkRight");

  if (!left && !right) return null;

  return ((left?.score ?? 0) + (right?.score ?? 0)) / 2;
}

function eyeDistance(landmarks) {
  const leftEye = landmarks[LEFT_EYE_OUTER];
  const rightEye = landmarks[RIGHT_EYE_OUTER];
  const dx = leftEye.x - rightEye.x;
  const dy = leftEye.y - rightEye.y;
  return Math.sqrt(dx * dx + dy * dy) || 1;
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

export function createVideoDeliveryAnalyzer() {
  let faceLandmarker = null;
  let videoEl = null;
  let stream = null;
  let rafId = null;
  let lastVideoTime = -1;

  let startedAt = performance.now();
  let framesAttempted = 0;
  let framesSampled = 0;
  let onCameraFrames = 0;
  let blinkEvents = 0;
  let wasBlinking = false;
  let movementAccum = 0;
  let lastLandmarkPositions = null;

  let isOnCamera = true;
  let lookAwayStartedAt = null;
  let lookAwayEvents = [];

  let eyesClosedStartedAt = null;
  let sustainedEyesClosedEvents = [];

  let isNormalPosture = true;
  let postureShiftStartedAt = null;
  let postureShiftEvents = [];

  // Calibrated per-person baselines - corrects for real camera/monitor
  // layout (facing "the camera" is rarely exactly yaw=0/pitch=0) and
  // for individual differences in resting eyelid position/seating
  // distance. Fall back to sane defaults so the analyzer still works
  // if calibrate() is skipped (e.g. the model failed to load in time).
  let baselineYaw = 0;
  let baselinePitch = 0;
  let baselineFaceScale = null;
  let blinkThreshold = DEFAULT_BLINK_THRESHOLD;

  function resetCounters() {
    startedAt = performance.now();
    framesAttempted = 0;
    framesSampled = 0;
    onCameraFrames = 0;
    blinkEvents = 0;
    wasBlinking = false;
    movementAccum = 0;
    lastLandmarkPositions = null;
    isOnCamera = true;
    lookAwayStartedAt = null;
    lookAwayEvents = [];
    eyesClosedStartedAt = null;
    sustainedEyesClosedEvents = [];
    isNormalPosture = true;
    postureShiftStartedAt = null;
    postureShiftEvents = [];
  }

  function detectOnce() {
    if (videoEl.currentTime === lastVideoTime) return null;
    lastVideoTime = videoEl.currentTime;

    framesAttempted += 1;

    const result = faceLandmarker.detectForVideo(videoEl, performance.now());

    if (!result.faceLandmarks?.length) return null;

    return result;
  }

  function detectLoop() {
    if (!faceLandmarker || !videoEl) return;

    const result = detectOnce();

    if (result) {
      framesSampled += 1;

      const landmarks = result.faceLandmarks[0];
      const scale = eyeDistance(landmarks);

      const positions = MOVEMENT_LANDMARK_INDICES.map((index) => landmarks[index]);

      if (lastLandmarkPositions) {
        let displacement = 0;
        for (let i = 0; i < positions.length; i++) {
          const dx = positions[i].x - lastLandmarkPositions[i].x;
          const dy = positions[i].y - lastLandmarkPositions[i].y;
          displacement += Math.sqrt(dx * dx + dy * dy);
        }
        // Normalize by face size (inter-eye distance) so moving
        // closer/further from the camera isn't read as fidgeting -
        // only motion relative to the face's own scale counts.
        movementAccum += displacement / positions.length / scale;
      }
      lastLandmarkPositions = positions;

      if (baselineFaceScale) {
        const scaleRatio = scale / baselineFaceScale;
        const now = performance.now();
        const normalNow =
          scaleRatio <= POSTURE_LEAN_IN_RATIO &&
          scaleRatio >= POSTURE_LEAN_BACK_RATIO;

        if (normalNow) {
          if (!isNormalPosture && postureShiftStartedAt !== null) {
            const durationMs = now - postureShiftStartedAt;

            if (durationMs >= POSTURE_SHIFT_MIN_MS) {
              const elapsedMs = now - startedAt;
              postureShiftEvents.push({
                duration_ms: durationMs,
                position_pct: elapsedMs
                  ? ((postureShiftStartedAt - startedAt) / elapsedMs) * 100
                  : 0,
              });
            }

            postureShiftStartedAt = null;
          }

          isNormalPosture = true;
        } else {
          if (isNormalPosture) {
            postureShiftStartedAt = now;
          }

          isNormalPosture = false;
        }
      }

      if (result.facialTransformationMatrixes?.length) {
        const { yaw, pitch } = rotationFromMatrix(
          result.facialTransformationMatrixes[0].data
        );

        const now = performance.now();
        const onCameraNow =
          Math.abs(yaw - baselineYaw) < ON_CAMERA_ANGLE_THRESHOLD &&
          Math.abs(pitch - baselinePitch) < ON_CAMERA_ANGLE_THRESHOLD;

        if (onCameraNow) {
          onCameraFrames += 1;

          if (!isOnCamera && lookAwayStartedAt !== null) {
            const durationMs = now - lookAwayStartedAt;

            if (durationMs >= LOOK_AWAY_MIN_MS) {
              const elapsedMs = now - startedAt;
              lookAwayEvents.push({
                duration_ms: durationMs,
                position_pct: elapsedMs
                  ? ((lookAwayStartedAt - startedAt) / elapsedMs) * 100
                  : 0,
              });
            }

            lookAwayStartedAt = null;
          }

          isOnCamera = true;
        } else {
          if (isOnCamera) {
            lookAwayStartedAt = now;
          }

          isOnCamera = false;
        }
      }

      const blinkScore = blinkScoreFrom(result);
      if (blinkScore !== null) {
        const now = performance.now();
        const closedNow = blinkScore > blinkThreshold;

        if (closedNow && !wasBlinking) {
          blinkEvents += 1;
          eyesClosedStartedAt = now;
        } else if (!closedNow && wasBlinking && eyesClosedStartedAt !== null) {
          const durationMs = now - eyesClosedStartedAt;

          if (durationMs >= SUSTAINED_EYES_CLOSED_MIN_MS) {
            const elapsedMs = now - startedAt;
            sustainedEyesClosedEvents.push({
              duration_ms: durationMs,
              position_pct: elapsedMs
                ? ((eyesClosedStartedAt - startedAt) / elapsedMs) * 100
                : 0,
            });
          }

          eyesClosedStartedAt = null;
        }

        wasBlinking = closedNow;
      }
    }

    rafId = requestAnimationFrame(detectLoop);
  }

  return {
    // Loads the face-landmark model (network fetch, WASM init - do
    // this once) and starts continuous detection on the given
    // MediaStream. Safe to call once per interview.
    async start(mediaStream) {
      stream = mediaStream;

      const filesetResolver = await FilesetResolver.forVisionTasks(
        WASM_BASE_URL
      );

      faceLandmarker = await FaceLandmarker.createFromOptions(
        filesetResolver,
        {
          baseOptions: {
            modelAssetPath: MODEL_URL,
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numFaces: 1,
          outputFaceBlendshapes: true,
          outputFacialTransformationMatrixes: true,
        }
      );

      videoEl = document.createElement("video");
      videoEl.muted = true;
      videoEl.playsInline = true;
      videoEl.srcObject = stream;
      await videoEl.play();

      resetCounters();
      rafId = requestAnimationFrame(detectLoop);
    },

    // Samples yaw/pitch/blink-openness for durationMs while the user
    // looks at the camera and holds still, and sets the baselines
    // used for eye-contact/blink detection from it. Call once, right
    // after start(), before any question is being answered.
    async calibrate(durationMs) {
      const yaws = [];
      const pitches = [];
      const blinkScores = [];
      const faceScales = [];

      const deadline = performance.now() + durationMs;

      while (performance.now() < deadline) {
        const result = detectOnce();

        if (result) {
          if (result.facialTransformationMatrixes?.length) {
            const { yaw, pitch } = rotationFromMatrix(
              result.facialTransformationMatrixes[0].data
            );
            yaws.push(yaw);
            pitches.push(pitch);
          }

          const blinkScore = blinkScoreFrom(result);
          if (blinkScore !== null) blinkScores.push(blinkScore);

          faceScales.push(eyeDistance(result.faceLandmarks[0]));
        }

        await new Promise((resolve) => requestAnimationFrame(resolve));
      }

      if (yaws.length) {
        baselineYaw = yaws.reduce((a, b) => a + b, 0) / yaws.length;
        baselinePitch = pitches.reduce((a, b) => a + b, 0) / pitches.length;
      }

      if (faceScales.length) {
        baselineFaceScale = faceScales.reduce((a, b) => a + b, 0) / faceScales.length;
      }

      if (blinkScores.length) {
        const avgOpenScore =
          blinkScores.reduce((a, b) => a + b, 0) / blinkScores.length;
        // Threshold sits halfway between this person's resting
        // "eyes open" score and fully-closed (1.0), never lower than
        // the default so a naturally low resting score can't make
        // blink detection oversensitive.
        blinkThreshold = Math.max(
          DEFAULT_BLINK_THRESHOLD,
          avgOpenScore + (1 - avgOpenScore) * 0.5
        );
      }

      resetCounters();
    },

    // Returns a plain, numeric-only summary of signals accumulated
    // since the last reset() - safe to send to the backend as-is.
    getSignalsSinceReset() {
      const elapsedMs = performance.now() - startedAt;
      const elapsedMin = elapsedMs / 60000;

      const longestLookAwayMs = lookAwayEvents.length
        ? Math.max(...lookAwayEvents.map((event) => event.duration_ms))
        : 0;

      const longestEyesClosedMs = sustainedEyesClosedEvents.length
        ? Math.max(...sustainedEyesClosedEvents.map((event) => event.duration_ms))
        : 0;

      const longestPostureShiftMs = postureShiftEvents.length
        ? Math.max(...postureShiftEvents.map((event) => event.duration_ms))
        : 0;

      return {
        frames_sampled: framesSampled,
        face_present_pct: framesAttempted
          ? Math.round((framesSampled / framesAttempted) * 100)
          : null,
        eye_contact_pct: framesSampled
          ? Math.round((onCameraFrames / framesSampled) * 100)
          : null,
        look_away_count: lookAwayEvents.length,
        longest_look_away_ms: Math.round(longestLookAwayMs),
        look_away_events: topEvents(lookAwayEvents),
        blink_rate_per_min:
          elapsedMin > 0 ? Math.round(blinkEvents / elapsedMin) : null,
        longest_eyes_closed_ms: Math.round(longestEyesClosedMs),
        eyes_closed_events: topEvents(sustainedEyesClosedEvents),
        longest_posture_shift_ms: Math.round(longestPostureShiftMs),
        posture_shift_events: topEvents(postureShiftEvents),
        movement_score: framesSampled
          ? Math.round((movementAccum / framesSampled) * 1000) / 1000
          : null,
      };
    },

    // Clears accumulated counters (call between questions) without
    // tearing down the camera stream/model or the calibrated
    // baselines.
    reset() {
      resetCounters();
    },

    // Fully tears down - stop the detection loop, camera tracks, and
    // release the model. Call once when leaving the interview.
    stop() {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = null;

      faceLandmarker?.close();
      faceLandmarker = null;

      if (videoEl) {
        videoEl.pause();
        videoEl.srcObject = null;
        videoEl = null;
      }

      stream?.getTracks().forEach((track) => track.stop());
      stream = null;
    },
  };
}
