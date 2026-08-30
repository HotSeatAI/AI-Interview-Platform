import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  getResumeAnalysisResult,
} from "../api/resumeAnalysisApi";
import useAuth from "../hooks/useAuth";

import Navbar from "../components/layout/Navbar.jsx";
import AnalysisTabs from "../components/resume-analysis/AnalysisTabs";
import AnalysisSummary from "../components/resume-analysis/AnalysisSummary";
import RequirementTable from "../components/resume-analysis/RequirementTable";
import ImprovementTable from "../components/resume-analysis/ImprovementTable";
import ReviewAreasTable from "../components/resume-analysis/ReviewAreasTable";
import AtsFindingsTable from "../components/resume-analysis/AtsFindingsTable";

const JD_AWARE_TABS = [
  { id: "overview", label: "Overview" },
  { id: "requirements", label: "Requirements" },
  { id: "improvements", label: "Improvements" },
  { id: "review", label: "Review Areas" },
];

const STANDALONE_TABS = [
  { id: "overview", label: "Overview" },
  { id: "findings", label: "Findings" },
];

export default function ResumeAnalysisPage() {
  const { analysisId } =
    useParams();

  const [analysis, setAnalysis] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [activeTab, setActiveTab] =
    useState("overview");

  const { token } = useAuth();

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadResult = async () => {
      try {
        const result =
          await getResumeAnalysisResult(
            analysisId,
            token
          );

        setAnalysis(result);

      } catch (err) {
        // Don't log the raw error - it carries the request's Authorization
        // header (Bearer token) in its config.
        console.error(
          "Failed to load analysis:",
          err?.response?.data?.detail || err?.message
        );

        setError(
          err?.response?.data?.detail ||
            "Unable to load analysis."
        );

      } finally {
        setLoading(false);
      }
    };

    loadResult();
  }, [analysisId, token]);

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="analysis-loading">
          Loading analysis...
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <div className="analysis-error">
          {error}
        </div>
      </>
    );
  }

  if (!analysis) {
    return null;
  }

  const result =
    analysis.result;

  const isStandalone = analysis.mode
    ? analysis.mode === "standalone"
    : !analysis.job_title;

  const matchingReport =
    result.matching_report;

  const recommendationReport =
    result.recommendation_report;

  const atsReport =
    analysis.ats_report;

  const missingAndReviewCount =
    (matchingReport?.summary?.missing_matches ?? 0) +
    (matchingReport?.summary?.ambiguous_matches ?? 0);

  const baseTabs = isStandalone ? STANDALONE_TABS : JD_AWARE_TABS;

  const tabs = baseTabs.map((tab) => {

    if (tab.id === "requirements") {
      return {
        ...tab,
        count: matchingReport?.matches?.length ?? 0,
      };
    }

    if (tab.id === "improvements") {
      return {
        ...tab,
        count: recommendationReport?.recommendations?.length ?? 0,
      };
    }

    if (tab.id === "review") {
      return {
        ...tab,
        count: missingAndReviewCount,
      };
    }

    if (tab.id === "findings") {
      return {
        ...tab,
        count: atsReport?.findings?.length ?? 0,
      };
    }

    return tab;
  });

  return (
    <>
    <Navbar />
    <main className="resume-analysis-page">

      <section className="analysis-header">
        <div>
          <span>
            Resume Intelligence
          </span>

          <h1>
            {analysis.job_title ||
              (isStandalone
                ? "ATS Compatibility Check"
                : "Resume Analysis")}
          </h1>

          <p>
            {isStandalone
              ? "How well an ATS can parse and rank this resume, plus what to fix to raise the score."
              : "Evidence-backed analysis of your resume against this job description."}
          </p>
        </div>
      </section>

      <AnalysisTabs
        tabs={tabs}
        activeTab={activeTab}
        onChange={setActiveTab}
      />

      {activeTab === "overview" && (
        <AnalysisSummary
          score={analysis.overall_score}
          matchingReport={matchingReport}
          atsReport={atsReport}
        />
      )}

      {activeTab === "findings" && (
        <AtsFindingsTable
          findings={atsReport?.findings}
        />
      )}

      {activeTab === "requirements" && (
        <RequirementTable
          matches={matchingReport?.matches}
          partialMatchGuidance={
            recommendationReport?.partial_match_guidance
          }
        />
      )}

      {activeTab === "improvements" && (
        <ImprovementTable
          recommendations={
            recommendationReport?.recommendations
          }
          keepAsIs={
            recommendationReport?.keep_as_is
          }
        />
      )}

      {activeTab === "review" && (
        <ReviewAreasTable
          matches={matchingReport?.matches}
          missingActions={
            recommendationReport?.missing_requirement_actions
          }
        />
      )}

    </main>
    </>
  );
}
