import { useState } from "react";

import useAuth from "../hooks/useAuth";
import Navbar from "../components/layout/Navbar.jsx";
import {
  updateProfile,
  requestEmailChange,
  changePassword,
} from "../api/profileApi";
import { COUNTRIES, CITIES_BY_COUNTRY } from "../constants/locationData";
import { JOB_DOMAINS } from "../constants/jobDomains";

const GENDER_OPTIONS = ["Male", "Female", "Prefer not to say"];
const OTHER_CITY = "__other__";
const currentYear = new Date().getFullYear();

function SettingsPage() {
  const { user, token, refreshUser } = useAuth();
  const isLocalAccount = user?.auth_provider === "local";

  // ---- Profile section ----
  const initialCity =
    user?.country && !CITIES_BY_COUNTRY[user.country]?.includes(user.city)
      ? OTHER_CITY
      : user?.city || "";

  const [formData, setFormData] = useState({
    full_name: user?.full_name || "",
    gender: user?.gender || "",
    job_domains: user?.job_domains || [],
    years_of_experience:
      user?.years_of_experience != null ? String(user.years_of_experience) : "",
    mobile_number: user?.mobile_number || "",
    institute_name: user?.institute_name || "",
    year_of_passout: user?.year_of_passout || "",
    country: user?.country || "",
    city: initialCity,
    cityOther: initialCity === OTHER_CITY ? user?.city || "" : "",
  });
  const [profileError, setProfileError] = useState("");
  const [profileSuccess, setProfileSuccess] = useState("");
  const [profileSubmitting, setProfileSubmitting] = useState(false);

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

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setProfileError("");
    setProfileSuccess("");

    if (
      !formData.full_name.trim() ||
      !formData.gender ||
      formData.job_domains.length === 0 ||
      formData.years_of_experience === ""
    ) {
      setProfileError("Please fill in all required fields.");
      return;
    }

    const resolvedCity =
      formData.city === OTHER_CITY ? formData.cityOther.trim() : formData.city.trim();

    setProfileSubmitting(true);
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
      setProfileSuccess("Profile updated.");
    } catch (err) {
      setProfileError(
        err?.friendlyMessage || err?.response?.data?.detail || "Failed to save your profile."
      );
    } finally {
      setProfileSubmitting(false);
    }
  };

  // ---- Change email section ----
  const [emailForm, setEmailForm] = useState({ current_password: "", new_email: "" });
  const [emailError, setEmailError] = useState("");
  const [emailPending, setEmailPending] = useState(false);
  const [emailSubmitting, setEmailSubmitting] = useState(false);

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setEmailError("");

    if (!emailForm.current_password || !emailForm.new_email) {
      setEmailError("Please fill in both fields.");
      return;
    }

    setEmailSubmitting(true);
    try {
      await requestEmailChange(emailForm, token);
      setEmailPending(true);
    } catch (err) {
      setEmailError(
        err?.friendlyMessage || err?.response?.data?.detail || "Failed to request email change."
      );
    } finally {
      setEmailSubmitting(false);
    }
  };

  // ---- Change password section ----
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_new_password: "",
  });
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordSubmitting, setPasswordSubmitting] = useState(false);

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordError("");
    setPasswordSuccess("");

    if (!passwordForm.current_password || !passwordForm.new_password) {
      setPasswordError("Please fill in all fields.");
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setPasswordError("New password must be at least 8 characters.");
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_new_password) {
      setPasswordError("New passwords don't match.");
      return;
    }

    setPasswordSubmitting(true);
    try {
      await changePassword(
        {
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password,
        },
        token
      );
      setPasswordSuccess("Password changed.");
      setPasswordForm({ current_password: "", new_password: "", confirm_new_password: "" });
    } catch (err) {
      setPasswordError(
        err?.friendlyMessage || err?.response?.data?.detail || "Failed to change password."
      );
    } finally {
      setPasswordSubmitting(false);
    }
  };

  return (
    <div className="settings-page">
      <Navbar />

      <main className="settings-container">
        <div className="section-header">
          <div className="eyebrow">ACCOUNT</div>
          <h1>Settings</h1>
          <p>View and update your profile, email, and password.</p>
        </div>

        <section className="settings-section">
          <h2 className="settings-section__title">Profile</h2>

          <form className="settings-form" onSubmit={handleProfileSubmit}>
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
              <span className="form-hint">
                Use the "Change Email" section below to update this.
              </span>
            </div>

            <div className="settings-form__row">
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
              <span>Job Domain(s) *</span>
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

            <div className="settings-form__row">
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

            <div className="settings-form__row">
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
                      showCityDropdown ? handleChange("cityOther") : handleChange("city")
                    }
                    placeholder="Optional"
                  />
                )}
              </div>
            </div>

            {profileError && <p className="error-text">{profileError}</p>}
            {profileSuccess && <p className="form-hint">{profileSuccess}</p>}

            <button
              type="submit"
              className="button button--primary"
              disabled={profileSubmitting}
            >
              {profileSubmitting ? "Saving…" : "Save Profile"}
            </button>
          </form>
        </section>

        {isLocalAccount ? (
          <section className="settings-section">
            <h2 className="settings-section__title">Change Email</h2>

            {emailPending ? (
              <p className="form-hint">
                Check {emailForm.new_email} for a link to confirm the change. Your
                current email stays active until then.
              </p>
            ) : (
              <form className="settings-form" onSubmit={handleEmailSubmit}>
                <div className="form-field">
                  <span>Current Password *</span>
                  <input
                    type="password"
                    value={emailForm.current_password}
                    onChange={(e) =>
                      setEmailForm((prev) => ({ ...prev, current_password: e.target.value }))
                    }
                    required
                  />
                </div>

                <div className="form-field">
                  <span>New Email *</span>
                  <input
                    type="email"
                    value={emailForm.new_email}
                    onChange={(e) =>
                      setEmailForm((prev) => ({ ...prev, new_email: e.target.value }))
                    }
                    required
                  />
                </div>

                {emailError && <p className="error-text">{emailError}</p>}

                <button
                  type="submit"
                  className="button button--primary"
                  disabled={emailSubmitting}
                >
                  {emailSubmitting ? "Sending…" : "Request Email Change"}
                </button>
              </form>
            )}
          </section>
        ) : (
          <section className="settings-section">
            <h2 className="settings-section__title">Change Email</h2>
            <p className="form-hint">Your email is managed by your Google account.</p>
          </section>
        )}

        {isLocalAccount && (
          <section className="settings-section">
            <h2 className="settings-section__title">Change Password</h2>

            <form className="settings-form" onSubmit={handlePasswordSubmit}>
              <div className="form-field">
                <span>Current Password *</span>
                <input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) =>
                    setPasswordForm((prev) => ({ ...prev, current_password: e.target.value }))
                  }
                  required
                />
              </div>

              <div className="settings-form__row">
                <div className="form-field">
                  <span>New Password *</span>
                  <input
                    type="password"
                    value={passwordForm.new_password}
                    onChange={(e) =>
                      setPasswordForm((prev) => ({ ...prev, new_password: e.target.value }))
                    }
                    minLength={8}
                    required
                  />
                </div>

                <div className="form-field">
                  <span>Confirm New Password *</span>
                  <input
                    type="password"
                    value={passwordForm.confirm_new_password}
                    onChange={(e) =>
                      setPasswordForm((prev) => ({
                        ...prev,
                        confirm_new_password: e.target.value,
                      }))
                    }
                    minLength={8}
                    required
                  />
                </div>
              </div>

              {passwordError && <p className="error-text">{passwordError}</p>}
              {passwordSuccess && <p className="form-hint">{passwordSuccess}</p>}

              <button
                type="submit"
                className="button button--primary"
                disabled={passwordSubmitting}
              >
                {passwordSubmitting ? "Changing…" : "Change Password"}
              </button>
            </form>
          </section>
        )}
      </main>
    </div>
  );
}

export default SettingsPage;
