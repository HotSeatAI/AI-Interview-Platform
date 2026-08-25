/**
 * Presentation-only helpers for the Resume Intelligence result page.
 *
 * These functions never alter score, matching, or recommendation
 * data — they only translate the existing structured backend
 * output (enum values, numbers) into plain, student-friendly
 * copy. No internal/technical terms (e.g. "controlled-concept",
 * "fuzzy", "semantic verification") are ever surfaced here.
 */

export const STATUS_LABELS = {
  strong: "Strong Match",
  partial: "Partial Match",
  ambiguous: "Needs Review",
  missing: "Not Found",
};

export function getStatusLabel(matchType) {
  return STATUS_LABELS[matchType] || "Not Found";
}

export function getStatusTone(matchType) {
  switch (matchType) {
    case "strong":
      return "positive";
    case "partial":
      return "info";
    case "ambiguous":
      return "warning";
    default:
      return "neutral";
  }
}

const PRIORITY_LABELS = {
  required: "Required",
  preferred: "Preferred",
  nice_to_have: "Nice to Have",
  unclear: "Unclear",
};

export function getPriorityLabel(importance) {
  return PRIORITY_LABELS[importance] || "Unclear";
}

export function getPriorityTone(importance) {
  switch (importance) {
    case "required":
      return "critical";
    case "preferred":
      return "info";
    default:
      return "neutral";
  }
}

/**
 * Buckets a raw 0-1 confidence value into a human-friendly
 * label. Purely a display transform of an existing number —
 * no scoring logic is touched.
 */
export function getConfidenceLabel(confidence) {
  if (confidence >= 0.75) return "High";
  if (confidence >= 0.45) return "Medium";
  if (confidence > 0) return "Low";
  return "None";
}

/**
 * Plain-language explanation of why a requirement did or did
 * not match, based only on the structured evidence_type enum
 * — never the backend's free-text "reason" string, so no
 * internal terminology can leak through.
 */
const EVIDENCE_TYPE_EXPLANATIONS = {
  direct: "This is explicitly demonstrated in your resume.",
  indirect:
    "Your resume shows related experience that supports this.",
  partial:
    "Your resume shows some evidence for this, but not a complete match.",
  ambiguous:
    "Your resume has related content, but it isn't explicit enough to confirm this.",
  unsupported: "No reliable evidence was found in your resume for this.",
  adjacent:
    "Your resume shows experience with a related technology, but not the specific one requested.",
};

export function getEvidenceExplanation(evidenceType) {
  return (
    EVIDENCE_TYPE_EXPLANATIONS[evidenceType] ||
    EVIDENCE_TYPE_EXPLANATIONS.unsupported
  );
}

export function getEvidenceFoundSummary(match) {
  const count = match.matched_resume_evidence?.length || 0;

  if (match.match_type === "strong" || match.match_type === "partial") {
    return count === 1 ? "1 example found" : `${count} examples found`;
  }

  if (match.match_type === "ambiguous") {
    return "Unclear evidence";
  }

  return "None found";
}

export function getRecommendedAction(match) {
  switch (match.match_type) {
    case "strong":
      return "No action needed";
    case "partial":
      return "Consider strengthening the wording";
    case "ambiguous":
      return "Review your resume for clearer evidence";
    default:
      return "Do not add unless true";
  }
}

const CHANGE_TYPE_LABELS = {
  rewrite: "Wording improvement",
  clarify: "Clarity improvement",
  quantify: "Add supported detail",
  surface_keyword: "Surface existing skill",
  improve_action_verb: "Stronger action verb",
  improve_impact: "Clearer impact",
  improve_specificity: "More specific wording",
};

export function getChangeTypeLabel(changeType) {
  return CHANGE_TYPE_LABELS[changeType] || "Suggested improvement";
}

export function getResumeArea(recommendation) {
  return recommendation.jd_requirement || getChangeTypeLabel(recommendation.change_type);
}

export function getSafetyBadge(safetyStatus) {
  if (safetyStatus === "safe") {
    return { label: "Evidence-Backed", tone: "positive" };
  }

  return { label: "Verify Before Adding", tone: "warning" };
}

/**
 * Overview-tab derivations. All computed from matching_report
 * data that already exists — no new analysis is performed.
 */

export function buildOverviewSummary(matchingReport) {
  const summary = matchingReport?.summary;

  if (!summary || summary.total_requirements === 0) {
    return "We couldn't find any requirements to compare against your resume.";
  }

  const {
    strong_matches,
    total_requirements,
    required_matched,
    required_requirements,
  } = summary;

  let sentence = `Your resume strongly matches ${strong_matches} of ${total_requirements} requirements for this role`;

  if (required_requirements > 0) {
    sentence += `, including ${required_matched} of ${required_requirements} required qualifications`;
  }

  sentence += ".";

  return sentence;
}

export function getStrongestArea(matches) {
  if (!matches?.length) return null;

  const strong = matches.filter((match) => match.match_type === "strong");

  const pool = strong.length
    ? strong
    : matches.filter((match) => match.match_type === "partial");

  if (!pool.length) return null;

  return pool.reduce((best, current) =>
    current.score > best.score ? current : best
  );
}

export function getPriorityArea(matches) {
  if (!matches?.length) return null;

  const weak = matches.filter(
    (match) =>
      match.match_type === "missing" || match.match_type === "ambiguous"
  );

  if (weak.length) {
    const required = weak.filter((match) => match.importance === "required");
    const pool = required.length ? required : weak;

    return pool.reduce((top, current) =>
      current.weight > top.weight ? current : top
    );
  }

  const partial = matches.filter((match) => match.match_type === "partial");

  if (partial.length) {
    return partial.reduce((top, current) =>
      current.weight > top.weight ? current : top
    );
  }

  return null;
}
