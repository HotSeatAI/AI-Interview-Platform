import { createContext, useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  startResumeAnalysis,
  getResumeAnalysisStatus,
} from "../api/resumeAnalysisApi";
import useAuth from "../hooks/useAuth";
import {
  loadResumeAnalysisState,
  saveResumeAnalysisState,
  clearResumeAnalysisState,
} from "../utils/resumeAnalysisStorage";

const ResumeAnalysisContext = createContext(null);

const POLL_INTERVAL_MS = 1500;

const IDLE_STATE = {
  resumeId: "",
  jobDescription: "",
  status: "idle",
  analysisId: null,
  progress: 0,
  currentStage: null,
  errorMessage: "",
};

function getInitialState() {
  const stored = loadResumeAnalysisState();

  if (!stored) {
    return { ...IDLE_STATE };
  }

  return {
    resumeId: stored.resumeId ?? "",
    jobDescription: stored.jobDescription ?? "",
    // An in-flight request cannot survive a refresh - re-verify with the
    // backend before trusting "analyzing" instead of just assuming it.
    status: stored.status === "analyzing" ? "restoring" : (stored.status ?? "idle"),
    analysisId: stored.analysisId ?? null,
    progress: stored.progress ?? 0,
    currentStage: stored.currentStage ?? null,
    errorMessage: stored.errorMessage ?? "",
  };
}

export function ResumeAnalysisProvider({ children }) {
  const { token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [state, setState] = useState(getInitialState);
  const [jobDescriptionFile, setJobDescriptionFileState] = useState(null);
  const [starting, setStarting] = useState(false);

  const locationRef = useRef(location.pathname);
  locationRef.current = location.pathname;

  // Persist the restorable slice. The raw File is never written here - it
  // can't survive serialization/refresh, and once a request has been sent
  // the backend already has it, so nothing is lost by not keeping it.
  useEffect(() => {
    saveResumeAnalysisState({
      resumeId: state.resumeId,
      jobDescription: state.jobDescription,
      status: state.status === "restoring" ? "analyzing" : state.status,
      analysisId: state.analysisId,
      progress: state.progress,
      currentStage: state.currentStage,
      errorMessage: state.errorMessage,
    });
  }, [state]);

  // If the authenticated identity changes (logout, or a different user logs
  // in in the same tab), this analysis belongs to the previous session -
  // don't leak it forward. Skip on the very first resolution of `token`
  // (that's just normal auth init, not a switch) so a refresh-restored
  // in-progress analysis isn't wiped out before it gets a chance to verify.
  const prevTokenRef = useRef(undefined);
  useEffect(() => {
    if (prevTokenRef.current !== undefined && prevTokenRef.current !== token) {
      clearResumeAnalysisState();
      setState({ ...IDLE_STATE });
      setJobDescriptionFileState(null);
    }
    prevTokenRef.current = token;
  }, [token]);

  const setResumeId = useCallback((resumeId) => {
    setState((prev) => ({ ...prev, resumeId }));
  }, []);

  const setJobDescription = useCallback((jobDescription) => {
    setState((prev) => ({ ...prev, jobDescription }));
    if (jobDescription.trim()) {
      setJobDescriptionFileState(null);
    }
  }, []);

  const setJobDescriptionFile = useCallback((file) => {
    setJobDescriptionFileState(file);
    if (file) {
      setState((prev) => ({ ...prev, jobDescription: "" }));
    }
  }, []);

  const setErrorMessage = useCallback((message) => {
    setState((prev) => ({ ...prev, errorMessage: message }));
  }, []);

  const resetAnalysis = useCallback(() => {
    setState((prev) => ({
      ...prev,
      status: "idle",
      analysisId: null,
      progress: 0,
      currentStage: null,
      errorMessage: "",
    }));
  }, []);

  const startAnalysis = useCallback(async () => {
    // Guard against duplicate/concurrent analyses: rapid double-clicks, or
    // calling this while an analysis (or its post-refresh re-verification)
    // is already in flight.
    if (starting || state.status === "analyzing" || state.status === "restoring") {
      return;
    }

    if (!state.resumeId) {
      setErrorMessage("Please select a resume to evaluate.");
      return;
    }

    if (!state.jobDescription.trim() && !jobDescriptionFile) {
      setErrorMessage("Please provide a job description.");
      return;
    }

    try {
      setStarting(true);
      setErrorMessage("");

      const result = await startResumeAnalysis({
        resumeId: state.resumeId,
        jobDescription: state.jobDescription,
        jobDescriptionFile,
        token,
      });

      setState((prev) => ({
        ...prev,
        status: "analyzing",
        analysisId: result.analysis_id,
        progress: result.progress ?? 0,
        currentStage: result.current_stage ?? null,
        errorMessage: "",
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        status: "error",
        errorMessage: err?.response?.data?.detail || "Failed to start resume analysis.",
      }));
    } finally {
      setStarting(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [starting, state.status, state.resumeId, state.jobDescription, jobDescriptionFile, token]);

  // Owns the polling (and, right after a refresh, the one-shot truth check)
  // for an active analysis. This effect lives in a provider mounted above
  // the routed pages (see App.jsx), so it keeps running across in-app route
  // navigation - only a hard refresh/tab close ever unmounts it.
  useEffect(() => {
    const isLive = state.status === "analyzing" || state.status === "restoring";
    if (!isLive || !state.analysisId || !token) {
      return undefined;
    }

    let cancelled = false;
    let timeoutId;

    const poll = async () => {
      try {
        const statusResponse = await getResumeAnalysisStatus(state.analysisId, token);
        if (cancelled) return;

        if (statusResponse.status === "completed") {
          setState((prev) => ({ ...prev, status: "completed", progress: 100 }));

          // Only auto-jump to the result if the user is actually sitting on
          // the Resume page right now - never yank them off whatever page
          // they navigated to while this was running in the background.
          if (locationRef.current === "/resume") {
            navigate(`/resume-analysis/${state.analysisId}`);
          }
          return;
        }

        if (statusResponse.status === "failed") {
          setState((prev) => ({
            ...prev,
            status: "error",
            errorMessage: statusResponse.error_message || "Resume analysis failed.",
          }));
          return;
        }

        setState((prev) => ({
          ...prev,
          status: "analyzing",
          progress: statusResponse.progress ?? prev.progress,
          currentStage: statusResponse.current_stage ?? prev.currentStage,
        }));

        timeoutId = setTimeout(poll, POLL_INTERVAL_MS);
      } catch {
        if (cancelled) return;
        setState((prev) => ({
          ...prev,
          status: "error",
          errorMessage: "Unable to check analysis progress.",
        }));
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [state.status, state.analysisId, token, navigate]);

  const value = {
    resumeId: state.resumeId,
    jobDescription: state.jobDescription,
    jobDescriptionFile,
    status: state.status,
    starting,
    analysisId: state.analysisId,
    progress: state.progress,
    currentStage: state.currentStage,
    errorMessage: state.errorMessage,
    setResumeId,
    setJobDescription,
    setJobDescriptionFile,
    setErrorMessage,
    startAnalysis,
    resetAnalysis,
  };

  return (
    <ResumeAnalysisContext.Provider value={value}>
      {children}
    </ResumeAnalysisContext.Provider>
  );
}

export default ResumeAnalysisContext;
