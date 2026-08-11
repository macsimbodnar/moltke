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

## 2026-08-11T recap (S114)

S114 complete. Stale pauses (pauser in plan_done/) now report via INV-1 and clear
via --step unpause; parent re-blockable. S070 step-over and DEC-040 unchanged,
both pinned. Red observed. Suite 451 OK.
Files: bin/moltke.py (unresolvable_pauses stale kind, INV-1 message, unpause
message routing), tests/test_s003_invariants.py (2 tests), testing.md (3 rows),
README.md (449 to 451), plan_done/S114.

## 2026-08-11T recap (S115)

S115 complete. Unpause messages route by kind; self-pause says "paused itself".
Red observed. Suite 452 OK.
Files: bin/moltke.py (one branch), tests/test_s003_invariants.py (1 test),
testing.md (2 rows), README.md (451 to 452), plan_done/S115.

## 2026-08-11T recap (S116)

S116 complete. --help lists unpause and check; a test over format_help() pins
every operation. Red observed. Suite 453 OK.
Files: bin/moltke.py (two help strings), tests/test_s009_surface.py (1 test),
testing.md (1 row), README.md (452 to 453), plan_done/S116.

## 2026-08-11T recap (S117 + audit close-out)

S117 complete: decisions index rebuilt from the body (44 lines for 44 entries),
body reordered oldest-to-newest. Doc edit only. Suite 453 OK.

Audit close-out: all six 2026-08-11 findings fixed same-day, S112-S117. The seven
2026-08-09 findings closed on re-run evidence. Parked block updated: nothing open,
DEC-041's stop stands, S112-S117 await the next version bump.

## 2026-08-11T15:12+02:00 prompt

> What's next on the plan?

## 2026-08-11T15:17+02:00 prompt

> yes bump the version. Then please perform an analysis from a fresh context to check for any usability issues or in general about what is required from the plugin. If it even makes sense as it is architecture right now or if my requirements makes sense. Then report to me the analysis result

## 2026-08-11T recap (S118)

S118 complete. 0.10.0 bumped; S112-S117 ship with it. Suite 453 OK.

## 2026-08-11T recap (product review)

Fresh-context product review at 7ebebef, preserved verbatim in
adocs/audit/2026-08-11_product_review.md. Clean-context spawn, questions only, no
briefing. Verdict: right tool for its actual design point (solo author, long-lived
repo, Claude Code primary); not yet the general product README implies. It found
one live defect while measuring: --pre-write reads stdin before the PATH argument
and hangs on a never-EOF pipe. No fixes started; findings await Max's direction.

## 2026-08-11T15:51+02:00 prompt

> let's discuss in an iteractive way each one of your comments one by one

## 2026-08-11T15:58+02:00 prompt

> This tool should be definitly build with a team in mind and not a solo dev!

## 2026-08-11T16:01+02:00 prompt

> 1. It is most like each memeber will have his own branch to the possibility of multiple person on the same branch is low but not impossible in certain circumstances. 
> 2. I would say that the plan should be in common and everyon can pick an item from it

## 2026-08-11T16:01+02:00 prompt

> 1. It is most like each memeber will have his own branch to the possibility of multiple person on the same branch is low but not impossible in certain circumstances. 
> 2. I would say that the plan should be in common and everyon can pick an item from it
> 3. My decision would be to remove the worklog since it's a source of problems

## 2026-08-11T17:38+02:00 prompt

> which one will you reccomend? I am afraid that fences might be uneccesary blocker and we the user will just fight it to find a work around. What's your take on this?

## 2026-08-11T17:40+02:00 prompt

> agree

## 2026-08-11T17:43+02:00 prompt

> B

## 2026-08-11T17:44+02:00 prompt

> A

## 2026-08-11T17:45+02:00 prompt

> we can ignore windows for now. Just document that

## 2026-08-11T17:47+02:00 prompt

> B

## 2026-08-11T17:49+02:00 prompt

> Go, implement and verify all by yourself untill it's done or my input is required
