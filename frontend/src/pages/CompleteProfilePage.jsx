import { useState } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../hooks/useAuth";
import { updateProfile, acceptTerms } from "../api/profileApi";
import BrandLogo from "../components/layout/BrandLogo";
import ThemeToggle from "../components/layout/ThemeToggle";
import TermsModal from "../components/profile/TermsModal";
import { COUNTRIES, CITIES_BY_COUNTRY, CITY_TO_COUNTRY } from "../constants/locationData";
import { JOB_DOMAINS } from "../constants/jobDomains";

const GENDER_OPTIONS = ["Male", "Female", "Prefer not to say"];
const OTHER_CITY = "__other__";

const currentYear = new Date().getFullYear();

function CompleteProfilePage() {
  const { user, token, refreshUser, logout } = useAuth();
  const navigate = useNavigate();

  const [showTerms, setShowTerms] = useState(
    Boolean(user?.profile_completed && !user?.terms_accepted)
  );
  const [termsSubmitting, setTermsSubmitting] = useState(false);
  const [termsError, setTermsError] = useState("");

  const [formData, setFormData] = useState({
    full_name: user?.username || "",
    gender: "",
    job_domains: [],
    years_of_experience: "",
    mobile_number: "",
    institute_name: "",
    year_of_passout: "",
    country: "",
    city: "",
    cityOther: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const availableJobDomains = JOB_DOMAINS.filter(
    (domain) => !formData.job_domains.includes(domain)
  );

  const addJobDomain = (domain) => {
    if (!domain) return;
    setFormData((prev) => {
      if (prev.job_domains.includes(domain)) return prev;
      return { ...prev, job_domains: [...prev.job_domains, domain] };
    });
  };

  const removeJobDomain = (domain) => {
    setFormData((prev) => ({
      ...prev,
      job_domains: prev.job_domains.filter((d) => d !== domain),
    }));
  };

  const handleChange = (field) => (e) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleCountryChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      country: e.target.value,
      city: "",
      cityOther: "",
    }));
  };

  const cityOptions = CITIES_BY_COUNTRY[formData.country] || [];
  const showCityDropdown = cityOptions.length > 0;
  const showOtherCityInput = !showCityDropdown || formData.city === OTHER_CITY;

  // No country picked yet, so City is free text - if what's typed matches
  // a known (unambiguous) city, fill in its country automatically.
  const handleCityTextChange = (e) => {
    const value = e.target.value;
    const match = CITY_TO_COUNTRY[value.trim().toLowerCase()];

    if (match) {
      setFormData((prev) => ({
        ...prev,
        country: match.country,
        city: match.city,
        cityOther: "",
      }));
      return;
    }

    setFormData((prev) => ({ ...prev, city: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.full_name.trim() || !formData.gender || formData.job_domains.length === 0 || formData.years_of_experience === "") {
      setError("Please fill in all required fields.");
      return;
    }

    const resolvedCity =
      formData.city === OTHER_CITY ? formData.cityOther.trim() : formData.city.trim();

    setSubmitting(true);
    try {
      const payload = {
        full_name: formData.full_name.trim(),
        gender: formData.gender,
        job_domains: formData.job_domains,
        years_of_experience: Number(formData.years_of_experience),
        mobile_number: formData.mobile_number.trim() || null,
        institute_name: formData.institute_name.trim() || null,
        year_of_passout: formData.year_of_passout ? Number(formData.year_of_passout) : null,
        country: formData.country.trim() || null,
        city: resolvedCity || null,
      };

      await updateProfile(payload, token);
      await refreshUser();
      setShowTerms(true);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to save your profile. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAcceptTerms = async () => {
    setTermsError("");
    setTermsSubmitting(true);
    try {
      await acceptTerms(token);
      await refreshUser();
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setTermsError(err?.response?.data?.detail || "Failed to save. Please try again.");
    } finally {
      setTermsSubmitting(false);
    }
  };

  const handleDeclineTerms = () => {
    logout();
    navigate("/login", { replace: true });
  };

  if (showTerms) {
    return (
      <div className="profile-setup-page">
        <header className="profile-setup-topbar">
          <BrandLogo />
          <ThemeToggle />
        </header>

        <TermsModal
          onAccept={handleAcceptTerms}
          onDecline={handleDeclineTerms}
          submitting={termsSubmitting}
          error={termsError}
        />
      </div>
    );
  }

  return (
    <div className="profile-setup-page">
      <header className="profile-setup-topbar">
        <BrandLogo />
        <ThemeToggle />
      </header>

      <main className="profile-setup-container">
        <div className="profile-setup-card">
          <div className="eyebrow">ONE LAST STEP</div>
          <h1 className="profile-setup-card__headline">Complete your profile</h1>
          <p className="profile-setup-card__sub">
            Tell us a bit about yourself before you get started. Fields marked
            with * are required.
          </p>

          <form className="profile-setup-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <span>Full Name *</span>
              <input
                type="text"
                value={formData.full_name}
                onChange={handleChange("full_name")}
                required
              />
            </div>

            <div className="form-field">
              <span>Email</span>
              <input type="email" value={user?.email || ""} disabled />
            </div>

            <div className="profile-setup-form__row">
              <div className="form-field">
                <span>Gender *</span>
                <select value={formData.gender} onChange={handleChange("gender")} required>
                  <option value="" disabled>
                    Select gender
                  </option>
                  {GENDER_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <span>Mobile Number</span>
                <input
                  type="tel"
                  value={formData.mobile_number}
                  onChange={handleChange("mobile_number")}
                  placeholder="Optional"
                />
              </div>
            </div>

            <div className="form-field">
              <span>Looking for Job Domain(s) *</span>
              <select
                value=""
                onChange={(e) => addJobDomain(e.target.value)}
                disabled={availableJobDomains.length === 0}
              >
                <option value="" disabled>
                  {availableJobDomains.length > 0
                    ? "Select a domain to add"
                    : "All domains added"}
                </option>
                {availableJobDomains.map((domain) => (
                  <option key={domain} value={domain}>
                    {domain}
                  </option>
                ))}
              </select>
              {formData.job_domains.length > 0 && (
                <div className="tag-list">
                  {formData.job_domains.map((domain) => (
                    <span key={domain} className="tag-chip">
                      {domain}
                      <button
                        type="button"
                        className="tag-chip__remove"
                        onClick={() => removeJobDomain(domain)}
                        aria-label={`Remove ${domain}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
              {formData.job_domains.length === 0 && (
                <span className="form-hint">Add at least one domain.</span>
              )}
            </div>

            <div className="form-field">
              <span>Years of Experience *</span>
              <input
                type="number"
                min="0"
                step="0.5"
                value={formData.years_of_experience}
                onChange={handleChange("years_of_experience")}
                required
              />
            </div>

            <div className="profile-setup-form__row">
              <div className="form-field">
                <span>Institute Name</span>
                <input
                  type="text"
                  value={formData.institute_name}
                  onChange={handleChange("institute_name")}
                  placeholder="Optional"
                />
              </div>

              <div className="form-field">
                <span>Year of Passout</span>
                <input
                  type="number"
                  min="1950"
                  max={currentYear + 10}
                  value={formData.year_of_passout}
                  onChange={handleChange("year_of_passout")}
                  placeholder="Optional"
                />
              </div>
            </div>

            <div className="profile-setup-form__row">
              <div className="form-field">
                <span>Country</span>
                <select value={formData.country} onChange={handleCountryChange}>
                  <option value="">Optional</option>
                  {COUNTRIES.map((country) => (
                    <option key={country} value={country}>
                      {country}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <span>City</span>
                {showCityDropdown && !showOtherCityInput ? (
                  <select value={formData.city} onChange={handleChange("city")}>
                    <option value="">Optional</option>
                    {cityOptions.map((city) => (
                      <option key={city} value={city}>
                        {city}
                      </option>
                    ))}
                    <option value={OTHER_CITY}>Other / not listed</option>
                  </select>
                ) : (
                  <input
                    type="text"
                    value={showCityDropdown ? formData.cityOther : formData.city}
                    onChange={
                      showCityDropdown
                        ? handleChange("cityOther")
                        : formData.country
                        ? handleChange("city")
                        : handleCityTextChange
                    }
                    placeholder={
                      formData.country ? "Enter your city" : "Type your city (or pick a country first)"
                    }
                  />
                )}
                {showCityDropdown && formData.city === OTHER_CITY && (
                  <button
                    type="button"
                    className="profile-setup-city-back"
                    onClick={() => setFormData((prev) => ({ ...prev, city: "", cityOther: "" }))}
                  >
                    Back to city list
                  </button>
                )}
              </div>
            </div>

            {error && <p className="error-text">{error}</p>}

            <button
              type="submit"
              className="button button--primary button--wide button--lg"
              disabled={submitting}
            >
              {submitting ? "Saving…" : "Save & Continue"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default CompleteProfilePage;
