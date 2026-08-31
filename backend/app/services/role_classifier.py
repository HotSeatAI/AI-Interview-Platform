"""
Role classification service.

This module determines which interview category a selected role belongs to.

Classification strategy:

1. Exact role matching
2. Keyword matching
3. Gemini fallback

Returns exactly one category:

- software
- finance
- consulting
- sales
- marketing
- digital_design
- analog_design
- embedded_systems
- vlsi
- product_management
"""

from app.services.api_key_manager import api_key_manager


SOFTWARE_KEYWORDS = {
    "software engineer",
    "software developer",
    "backend engineer",
    "backend developer",
    "frontend engineer",
    "frontend developer",
    "front end engineer",
    "back end engineer",
    "full stack engineer",
    "full stack developer",
    "fullstack developer",
    "web developer",
    "application developer",
    "python developer",
    "java developer",
    "c++ developer",
    "cpp developer",
    "android developer",
    "ios developer",
    "mobile developer",
    "cloud engineer",
    "devops engineer",
    "site reliability engineer",
    "sre",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "artificial intelligence engineer",
    "data engineer",
    "data scientist",
    "sde",
"software development engineer",
"full stack",
"frontend",
"backend",
"web engineer",
"application engineer",
"java engineer",
"python engineer",
"c++ engineer",
"cpp engineer",
"react developer",
"node developer",
"ios engineer",
"android engineer",
}


FINANCE_KEYWORDS = {
    "financial analyst",
    "finance analyst",
    "investment banking",
    "investment banker",
    "investment analyst",
    "equity research",
    "equity analyst",
    "portfolio manager",
    "portfolio analyst",
    "treasury",
    "risk analyst",
    "valuation",
    "corporate finance",
    "private equity",
    "venture capital",
    "asset management",
    "wealth management",
    "credit analyst",
}


CONSULTING_KEYWORDS = {
    "consultant",
    "management consultant",
    "strategy consultant",
    "business consultant",
    "operations consultant",
    "business consulting",
    "management consulting",
    "operations consulting",
    "advisory",
    "business analyst",
}


SALES_KEYWORDS = {
    "sales executive",
    "sales manager",
    "business development",
    "business development representative",
    "sales development representative",
    "account executive",
    "account manager",
    "relationship manager",
    "customer success",
    "inside sales",
    "enterprise sales",
}


MARKETING_KEYWORDS = {
    "marketing",
    "marketing analyst",
    "digital marketing",
    "performance marketing",
    "growth marketing",
    "product marketing",
    "brand manager",
    "branding",
    "seo",
    "sem",
    "content marketing",
}


DIGITAL_DESIGN_KEYWORDS = {
    "rtl",
    "rtl engineer",
    "rtl design",
    "digital design",
    "digital design engineer",
    "asic",
    "asic engineer",
    "asic design engineer",
    "logic design",
    "logic design engineer",
    "verification engineer",
    "design verification",
    "dv engineer",
    "fpga",
    "fpga engineer",
    "fpga design engineer",
    "verilog",
    "systemverilog",
    "rtl developer",
"verification",
"design verification engineer",
}


ANALOG_DESIGN_KEYWORDS = {
    "analog",
    "analog design",
    "analog engineer",
    "analog design engineer",
    "analog ic",
    "analog ic design",
    "analog ic engineer",
    "mixed signal",
    "mixed signal engineer",
    "mixed signal design",
    "circuit design",
}


EMBEDDED_SYSTEMS_KEYWORDS = {
    "embedded",
    "embedded engineer",
    "embedded systems",
    "embedded systems engineer",
    "embedded software",
    "embedded software engineer",
    "firmware",
    "firmware engineer",
    "device driver",
    "device driver engineer",
    "microcontroller",
    "microcontroller engineer",
    "iot",
    "automotive embedded",
    "embedded linux",
"embedded linux engineer",
"linux kernel",
"kernel developer",
}


VLSI_KEYWORDS = {
    "vlsi",
    "physical design",
    "physical design engineer",
    "backend vlsi",
    "physical verification",
    "timing engineer",
    "sta",
    "static timing",
    "dft",
    "scan",
    "pd engineer",
    "synthesis",
"synthesis engineer",
"physical implementation",
"timing closure",
"physical design",
"backend physical design",
}


PRODUCT_MANAGEMENT_KEYWORDS = {
    "product manager",
    "associate product manager",
    "assistant product manager",
    "apm",
    "technical product manager",
    "group product manager",
    "senior product manager",
    "principal product manager",
    "product owner",
    "product analyst",
    "product management",
    "growth product manager",
    "platform product manager",
}
class RoleClassifier:
    """
    Classifies interview roles into predefined interview categories.
    """

    def __init__(self):

        self.key_manager = api_key_manager

    @staticmethod
    def _normalize_role(role: str) -> str:
        return role.strip().lower()

    def _exact_match(self, role: str) -> str | None:

        role = self._normalize_role(role)

        if role in DIGITAL_DESIGN_KEYWORDS:
            return "digital_design"

        if role in ANALOG_DESIGN_KEYWORDS:
            return "analog_design"

        if role in EMBEDDED_SYSTEMS_KEYWORDS:
            return "embedded_systems"

        if role in VLSI_KEYWORDS:
            return "vlsi"

        if role in PRODUCT_MANAGEMENT_KEYWORDS:
            return "product_management"

        if role in FINANCE_KEYWORDS:
            return "finance"

        if role in CONSULTING_KEYWORDS:
            return "consulting"

        if role in SALES_KEYWORDS:
            return "sales"

        if role in MARKETING_KEYWORDS:
            return "marketing"

        if role in SOFTWARE_KEYWORDS:
            return "software"

        return None
    def _keyword_match(self, role: str) -> str | None:

        role = self._normalize_role(role)

        # Electronics domains first (more specific)

        for keyword in DIGITAL_DESIGN_KEYWORDS:
            if keyword in role:
                return "digital_design"

        for keyword in ANALOG_DESIGN_KEYWORDS:
            if keyword in role:
                return "analog_design"

        for keyword in EMBEDDED_SYSTEMS_KEYWORDS:
            if keyword in role:
                return "embedded_systems"

        for keyword in VLSI_KEYWORDS:
            if keyword in role:
                return "vlsi"

        # Product Management

        for keyword in PRODUCT_MANAGEMENT_KEYWORDS:
            if keyword in role:
                return "product_management"

        # Business domains

        for keyword in FINANCE_KEYWORDS:
            if keyword in role:
                return "finance"

        for keyword in CONSULTING_KEYWORDS:
            if keyword in role:
                return "consulting"

        for keyword in SALES_KEYWORDS:
            if keyword in role:
                return "sales"

        for keyword in MARKETING_KEYWORDS:
            if keyword in role:
                return "marketing"

        # Software last (contains broader terms)

        for keyword in SOFTWARE_KEYWORDS:
            if keyword in role:
                return "software"

        return None

    def _gemini_classification(self, role: str) -> str:

        prompt = f"""
Classify the following interview role into exactly ONE category.

Categories:

Software
Finance
Consulting
Sales
Marketing
Digital_Design
Analog_Design
Embedded_Systems
VLSI
Product_Management

Interview Role:
{role}

Rules:
- Return ONLY one category.
- Use exactly one of the category names above.
- Do not explain.
- Do not include punctuation.
"""

        response = self.key_manager.generate_content(prompt)

        category = response.text.strip().lower()

        valid_categories = {
            "software",
            "finance",
            "consulting",
            "sales",
            "marketing",
            "digital_design",
            "analog_design",
            "embedded_systems",
            "vlsi",
            "product_management",
        }

        if category not in valid_categories:
            return "software"

        return category

    def classify_role(self, role: str) -> str:
        """
        Classify a role into one of the supported interview categories.
        """

        category = self._exact_match(role)

        if category:
            return category

        category = self._keyword_match(role)

        if category:
            return category

        return self._gemini_classification(role)


# ============================================================
# Software sub-role classification.
#
# Second-level classifier, used only inside the `software` domain's
# prompt builder (build_software_prompt), to decide which "Core CS
# Fundamentals" and "System Design" topics are actually relevant to
# the specific role - e.g. an ML Engineer shouldn't be asked about
# OS/DBMS, and a Frontend Developer shouldn't be asked about database
# sharding. Independent of classify_role() above: classify_role still
# returns "software" for all of these roles, this function only picks
# which topic set within the software prompt to use.
#
# Deliberately keyword-only, no Gemini fallback - "generic" (today's
# original OS/DBMS/OOP behavior) is a legitimate, confirmed-correct
# default for backend/full-stack/SDE/unmatched roles, not an error
# case that needs an LLM to resolve.
# ============================================================

ML_DATA_SCIENCE_KEYWORDS = {
    "machine learning",
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    "data science",
    "ai engineer",
    "artificial intelligence engineer",
    "deep learning",
    "deep learning engineer",
    "nlp engineer",
    "natural language processing",
    "computer vision",
    "computer vision engineer",
    "mlops",
    "mlops engineer",
}

DATA_ENGINEERING_KEYWORDS = {
    "data engineer",
    "data engineering",
    "etl developer",
    "etl engineer",
    "big data engineer",
    "big data developer",
    "analytics engineer",
    "data pipeline engineer",
    "data platform engineer",
}

FRONTEND_SUBROLE_KEYWORDS = {
    "frontend developer",
    "frontend engineer",
    "front-end developer",
    "front-end engineer",
    "front end developer",
    "ui developer",
    "ui engineer",
    "react developer",
    "angular developer",
    "vue developer",
}

MOBILE_SUBROLE_KEYWORDS = {
    "android developer",
    "ios developer",
    "mobile developer",
    "mobile app developer",
    "mobile engineer",
    "flutter developer",
    "react native developer",
    "swift developer",
    "kotlin developer",
}

DEVOPS_SRE_KEYWORDS = {
    "devops engineer",
    "devops",
    "site reliability engineer",
    "sre",
    "cloud engineer",
    "platform engineer",
    "infrastructure engineer",
    "kubernetes engineer",
    "cloud infrastructure engineer",
}

QA_TESTING_KEYWORDS = {
    "qa engineer",
    "quality assurance engineer",
    "test engineer",
    "sdet",
    "software test engineer",
    "automation test engineer",
    "qa automation engineer",
}


def classify_software_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "software" domain into
    a finer-grained sub-role bucket, used to pick relevant Fundamentals
    and System Design topics. Returns "generic" (today's original
    OS/DBMS/OOP behavior) if nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in ML_DATA_SCIENCE_KEYWORDS:
        if keyword in normalized:
            return "ml_data_science"

    for keyword in DATA_ENGINEERING_KEYWORDS:
        if keyword in normalized:
            return "data_engineering"

    for keyword in FRONTEND_SUBROLE_KEYWORDS:
        if keyword in normalized:
            return "frontend"

    for keyword in MOBILE_SUBROLE_KEYWORDS:
        if keyword in normalized:
            return "mobile"

    for keyword in DEVOPS_SRE_KEYWORDS:
        if keyword in normalized:
            return "devops_sre"

    for keyword in QA_TESTING_KEYWORDS:
        if keyword in normalized:
            return "qa_testing"

    return "generic"


# ============================================================
# Finance sub-role classification (used only inside
# build_finance_prompt, to pick relevant Finance Fundamentals
# topics per specific finance role).
# ============================================================

INVESTMENT_BANKING_PE_KEYWORDS = {
    "investment banking",
    "investment banker",
    "m&a",
    "mergers and acquisitions",
    "private equity",
    "ib analyst",
    "ib associate",
}

EQUITY_RESEARCH_KEYWORDS = {
    "equity research",
    "asset management",
    "portfolio management",
    "portfolio manager",
    "buy side analyst",
    "sell side analyst",
}

CORPORATE_FINANCE_TREASURY_KEYWORDS = {
    "corporate finance",
    "treasury",
    "fp&a",
    "financial planning and analysis",
    "treasury analyst",
    "treasury manager",
}

FINANCE_RISK_MANAGEMENT_KEYWORDS = {
    "risk management",
    "risk analyst",
    "market risk",
    "credit risk",
    "risk manager",
}

VENTURE_CAPITAL_KEYWORDS = {
    "venture capital",
    "vc analyst",
    "vc associate",
    "startup investing",
}


def classify_finance_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "finance" domain into
    a finer-grained sub-role bucket, used to pick relevant Finance
    Fundamentals topics. Returns "generic" if nothing more specific
    matches.
    """

    normalized = role.strip().lower()

    for keyword in INVESTMENT_BANKING_PE_KEYWORDS:
        if keyword in normalized:
            return "investment_banking_pe"

    for keyword in EQUITY_RESEARCH_KEYWORDS:
        if keyword in normalized:
            return "equity_research"

    for keyword in CORPORATE_FINANCE_TREASURY_KEYWORDS:
        if keyword in normalized:
            return "corporate_finance_treasury"

    for keyword in FINANCE_RISK_MANAGEMENT_KEYWORDS:
        if keyword in normalized:
            return "risk_management"

    for keyword in VENTURE_CAPITAL_KEYWORDS:
        if keyword in normalized:
            return "venture_capital"

    return "generic"


# ============================================================
# Consulting sub-role classification (used only inside
# build_consulting_prompt).
# ============================================================

OPERATIONS_CONSULTING_KEYWORDS = {
    "operations consulting",
    "operations consultant",
    "supply chain consulting",
}

DIGITAL_CONSULTING_KEYWORDS = {
    "digital consulting",
    "digital consultant",
    "technology consulting",
    "it consulting",
}


def classify_consulting_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "consulting" domain
    into a finer-grained sub-role bucket. Returns "generic" if
    nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in OPERATIONS_CONSULTING_KEYWORDS:
        if keyword in normalized:
            return "operations_consulting"

    for keyword in DIGITAL_CONSULTING_KEYWORDS:
        if keyword in normalized:
            return "digital_consulting"

    return "generic"


# ============================================================
# Sales sub-role classification (used only inside
# build_sales_prompt).
# ============================================================

CUSTOMER_SUCCESS_KEYWORDS = {
    "customer success",
    "account manager",
    "relationship manager",
    "client success",
}


def classify_sales_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "sales" domain into a
    finer-grained sub-role bucket. Returns "generic" if nothing more
    specific matches.
    """

    normalized = role.strip().lower()

    for keyword in CUSTOMER_SUCCESS_KEYWORDS:
        if keyword in normalized:
            return "customer_success"

    return "generic"


# ============================================================
# Marketing sub-role classification (used only inside
# build_marketing_prompt).
# ============================================================

BRAND_MANAGEMENT_KEYWORDS = {
    "brand management",
    "brand manager",
    "brand marketing",
}

MARKETING_SEO_KEYWORDS = {
    "seo specialist",
    "seo executive",
    "search engine optimization",
}

CONTENT_MARKETING_KEYWORDS = {
    "content marketing",
    "content marketer",
    "content strategist",
}

PRODUCT_MARKETING_KEYWORDS = {
    "product marketing",
    "product marketer",
}


def classify_marketing_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "marketing" domain
    into a finer-grained sub-role bucket. Returns "generic" if
    nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in BRAND_MANAGEMENT_KEYWORDS:
        if keyword in normalized:
            return "brand_management"

    for keyword in MARKETING_SEO_KEYWORDS:
        if keyword in normalized:
            return "seo"

    for keyword in CONTENT_MARKETING_KEYWORDS:
        if keyword in normalized:
            return "content_marketing"

    for keyword in PRODUCT_MARKETING_KEYWORDS:
        if keyword in normalized:
            return "product_marketing"

    return "generic"


# ============================================================
# VLSI sub-role classification (used only inside
# build_vlsi_prompt).
# ============================================================

VLSI_PHYSICAL_DESIGN_KEYWORDS = {
    "physical design",
    "pd engineer",
    "backend physical design",
    "backend vlsi",
    "physical implementation",
    "floorplanning",
}

VLSI_DFT_KEYWORDS = {
    "dft",
    "dft engineer",
    "design for test",
    "scan",
    "atpg",
}

VLSI_STA_TIMING_KEYWORDS = {
    "sta",
    "static timing",
    "timing engineer",
    "timing closure",
}


def classify_vlsi_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "vlsi" domain into a
    finer-grained sub-role bucket. Returns "generic" if nothing more
    specific matches.
    """

    normalized = role.strip().lower()

    for keyword in VLSI_PHYSICAL_DESIGN_KEYWORDS:
        if keyword in normalized:
            return "physical_design"

    for keyword in VLSI_DFT_KEYWORDS:
        if keyword in normalized:
            return "dft"

    for keyword in VLSI_STA_TIMING_KEYWORDS:
        if keyword in normalized:
            return "sta_timing"

    return "generic"


# ============================================================
# Digital Design sub-role classification (used only inside
# build_digital_design_prompt).
# ============================================================

FPGA_KEYWORDS = {
    "fpga",
    "fpga engineer",
    "fpga design engineer",
}

VERIFICATION_DV_KEYWORDS = {
    "verification engineer",
    "design verification",
    "dv engineer",
    "verification",
    "functional verification engineer",
}


def classify_digital_design_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "digital_design"
    domain into a finer-grained sub-role bucket. Returns "generic"
    if nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in FPGA_KEYWORDS:
        if keyword in normalized:
            return "fpga"

    for keyword in VERIFICATION_DV_KEYWORDS:
        if keyword in normalized:
            return "verification_dv"

    return "generic"


# ============================================================
# Embedded Systems sub-role classification (used only inside
# build_embedded_systems_prompt).
# ============================================================

EMBEDDED_LINUX_KEYWORDS = {
    "embedded linux",
    "embedded linux engineer",
    "linux kernel",
    "kernel developer",
}

IOT_SUBROLE_KEYWORDS = {
    "iot",
    "iot engineer",
}

AUTOMOTIVE_EMBEDDED_KEYWORDS = {
    "automotive embedded",
    "automotive embedded engineer",
    "autosar",
}


def classify_embedded_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "embedded_systems"
    domain into a finer-grained sub-role bucket. Returns "generic"
    if nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in EMBEDDED_LINUX_KEYWORDS:
        if keyword in normalized:
            return "embedded_linux"

    for keyword in IOT_SUBROLE_KEYWORDS:
        if keyword in normalized:
            return "iot"

    for keyword in AUTOMOTIVE_EMBEDDED_KEYWORDS:
        if keyword in normalized:
            return "automotive_embedded"

    return "generic"


# ============================================================
# Analog Design sub-role classification (used only inside
# build_analog_design_prompt).
# ============================================================

MIXED_SIGNAL_KEYWORDS = {
    "mixed signal",
    "mixed signal engineer",
    "mixed signal design",
}


def classify_analog_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "analog_design"
    domain into a finer-grained sub-role bucket. Returns "generic"
    if nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in MIXED_SIGNAL_KEYWORDS:
        if keyword in normalized:
            return "mixed_signal"

    return "generic"


# ============================================================
# Product Management sub-role classification (used only inside
# build_product_management_prompt).
# ============================================================

TECHNICAL_PM_KEYWORDS = {
    "technical product manager",
    "technical pm",
}

GROWTH_PM_KEYWORDS = {
    "growth product manager",
    "growth pm",
}

PRODUCT_ANALYST_KEYWORDS = {
    "product analyst",
}


def classify_product_management_subrole(role: str) -> str:
    """
    Classify a role already known to be in the "product_management"
    domain into a finer-grained sub-role bucket. Returns "generic"
    if nothing more specific matches.
    """

    normalized = role.strip().lower()

    for keyword in TECHNICAL_PM_KEYWORDS:
        if keyword in normalized:
            return "technical_pm"

    for keyword in GROWTH_PM_KEYWORDS:
        if keyword in normalized:
            return "growth_pm"

    for keyword in PRODUCT_ANALYST_KEYWORDS:
        if keyword in normalized:
            return "product_analyst"

    return "generic"