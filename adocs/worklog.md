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

## 2026-08-11T recap (S109)

S109 complete. .moltke.local.md: created by --session-start when absent, excluded
via .git/info/exclude, injected into session context, never overwritten,
idempotent, INV-11-silent in unmarked/declined repos, works without git.
6 tests, red observed. DEC-043 records the design. Suite 444 OK.
Files: bin/moltke.py (LOCAL_FILE, local_file_lines, mode_session_start),
templates/moltke_local.md (new), tests/test_s005_hooks.py (TestMachineLocalFile),
MANUAL.md, AGENTS.md §2 + templates/AGENTS.md, adocs/decisions.md (DEC-043),
adocs/testing.md (5 rows), README.md (438 to 444),
adocs/plan_done/S109_machine_local_file.md.

## 2026-08-11T recap (S110)

S110 complete, batch done. Project rules section in AGENTS.md + template
(byte-identical), MANUAL precedence paragraph, 0.9.0 bumped. Correction to the
stamp: the measured always-read set at completion is 53,704 bytes (~13.4k
tokens), not the ~51 KB the stamp estimated — AGENTS.md grew by the two new
sections and decisions.md by DEC-043/044. Against 180,518 at e22a911 that is a
70% cut, with per-step growth ~0 by construction. Suite 444 OK.
Files: AGENTS.md, templates/AGENTS.md, MANUAL.md, .claude-plugin/plugin.json,
adocs/testing.md (4 rows), adocs/plan_done/S110_project_rules_and_0_9_0.md.

## 2026-08-11T recap (S111)

S111 complete. First live tier-1 fast check (S108 model) ran over the batch's two
code commits and found five things: one behavioural edge — the exclude check was
a substring test, so `.moltke.local.md.bak` read as already-excluded — fixed
line-wise with a red-first test, and four stale INV-8 comment references, now
naming INV-7 alone. Suite 445 OK.
Files: bin/moltke.py, tests/test_s005_hooks.py, adocs/testing.md (2 rows),
README.md (444 to 445), adocs/plan_done/S111_fast_check_findings.md.

## 2026-08-11T13:24+02:00 prompt

> perform audit

## 2026-08-11T13:25+02:00 prompt

> perform audit and if anything comes out start fixing

## 2026-08-11T recap (audit triage)

Sixth adversarial audit at 5625acb: six findings (one medium, five low), report
adocs/audit/2026-08-11_adversarial.md, --audit check exit 0. All seven 2026-08-09
findings re-measured by the reviewer from their own reproductions; none
reproduces; closed on re-run evidence — the loop DEC-041 froze now closes
properly. Six steps S112-S117, one per finding, medium first. Reviewer mutation
testing: nine mutants, all killed.

## 2026-08-11T recap (S112)

S112 complete. Exclusion via `git rev-parse --git-path info/exclude` — in a
linked worktree the old --absolute-git-dir join pointed at
.git/worktrees/<name>/info/exclude, which git status never reads. Red observed
on a real linked-worktree fixture. Suite 446 OK.
Files: bin/moltke.py (local_file_lines), tests/test_s005_hooks.py, testing.md
(2 rows), README.md (445 to 446), plan_done/S112.

## 2026-08-11T recap (S113)

S113 complete. _canonical_case folds each existing path component to its on-disk
spelling via samefile before the pre-write rules read it. Red observed both ways:
ADOCS/PLAN_DONE bypassed the fence into the real plan_done/, Adocs/plan_todo got
a false refusal. Case-sensitive filesystems unchanged; tests skip with a message
there. Suite 449 OK.
Files: bin/moltke.py (_canonical_case, mode_pre_write), tests/test_s005_hooks.py
(TestCaseVariantPaths), testing.md (3 rows), README.md (446 to 449), plan_done/S113.
