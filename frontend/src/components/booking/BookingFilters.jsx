import { INTERVIEW_DOMAINS } from "../../constants/interviewDomains";

const TIME_OF_DAY_OPTIONS = [
  { value: "any", label: "Any" },
  { value: "morning", label: "Morning" },
  { value: "afternoon", label: "Afternoon" },
  { value: "evening", label: "Evening" },
];

function BookingFilters({ filters, onChange }) {
  const selectedDomain = INTERVIEW_DOMAINS.find((domain) => domain.code === filters.domain);

  const handleDomainChange = (event) => {
    onChange({ ...filters, domain: event.target.value, subDomain: "" });
  };

  const handleFieldChange = (field) => (event) => {
    onChange({ ...filters, [field]: event.target.value });
  };

  const handleTimeOfDaySelect = (timeOfDay) => {
    onChange({ ...filters, timeOfDay });
  };

  return (
    <form className="booking-filters" onSubmit={(event) => event.preventDefault()}>
      <label className="form-field">
        <span>Domain</span>
        <select name="domain" value={filters.domain} onChange={handleDomainChange}>
          <option value="" disabled>
            Select a domain
          </option>
          {INTERVIEW_DOMAINS.map((domain) => (
            <option key={domain.code} value={domain.code}>
              {domain.label}
            </option>
          ))}
        </select>
      </label>

      <label className="form-field">
        <span>Sub-domain</span>
        <select
          name="subDomain"
          value={filters.subDomain}
          onChange={handleFieldChange("subDomain")}
          disabled={!selectedDomain}
        >
          <option value="">Any sub-domain</option>
          {selectedDomain?.subDomains.map((sub) => (
            <option key={sub.code} value={sub.code}>
              {sub.label}
            </option>
          ))}
        </select>
      </label>

      <label className="form-field">
        <span>Earliest date</span>
        <input
          type="date"
          name="fromDate"
          value={filters.fromDate}
          onChange={handleFieldChange("fromDate")}
        />
      </label>

      <label className="form-field">
        <span>Latest date</span>
        <input
          type="date"
          name="toDate"
          value={filters.toDate}
          min={filters.fromDate || undefined}
          onChange={handleFieldChange("toDate")}
        />
        <span className="form-hint">Optional - leave blank for no upper bound.</span>
      </label>

      <div className="form-field">
        <span>Time of day</span>
        <div className="segmented-control">
          {TIME_OF_DAY_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`segmented-control__option ${
                filters.timeOfDay === option.value ? "segmented-control__option--active" : ""
              }`}
              onClick={() => handleTimeOfDaySelect(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </form>
  );
}

export default BookingFilters;
