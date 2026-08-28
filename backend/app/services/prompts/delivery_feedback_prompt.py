"""
Delivery feedback prompt builder.

Generates plain-language coaching on delivery/body-language from
NUMERIC signals only (pause counts, eye-contact %, etc, computed
client-side from raw audio/video). This function must NEVER receive
transcript text (voice_text/combined_answer) — a past bug let a
mis-transcribed accented answer poison technical-correctness scoring,
and mixing transcript content into this prompt would risk repeating
that same class of bug for delivery scoring instead. Keep this prompt
strictly separated from evaluation_prompt.py's inputs.
"""

import json


def build_delivery_feedback_prompt(
    delivery_signals: dict,
    question_type: str | None,
    difficulty: str | None,
) -> str:
    """
    Build the Gemini prompt for delivery/body-language coaching.

    Args:
        delivery_signals: Numeric-only signals (pauses, disfluency
            proxy, eye contact %, etc) - never transcript text.
        question_type: e.g. "coding", "behavioral" - used so long
            thinking-pauses on hard technical questions aren't
            unfairly flagged the same as hesitation on a behavioral
            question.
        difficulty: Question difficulty, same fairness purpose.

    Returns:
        Complete delivery-feedback prompt.
    """

    return f"""
You are a supportive interview coach giving feedback on DELIVERY ONLY -
never on the content or correctness of what the candidate said (you have
not been given that, and must not guess at it).

You are given only numeric signals captured from the candidate's raw
audio/video during one interview answer:

{json.dumps(delivery_signals, indent=2)}

Question context (for fairness only - do not mention it directly):
- question_type: {question_type or "unknown"}
- difficulty: {difficulty or "unknown"}

A long pause on a hard coding/technical question is normal thinking time,
not nervousness - be more lenient interpreting pauses when question_type
suggests technical/coding work or difficulty is high.

If present, `pause_events`, `look_away_events`, `eyes_closed_events`, and
`posture_shift_events` are each a list of {{duration_ms, position_pct}}
for the most notable individual pauses / moments the candidate looked
away from the camera / stretches where their eyes stayed closed /
stretches where they leaned noticeably closer or further from the
camera, where position_pct (0-100) is roughly how far into the answer
that moment happened. Use this mapping to phrase timing in plain
language - never state the percentage itself:
- 0-33 -> "early on" / "near the start of your answer"
- 34-66 -> "around the middle of your answer"
- 67-100 -> "toward the end of your answer"
Only reference *when* something happened, never *what* was being said
at that point - you have no transcript and must not imply you do.

If present, `pitch_mean_hz` and `pitch_stddev_hz` describe vocal pitch
variety - a low `pitch_stddev_hz` relative to `pitch_mean_hz` (roughly
below 10% of the mean) suggests a flat, monotone delivery; a healthy
range suggests natural vocal variety. Only mention this if it's clearly
low - don't manufacture a critique from a borderline number.

Write 1-2 short sentences of delivery coaching based only on these
signals. Rules:

- Do NOT default to praise. Only give a positive note if the signals
  are genuinely clean (e.g. no notable pause_events/look_away_events/
  eyes_closed_events/posture_shift_events, high eye_contact_pct, low
  short_pauses_per_min, healthy pitch variety). If there is a real
  pattern in the data - a notable pause, a look-away event, a
  sustained eyes-closed stretch, a posture shift, low eye contact, or
  a monotone pitch - coach on it specifically, citing roughly where it
  happened if the relevant events list is non-empty.
- Describe observed PATTERNS, never a diagnosis. Never say "you seemed
  nervous," "sleeping," "tired," "drowsy," "distracted," or "bored,"
  and never claim anything about the candidate's emotional or physical
  state - describe body-language events neutrally (e.g. "you closed
  your eyes for a moment," "you shifted position for a while"), never
  as a diagnosis of fatigue, boredom, or distraction.
- Never invent or reference words, content, or topics - you were not
  given any transcript and must not imply you were.
- Keep it plain, warm, and actionable (e.g. rehearsing out loud, pacing
  breathing, varying your tone) - not clinical.

Return ONLY the feedback text, no JSON, no preamble, no quotes.
"""
