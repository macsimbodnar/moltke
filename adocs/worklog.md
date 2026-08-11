# Worklog

Prompts and recaps, appended by the UserPromptSubmit hook and by work turns.
Truncated 2026-08-11 (S106, DEC-042): everything earlier is in git history at
and before commit af7d91b. This file may be trimmed again whenever it grows
beyond usefulness; it is never read as context.

## 2026-08-11T recap (S106)

S106 complete. specs.md 84,637 to 8,413 bytes; decisions.md 70,505 to 23,258
keeping all 42 entries, ids stable, accepted-finding references intact
(--audit list exit 0); worklog truncated to a stub naming its history commit;
status.md Parked block rewritten to current truth. Always-read set measured:
180,518 bytes at e22a911 to 49,900 (~12.5k tokens). Suite 438 OK.
Files: adocs/specs.md, adocs/decisions.md, adocs/worklog.md, adocs/status.md,
adocs/testing.md (4 rows), adocs/plan_done/S106_compact_the_documents.md.

## 2026-08-11T recap (S107)

S107 complete. AGENTS.md §1 rewritten to the tiered reading protocol (zero doc
reads on routine turns, grep-first for decisions.md), precedence chain stated
(.moltke.local.md > Project rules > base), §2/§4/§7/§8/§9/§11 aligned with
S105/S106, decisions.md prohibition dropped from §11, subagent-freedom line
added. Spawning survey: no constraining sentence found; the two remaining
mentions enable audit spawns or are the stack metaphor. Template copied,
byte-identical, drift test green. Suite 438 OK.
Files: AGENTS.md, templates/AGENTS.md, adocs/testing.md (4 rows),
adocs/plan_done/S107_ruleset_reading_protocol.md.

## 2026-08-11T recap (S108)

S108 complete. Three-tier review model (DEC-044): fast check after every step
completion (small subagent, diff-scoped, no ceremony), audit proposals with
accept/postpone and Parked persistence, /moltke:audit on demand unchanged in
mechanics but closing by re-run or by recorded decision. AGENTS.md §10 rewritten,
template identical, both skills updated, MANUAL gained a Review model section.
No code change. Suite 438 OK.
Files: AGENTS.md, templates/AGENTS.md, skills/step/SKILL.md,
skills/audit/SKILL.md, MANUAL.md, adocs/decisions.md (DEC-044),
adocs/testing.md (4 rows), adocs/plan_done/S108_three_tier_review_model.md.
