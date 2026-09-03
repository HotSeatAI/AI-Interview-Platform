// Fixed display labels for already-known round keys (e.g. rendering
// history rows). The round *options* offered while generating an
// interview always come from the backend (GET /interview/rounds),
// not this map - see backend/app/services/prompts/software_rounds.py
// for the source of truth on round content per role.
export const ROUND_LABELS = {
  round_1: "Round 1",
  round_2: "Round 2",
  round_3: "Round 3: HR / Behavioral",
};
