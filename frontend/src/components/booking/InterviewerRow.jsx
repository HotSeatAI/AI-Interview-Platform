import { useState } from "react";

import { getDomainLabel, getSubDomainLabel } from "../../constants/interviewDomains";
import { getInitials } from "../../utils/initials";
import { formatSlotLabel } from "../../utils/formatSlot";
import Button from "../ui/Button";

function InterviewerRow({ interviewer, onRequestBook }) {
  const [selectedSlotId, setSelectedSlotId] = useState("");

  const selectedSlot = interviewer.slots.find((slot) => slot.id === selectedSlotId);

  return (
    <article className="list-row list-row--booking">
      <div className="list-row__info">
        <div className="list-row__title">
          <span className="interviewer-avatar">{getInitials(interviewer.name)}</span>
          {interviewer.name}
        </div>
        <div className="list-row__meta">
          <span className="badge badge--info">{getDomainLabel(interviewer.domain)}</span>
          {interviewer.sub_domains.map((subDomain) => (
            <span key={subDomain} className="badge badge--neutral">
              {getSubDomainLabel(interviewer.domain, subDomain)}
            </span>
          ))}
          <span>{interviewer.experience_years} yrs experience</span>
          {interviewer.rating && <span>★ {interviewer.rating}</span>}
        </div>
        <p className="list-row__bio">{interviewer.bio}</p>
      </div>

      <div className="slot-chip-group">
        {interviewer.slots.map((slot) => (
          <button
            key={slot.id}
            type="button"
            className={`slot-chip ${selectedSlotId === slot.id ? "slot-chip--selected" : ""}`}
            onClick={() => setSelectedSlotId(slot.id)}
          >
            {formatSlotLabel(slot)}
          </button>
        ))}
      </div>

      <div className="list-row__actions">
        <Button
          variant="primary"
          size="sm"
          disabled={!selectedSlot}
          onClick={() => onRequestBook(interviewer, selectedSlot)}
        >
          Book slot
        </Button>
      </div>
    </article>
  );
}

export default InterviewerRow;
