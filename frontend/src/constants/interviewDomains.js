// Hand-derived from backend/app/services/role_classifier.py — domain and
// sub-domain codes must stay in sync with that file's classify_role() /
// classify_*_subrole() return values if they ever change.
export const INTERVIEW_DOMAINS = [
  {
    code: "software",
    label: "Software Engineering",
    subDomains: [
      { code: "ml_data_science", label: "ML / Data Science" },
      { code: "data_engineering", label: "Data Engineering" },
      { code: "frontend", label: "Frontend" },
      { code: "mobile", label: "Mobile" },
      { code: "devops_sre", label: "DevOps / SRE" },
      { code: "qa_testing", label: "QA / Testing" },
      { code: "generic", label: "General Software (SDE / Full-stack)" },
    ],
  },
  {
    code: "finance",
    label: "Finance",
    subDomains: [
      { code: "investment_banking_pe", label: "Investment Banking / PE" },
      { code: "equity_research", label: "Equity Research" },
      { code: "corporate_finance_treasury", label: "Corporate Finance / Treasury" },
      { code: "risk_management", label: "Risk Management" },
      { code: "venture_capital", label: "Venture Capital" },
      { code: "generic", label: "General Finance" },
    ],
  },
  {
    code: "consulting",
    label: "Consulting",
    subDomains: [
      { code: "operations_consulting", label: "Operations Consulting" },
      { code: "digital_consulting", label: "Digital / Technology Consulting" },
      { code: "generic", label: "General Consulting" },
    ],
  },
  {
    code: "sales",
    label: "Sales",
    subDomains: [
      { code: "customer_success", label: "Customer Success" },
      { code: "generic", label: "General Sales" },
    ],
  },
  {
    code: "marketing",
    label: "Marketing",
    subDomains: [
      { code: "brand_management", label: "Brand Management" },
      { code: "seo", label: "SEO" },
      { code: "content_marketing", label: "Content Marketing" },
      { code: "product_marketing", label: "Product Marketing" },
      { code: "generic", label: "General Marketing" },
    ],
  },
  {
    code: "vlsi",
    label: "VLSI",
    subDomains: [
      { code: "physical_design", label: "Physical Design" },
      { code: "dft", label: "DFT (Design for Test)" },
      { code: "sta_timing", label: "STA / Timing" },
      { code: "generic", label: "General VLSI" },
    ],
  },
  {
    code: "digital_design",
    label: "Digital Design",
    subDomains: [
      { code: "fpga", label: "FPGA" },
      { code: "verification_dv", label: "Verification / DV" },
      { code: "generic", label: "General Digital Design" },
    ],
  },
  {
    code: "embedded_systems",
    label: "Embedded Systems",
    subDomains: [
      { code: "embedded_linux", label: "Embedded Linux" },
      { code: "iot", label: "IoT" },
      { code: "automotive_embedded", label: "Automotive Embedded" },
      { code: "generic", label: "General Embedded" },
    ],
  },
  {
    code: "analog_design",
    label: "Analog Design",
    subDomains: [
      { code: "mixed_signal", label: "Mixed Signal" },
      { code: "generic", label: "General Analog Design" },
    ],
  },
  {
    code: "product_management",
    label: "Product Management",
    subDomains: [
      { code: "technical_pm", label: "Technical PM" },
      { code: "growth_pm", label: "Growth PM" },
      { code: "product_analyst", label: "Product Analyst" },
      { code: "generic", label: "General PM" },
    ],
  },
];

export function getDomainLabel(domainCode) {
  return INTERVIEW_DOMAINS.find((domain) => domain.code === domainCode)?.label || domainCode;
}

export function getSubDomainLabel(domainCode, subDomainCode) {
  const domain = INTERVIEW_DOMAINS.find((entry) => entry.code === domainCode);
  return domain?.subDomains.find((sub) => sub.code === subDomainCode)?.label || subDomainCode;
}
