// Mock interviewer directory + availability, standing in for a future
// backend-backed peer-interviewer marketplace. Dates are generated off
// today's date (not hardcoded) so slots never look stale/expired.

function isoDateOffset(daysFromToday) {
  const date = new Date();
  date.setDate(date.getDate() + daysFromToday);
  return date.toISOString().slice(0, 10);
}

function slot(id, daysFromToday, startTime, endTime) {
  return { id, date: isoDateOffset(daysFromToday), start_time: startTime, end_time: endTime };
}

export const MOCK_INTERVIEWERS = [
  {
    id: "intv_software_1",
    name: "Ananya Rao",
    domain: "software",
    sub_domains: ["frontend", "generic"],
    experience_years: 6,
    rating: 4.8,
    bio: "Senior frontend engineer at a fintech startup; loves React deep-dives.",
    slots: [
      slot("slot_software_1_1", 1, "09:00", "10:00"),
      slot("slot_software_1_2", 4, "18:30", "19:30"),
    ],
  },
  {
    id: "intv_software_2",
    name: "Marcus Chen",
    domain: "software",
    sub_domains: ["devops_sre", "qa_testing"],
    experience_years: 8,
    rating: 4.6,
    bio: "SRE lead who's run interview loops for infra teams at two unicorns.",
    slots: [
      slot("slot_software_2_1", 2, "14:00", "15:00"),
      slot("slot_software_2_2", 7, "10:00", "11:00"),
    ],
  },
  {
    id: "intv_software_3",
    name: "Priya Nair",
    domain: "software",
    sub_domains: ["ml_data_science", "data_engineering"],
    experience_years: 5,
    rating: 4.9,
    bio: "ML engineer building recommendation systems; ex-FAANG interviewer.",
    slots: [
      slot("slot_software_3_1", 3, "19:00", "20:00"),
      slot("slot_software_3_2", 6, "08:30", "09:30"),
    ],
  },
  {
    id: "intv_finance_1",
    name: "David Whitfield",
    domain: "finance",
    sub_domains: ["investment_banking_pe", "generic"],
    experience_years: 9,
    rating: 4.7,
    bio: "Ex-bulge-bracket associate, now coaching IB/PE case interviews.",
    slots: [
      slot("slot_finance_1_1", 2, "09:30", "10:30"),
      slot("slot_finance_1_2", 5, "17:30", "18:30"),
    ],
  },
  {
    id: "intv_finance_2",
    name: "Sofia Martins",
    domain: "finance",
    sub_domains: ["equity_research", "risk_management"],
    experience_years: 6,
    rating: 4.5,
    bio: "Equity research associate covering tech; sharp on valuation drills.",
    slots: [
      slot("slot_finance_2_1", 4, "13:00", "14:00"),
    ],
  },
  {
    id: "intv_consulting_1",
    name: "James O'Connor",
    domain: "consulting",
    sub_domains: ["operations_consulting", "generic"],
    experience_years: 7,
    rating: 4.6,
    bio: "MBB alum; runs case-interview prep for ops and strategy roles.",
    slots: [
      slot("slot_consulting_1_1", 1, "16:00", "17:00"),
      slot("slot_consulting_1_2", 8, "09:00", "10:00"),
    ],
  },
  {
    id: "intv_consulting_2",
    name: "Lena Fischer",
    domain: "consulting",
    sub_domains: ["digital_consulting"],
    experience_years: 4,
    rating: 4.4,
    bio: "Digital transformation consultant, big on structured frameworks.",
    slots: [
      slot("slot_consulting_2_1", 6, "11:00", "12:00"),
    ],
  },
  {
    id: "intv_sales_1",
    name: "Carlos Mendes",
    domain: "sales",
    sub_domains: ["customer_success", "generic"],
    experience_years: 5,
    rating: 4.3,
    bio: "Enterprise AE turned CS lead; great for pitch/objection-handling practice.",
    slots: [
      slot("slot_sales_1_1", 3, "10:00", "11:00"),
      slot("slot_sales_1_2", 9, "15:00", "16:00"),
    ],
  },
  {
    id: "intv_sales_2",
    name: "Grace Kim",
    domain: "sales",
    sub_domains: ["generic"],
    experience_years: 3,
    rating: 4.2,
    bio: "SMB sales rep of the quarter, twice; loves roleplay-style mocks.",
    slots: [
      slot("slot_sales_2_1", 5, "18:00", "19:00"),
    ],
  },
  {
    id: "intv_marketing_1",
    name: "Isabella Rossi",
    domain: "marketing",
    sub_domains: ["brand_management", "product_marketing"],
    experience_years: 6,
    rating: 4.7,
    bio: "Brand marketing lead at a DTC company; strong on positioning drills.",
    slots: [
      slot("slot_marketing_1_1", 2, "08:00", "09:00"),
      slot("slot_marketing_1_2", 7, "14:30", "15:30"),
    ],
  },
  {
    id: "intv_marketing_2",
    name: "Noah Bennett",
    domain: "marketing",
    sub_domains: ["seo", "content_marketing"],
    experience_years: 4,
    rating: 4.5,
    bio: "SEO/content lead, ex-agency; can grill on growth-loop case studies.",
    slots: [
      slot("slot_marketing_2_1", 4, "19:30", "20:30"),
    ],
  },
  {
    id: "intv_vlsi_1",
    name: "Rajesh Kumar",
    domain: "vlsi",
    sub_domains: ["physical_design", "sta_timing"],
    experience_years: 10,
    rating: 4.9,
    bio: "Staff PD engineer; deep on timing closure and floorplanning questions.",
    slots: [
      slot("slot_vlsi_1_1", 1, "09:00", "10:00"),
      slot("slot_vlsi_1_2", 6, "17:00", "18:00"),
    ],
  },
  {
    id: "intv_vlsi_2",
    name: "Mei Ling",
    domain: "vlsi",
    sub_domains: ["dft", "generic"],
    experience_years: 5,
    rating: 4.4,
    bio: "DFT engineer, scan/ATPG focus; runs practical mock rounds.",
    slots: [
      slot("slot_vlsi_2_1", 8, "12:00", "13:00"),
    ],
  },
  {
    id: "intv_digital_design_1",
    name: "Ethan Brooks",
    domain: "digital_design",
    sub_domains: ["fpga", "verification_dv"],
    experience_years: 7,
    rating: 4.6,
    bio: "FPGA/DV engineer at an aerospace supplier; loves SystemVerilog quizzing.",
    slots: [
      slot("slot_dd_1_1", 3, "09:00", "10:00"),
      slot("slot_dd_1_2", 5, "20:00", "21:00"),
    ],
  },
  {
    id: "intv_digital_design_2",
    name: "Hannah Schmidt",
    domain: "digital_design",
    sub_domains: ["generic"],
    experience_years: 3,
    rating: 4.3,
    bio: "RTL design engineer, first two years in ASIC verification.",
    slots: [
      slot("slot_dd_2_1", 9, "10:30", "11:30"),
    ],
  },
  {
    id: "intv_embedded_systems_1",
    name: "Oscar Delgado",
    domain: "embedded_systems",
    sub_domains: ["embedded_linux", "iot"],
    experience_years: 8,
    rating: 4.7,
    bio: "Embedded Linux/IoT platform lead; strong on driver + bring-up questions.",
    slots: [
      slot("slot_embedded_1_1", 2, "07:30", "08:30"),
      slot("slot_embedded_1_2", 7, "18:00", "19:00"),
    ],
  },
  {
    id: "intv_embedded_systems_2",
    name: "Fatima Al-Sayed",
    domain: "embedded_systems",
    sub_domains: ["automotive_embedded", "generic"],
    experience_years: 6,
    rating: 4.5,
    bio: "Automotive embedded engineer, AUTOSAR/functional-safety background.",
    slots: [
      slot("slot_embedded_2_1", 4, "13:30", "14:30"),
    ],
  },
  {
    id: "intv_analog_design_1",
    name: "Viktor Petrov",
    domain: "analog_design",
    sub_domains: ["mixed_signal", "generic"],
    experience_years: 9,
    rating: 4.8,
    bio: "Mixed-signal IC designer; grills on ADC/DAC and noise-analysis basics.",
    slots: [
      slot("slot_analog_1_1", 1, "11:00", "12:00"),
      slot("slot_analog_1_2", 10, "09:30", "10:30"),
    ],
  },
  {
    id: "intv_analog_design_2",
    name: "Chloe Dubois",
    domain: "analog_design",
    sub_domains: ["generic"],
    experience_years: 4,
    rating: 4.4,
    bio: "Analog layout engineer moving into design; enjoys teaching fundamentals.",
    slots: [
      slot("slot_analog_2_1", 6, "16:30", "17:30"),
    ],
  },
  {
    id: "intv_product_management_1",
    name: "Ryan Park",
    domain: "product_management",
    sub_domains: ["technical_pm", "growth_pm"],
    experience_years: 7,
    rating: 4.7,
    bio: "Senior PM at a B2B SaaS company; strong on product-sense and metrics cases.",
    slots: [
      slot("slot_pm_1_1", 2, "10:00", "11:00"),
      slot("slot_pm_1_2", 5, "19:00", "20:00"),
    ],
  },
  {
    id: "intv_product_management_2",
    name: "Aisha Bello",
    domain: "product_management",
    sub_domains: ["product_analyst", "generic"],
    experience_years: 3,
    rating: 4.3,
    bio: "Product analyst turned APM; good for early-career PM mocks.",
    slots: [
      slot("slot_pm_2_1", 9, "08:00", "09:00"),
    ],
  },
];
