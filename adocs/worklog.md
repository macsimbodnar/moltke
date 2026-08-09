# Worklog

Append only. Forensic history for humans, never a context source (DEC-011).
Mechanical prompt logging starts when hooks land (S005); until then entries are
appended by hand.

## 2026-08-01T14:54+02:00 prompt

> read bootstrap.md and AGENTS.md, then work S001 from section 8

## 2026-08-01 recap S001

- Step: S001 scaffold, worked by hand per specs (pre-tooling).
- Changed: `.workflow.json`, `CLAUDE.md`, `.gitignore`; `bootstrap.md` moved to `project/specs.md` and restructured (prime directive, INV-1..INV-12); `project/` tree per AGENTS.md §2; DEC-001..DEC-012 seeded newest first; plan.md ordering S001..S011 with one step file each; S001 completed into `plan_done/`.
- Tests: none yet (suite arrives S002). Manual invariant checks run and recorded in testing.md; first run caught missing `plan_done/`, fixed, re-run green.
- README/MANUAL: checked — both absent by plan (S011).
- Flagged: INV-8 append-only bytes vs decisions.md newest-first ordering conflict, routed to S004.
- Commits: 21a8226 (scaffold), 2fcbb94 (untrack stray `.claude/` temp file swept in by `git add -A`).

## 2026-08-01T15:20+02:00 prompts (hand-logged as a batch)

> What is the next step? All defered decisions or anything that i should decide now let's solce it in iteractive way now

> I will handle github configuration by myslef. You just create commits and nothing else. Untill new orders

> What would be most efficient way to handle decisions? Appending is faster but then you need to read the whole file and consume more tokens. if adding on top is something that will not require to read the whole file increasing the context the nlet's put on top, if not then on bottom

> bottom

## 2026-08-01 recap decisions ordering

- Not a step; rules and decisions turn.
- DEC-013: decisions.md newest last; AGENTS.md §2/§8 amended; DEC-001..DEC-012 reordered oldest first (one-time exception authorized by DEC-013); S004 reconcile clause dropped; superseding testing.md row appended.
- DEC-014: GitHub configuration is Max's own; agent commits only, until new orders.
- Commit: e8084d3

## 2026-08-01T15:45+02:00 prompt (hand-logged)

> ok, before proceeding i want to rename the project, repository and commands. The new name of the project is moltke (Moltke commanded armies he could not see by writing orders that survived his absence. Same problem, smaller scale.)

## 2026-08-01 recap moltke rename

- Not a step; naming decision turn. Scope question answered by Max: full rename.
- DEC-015: plugin/repo `moltke`, CLI `bin/moltke.py`, marker `.moltke.json`, skills init/step/audit under /moltke:.
- Renamed: `.workflow.json` → `.moltke.json`; step files S002/S006/S007 short names; specs, AGENTS.md, plan, status, plan_todo step files updated. Immutable history keeps old names, reads through DEC-015.
- Superseding testing.md row appended for the marker.
- GitHub repo rename and local directory rename left to Max (DEC-014).
- Commit: 00da550

## 2026-08-01T16:10+02:00 prompt (hand-logged)

> before proceeding i just want to evaluate if it even makes sense to create this project. For example i found this one https://github.com/SpillwaveSolutions/project-memory and there are many others. Maybe there is one out there that is actually a standard for this so i don't need to reinvent the wheel. Please search online for it and evaluate if i should proceed with the project or not

## 2026-08-01T16:35+02:00 prompt (hand-logged)

> ok i want to proceed. let's proceed

## 2026-08-01 recap S002

- Step: S002 moltke.py skeleton.
- Changed: bin/moltke.py (find_root, load_marker/check_marker, INV-11 gate, --validate with INVARIANT_CHECKS registry, hook-mode stubs for S005); tests/fixtures.py (broken-fixture builders); tests/test_s002_marker.py (12 tests).
- Red observed: stub version exiting 0 everywhere -> 9 of 12 failed ("AssertionError: 0 != 1", "'all checks pass' not found in ''"); the 3 passing were INV-11 gate tests whose non-vacuity partners were among the failures. Then implemented; 12/12 green. Dogfood: `python3 bin/moltke.py --validate` passes on this repo.
- Flagged: INV-11 vs --scaffold tension (scaffold must run unmarked); routed to S006 step file and status parked.
- README/MANUAL: checked, absent by plan (S011).
- Commit: 2a50f1d

## 2026-08-01 recap S003

- Step: S003 invariants 1-7.
- Changed: bin/moltke.py (step parsing, plan_steps, inv_1..inv_7 registered); tests/fixtures.py (step_file, workflow_repo); tests/test_s003_invariants.py (12 tests).
- Red observed: empty registry -> 9 failures ("AssertionError: 0 != 1"), then implemented, 24/24 green. Dogfood --validate passes on this repo.
- INV-7 interpretation recorded in specs (git HEAD baseline, additions legal, abstain without git). INV-3 strengthened: missing plan.md in an enabled repo is a violation; re-targeted test_valid_marker_passes from bare marker to plan tree (strengthening, not weakening).
- README/MANUAL: checked, absent by plan (S011).
- Commit: 70f7e2b

## 2026-08-01 recap S004

- Step: S004 invariants 8-10.
- Changed: bin/moltke.py (inv_8 byte-prefix vs git HEAD, inv_9 unique DEC ids, inv_10 finding statuses and open-finding references); tests/fixtures.py (decisions/worklog in workflow_repo, audit_report helper); tests/test_s004_invariants.py (9 tests).
- Red observed: 6 failures ("AssertionError: 0 != 1") before implementation; 33/33 green after. Dogfood --validate passes on this repo.
- INV-10 fixed the finding format ahead of S008 (### <report>-F<nn> + Status: line); noted in specs and the S008 step file.
- README/MANUAL: checked, absent by plan (S011).
- Commit: 21b27d0

## 2026-08-01 recap S005

- Step: S005 hooks wiring.
- Changed: bin/moltke.py (mode_session_start, mode_log_prompt, mode_pre_write, mode_post_write, mode_stop, derived_next/status_next, 3-block stop cap); hooks/hooks.json (five events, ${CLAUDE_PLUGIN_ROOT}); tests/test_s005_hooks.py (16 tests); fixtures gained status.md.
- Live-docs deviations recorded in specs: UserPromptSubmit exit 2 erases the prompt (log fails open); SessionStart context via hookSpecificOutput.additionalContext; no documented Stop cap (self-imposed cap of 3, state in .git/moltke_stop_state.json).
- Red observed: 8 failures + 2 errors before implementation; 49/49 green after. Dogfood --validate passes.
- README/MANUAL: checked, absent by plan (S011).
- Commit: 3f9b649

## 2026-08-01T17:30+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S006

- Step: S006 init skill and templates tree.
- Changed: bin/moltke.py (mode_scaffold, mode_decline, scaffold_root, declined, plan_text); skills/init/SKILL.md; templates/ (AGENTS.md copy, CLAUDE.md, cursor_rules, moltke.json, project/*.md, step_template.md, audit_report_template.md); tests/test_s006_scaffold.py (12 tests).
- Red observed: 6 failures + 3 errors before implementation; 61/61 green after.
- Defect found by end-to-end scaffold of a throwaway repo (not by unit tests): commented-out example step in the plan template produced a phantom next step S001, a false stale-status.md report, and a Stop block on the first turn of a fresh repo. Regression test written first (red: "'stale' unexpectedly found in ... derived next step: s001"), then plan_text() strips comments and fenced blocks in derived_next and INV-3.
- Trivial in-scope fix: AGENTS.md 8 carried a live DEC-013 cross-reference that would have shipped into other repos; reworded before copying to templates. Caught by the genericity test.
- DEC-017 (setup modes exempt from INV-11, --decline added to the surface) and DEC-018 (thin Cursor pointer; Cursor reads AGENTS.md natively) recorded.
- README/MANUAL: checked, absent by plan (S011).
- Commits: d93673c (decisions + ruleset fix), c52f044 (S006).

## 2026-08-01T18:15+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S007

- Step: S007 step skill and lifecycle operations.
- Changed: bin/moltke.py (field_value, locate_step, next_step_id, write_step, append_to_plan, set_field, step_new/start/block/done/status, mode_step); skills/step/SKILL.md; tests/test_s007_step.py (19 tests).
- Red observed: 16 failures + 1 error before implementation; 82/82 green after.
- Two latent defects found and fixed red-first: (1) unfilled `paused_by: <!-- ... -->` placeholder counted as a real pause, hiding a second active step from INV-1 (red: "0 != 1 : moltke: all checks pass"); (2) INV-4 treated a completed child's `blocks:` as live, which would block the parent forever. Both recorded in specs.
- Also fixed: `set_field` silently did nothing when a step file lacked the key; a refusal echoed a raw field value ("complete S004  # 2026-08-01 first"). One test re-targeted to exercise the blocks gate in isolation, with a new test added for the paused gate (both gates now covered, coverage strengthened not reduced).
- Dogfood: full lifecycle (new, start, block, refused parent completion, refused child completion without testing row, completion, status) verified on a throwaway repo; then S007 itself completed with `--step done` and status.md regenerated by `--step status`, Parked list preserved.
- Observation, not a defect: with a step in progress, status shows it as both "In progress" and "Next", which is exactly the AGENTS.md 1 derivation (first step in plan order not in plan_done).
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.

## 2026-08-01T19:00+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S008

- Step: S008 adversarial_reviewer subagent and audit skill.
- Changed: bin/moltke.py (strip_guidance, finding_references, report_findings, inv_10 id-prefix check, reviewer fence in mode_pre_write, audit_new/audit_list/mode_audit); agents/adversarial_reviewer.md; skills/audit/SKILL.md; templates/audit_report_template.md restructured so the format example is fenced; tests/test_s008_audit.py (12 tests) + 1 regression test in test_s006_scaffold.py.
- Red observed: 9 failures + 1 error before implementation; 95/95 green after.
- Live-docs check: subagent frontmatter supports tools/disallowedTools but no path restriction, so the "writes only to project/audit/" rule is enforced by the PreToolUse hook via agent_type. Recorded in specs.
- Defect found by dogfooding: scaffolded decisions.md template example DEC-001 collided with a user's first real DEC-001 (false INV-9 duplicate). Fourth instance of guidance-parsed-as-data; consolidated into strip_guidance used by every scanner, rule recorded in specs. Red observed first.
- Not done here: the reviewer cannot actually be spawned until the plugin is installed (S010); no audit report was created in this repo, because a report nobody ran would be fabricated evidence.
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.

## 2026-08-01T19:45+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S009

- Step: S009 golden surface test.
- Changed: bin/moltke.py (extracted build_parser so the surface is introspectable); tests/test_s009_surface.py (5 tests); tests/golden/cli_surface.txt.
- Red observed by tampering, twice: added flag `--purge` and added `--step abandon`; each failed both the golden and the documentation check, output recorded in testing.md; both reverted and suite green after.
- Tightened during the step: the documentation check originally matched a bare word anywhere in the file, so `--step new` was satisfied by the word "new" in prose. Now an operation counts only on a line that also names its mode.
- Known gap, recorded not hidden: the MANUAL half is skipped until MANUAL.md exists; the S011 step file carries the instruction to confirm it stops skipping and actually bites.
- DEC-012 identity: verified covered by test_s006_scaffold.py, not duplicated; a tripwire asserts the guard still exists.
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.

## 2026-08-01T20:15+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S010

- Step: S010 plugin manifest and marketplace entry.
- Changed: .claude-plugin/plugin.json, .claude-plugin/marketplace.json; tests/test_s010_plugin.py (11 tests); plan.md and the S010 step file narrowed; S012 created; S011 note added.
- Red observed: 7 failures before the manifests existed; 110/110 green after (1 skipped).
- Live tooling: `claude plugin validate --strict` failed first on a missing marketplace description, then passed. Validating a copy without marketplace.json exercised the plugin manifest, skills, agents, and hooks, and surfaced the root-CLAUDE.md warning.
- Plan amended, not deviated: DEC-019 narrows S010 to environment-free verification and creates S012 (Max-owned) for install, live hooks, and second machine. DEC-020 records that the repo root is also the plugin root.
- Not done, deliberately: no plugin installed locally; that changes Max's Claude configuration and is not "create commits" (DEC-014).
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.

## 2026-08-02T09:00+02:00 prompt (hand-logged)

> next

## 2026-08-02 recap S011

- Step: S011 README and MANUAL.
- Changed: README.md, MANUAL.md; specs dated note; testing rows.
- Facts verified before writing, not recalled: no env vars (grep), exit codes 0/1/2 from the constants, STOP_CAP 3 and .git/moltke_stop_state.json, Python 3.12, 110 tests, layout from ls.
- The dormant MANUAL surface check activated on file creation. Verified it bites by deleting two modes from MANUAL: failed with "Lists differ: ['--decline', '--audit list'] != []". Restored, green.
- Caught by that: README claimed "one test skipped by design", which stopped being true the moment MANUAL existed. Corrected in the same commit.
- Known issues recorded honestly in MANUAL: plugin ships this repo's project state (DEC-020); the README/MANUAL gate is mechanical and cannot tell whether anyone looked; the reviewer fence depends on the agent_type field and fails open if it is absent; INV-7/INV-8 abstain without a git baseline; the hook layer has never run in a live session (S012).
- Commit: see below.

## 2026-08-02T17:20+02:00 prompt

> /moltke:init

## 2026-08-02T17:24+02:00 prompt

> /moltke:step

## 2026-08-02T17:29+02:00 prompt

> i want to refactor. I don't like the name "project" that is used for the files. I want it to be called adocs that stays for agent documentation. adocs. Preapre a plan for the migration. Execuite the plan and then also rename the directory in this project aswell. No migration steps are needed because no one except this project is using the plugin anyway

## 2026-08-02 recap — S013 adocs rename

- Step: S013 (blocking child of S012, created with `--step block`; S012 unpaused on completion).
- Decision: DEC-021, `project/` → `adocs/`, no migration path.
- Changed: `bin/moltke.py` (single `DOCS` constant, every path and hook message); `project/` → `adocs/` (plain `mv`, `git mv` refused because S012 was already staged out of `plan_todo/`); `templates/project/` → `templates/adocs/`; AGENTS.md and templates/AGENTS.md (byte-identical, verified with `cmp`); skills/*, agents/adversarial_reviewer.md, templates/cursor_rules, README.md, MANUAL.md, adocs/specs.md (dated note), adocs/plan.md; plugin.json 0.1.0 → 0.2.0.
- Tests added: `tests/test_s013_adocs.py`, 2 tests. Red observed for both: scaffold guard `AssertionError: True is not false : scaffold created project/` after pointing SCAFFOLD_DIRS back at `project/`; doc guard `Lists differ: ['README.md:2: stale ref to project/status.md'] != []` after inserting a stale line. Suite 110 → 112, green.
- Re-targeted, not relaxed: the doc guard first failed on MANUAL's own known-issue entry describing the old name. Rule changed from "the string never appears" to "the string never appears outside an explicit `<!-- historical -->` block", with a vacuity assert requiring at least one marked mention. Red re-observed for both the leftover case and the missing-marker case.
- README checked: test count 110 → 112. MANUAL checked: two known issues added (no 0.1.0 migration; hooks run the installed copy, not the checkout), and the live-hook entry narrowed to what was actually observed rather than removed.
- Twice lost work to `git checkout --` on files with uncommitted changes: `bin/moltke.py` (whole refactor) and `MANUAL.md` (rename plus new entries). Both redone; the moltke.py redo was scripted so a missing target string fails loudly instead of silently skipping.
- S012 evidence gathered this turn, before the rename: install is moltke@moltke 0.1.0, sha 0b5c96b, from git@github.com:macsimbodnar/moltke.git; SessionStart, UserPromptSubmit, PreToolUse (both refusals) and PostToolUse observed firing live.

## 2026-08-06 recap — audit and triage

Note: this session's prompts are absent above. The installed plugin was still
0.1.0, whose `--log-prompt` targets `project/`, so every prompt was discarded
silently. That is audit finding F14, reproduced and planned as S014.

- Ran an adversarial audit of the implementation against its documentation.
  Report: `adocs/audit/2026-08-06_adversarial.md`, 14 findings, 5 high, 6 medium,
  3 low. Written before any fix; no code was changed during the run.
- High findings, all reproduced: F14 prompt logging fails silently and is losing
  data in this repository today; F01 the Stop hook's recap gate cannot fire in a
  live session because `--log-prompt` already grew the worklog before the turn
  started; F02 the reviewer fence does bare-name `agent_type` equality while
  plugin components are namespaced, and it fails open; F03 the reviewer holds
  `Bash` against a `Write|Edit` matcher, so the fence is bypassable by design;
  F04 INV-7 and INV-8 baseline against HEAD, so committed tampering is invisible.
- Two suspicions killed by the live docs rather than assumed: `prompt_id` does
  exist in the Stop payload, so the no-deadlock cap keys correctly; PostToolUse
  exit 2 is documented non-blocking, so `--post-write` is correct as written.
- Triaged all 14 into one step each, S014..S026, closed out by S027. Order puts
  correctness defects first (AGENTS.md section 3): S014 before S015 because
  fixing prompt logging changes what the recap check reads; S016 before S017
  because the fence must match before widening it means anything; S023 late so
  it guards the surface after S017 and S021 add to it.
- Decisions recorded before the code lands: DEC-022 reviewer fence gives way to
  post-hoc reconciliation via a new `--audit check`, DEC-023 optional
  `test_command` gate on `--step done`, DEC-024 worklog secrets detected in the
  suite rather than redacted at write time.
- Files touched: `adocs/audit/2026-08-06_adversarial.md` (new), `decisions.md`
  (+DEC-022..024, byte-prefix verified intact), `plan.md` (+14), 14 new step
  files in `plan_todo/`, `status.md`.
- Tests added: none. This was an audit and a planning session; every fix carries
  its own red-first test in its own step.
- Verified: `--validate` green (the 14 INV-10 violations discharged by the
  `closes:` fields), suite 112 tests OK.
- Commit: f443ebe.
- Still open: S012's completion stamp needs to state what the two-machine
  install actually exercised, which is Max's to supply (DEC-014, DEC-019).

## 2026-08-06T12:38+02:00 prompt

> ❯ I have just installed Moltke on this machine. The files where here from the push but i did not have moltke installed in this machine. Now it is. So you can run checks and got your stamp.

## 2026-08-06T12:41+02:00 prompt

> I did not understand what i have to do here? Remaining for the stamp: reviewer fence under a real spawn. Still need your go-ahead — you didn't answer, the hook feedback interrupted. Spawn moltke:adversarial_reviewer on a throwaway task, have it attempt one write outside adocs/audit/, read the real agent_type? That closes F02 or proves it. Without it, F02 stays planned and the stamp says the fence clause is unverified.
> Let's answer one by one

## 2026-08-06T12:42+02:00 prompt

> yes, and i want to change this rule. I think it's fine to spawn subagents

## 2026-08-06 recap — S012 install verification

- Moltke installed on this machine, so S012's clauses could be exercised against
  the `adocs/` build instead of the stale 0.1.0 cache.
- All five hook events probed individually and observed firing: SessionStart
  printed the stack and `Derived next step: S012`; UserPromptSubmit appended the
  prompt verbatim; PreToolUse refused a write into `plan_done/` and a step file
  at the repo root; PostToolUse surfaced `INV-3` on an unlisted step file without
  blocking the write; Stop refused a deliberately staled `status.md`.
- Reviewer fence FAILED. A real plugin spawn of `moltke:adversarial_reviewer` was
  told to attempt one write to `PROBE_S012.md` in the repo root. It reported
  `File created successfully` with no hook denial; the file existed (6 bytes) and
  was removed by the main thread. The path matches no step-file pattern and is
  not under `plan_done/`, so the fence was the only rule that could have blocked
  it. Audit finding F02 goes from probable to proven.
- Still unobserved: the exact `agent_type` string. The probe proves the equality
  at `bin/moltke.py:408` is false; it does not distinguish a namespaced value
  from an absent field. S016's acceptance now requires logging the observed value
  before choosing the match, and re-probing with a live spawn.
- S012 completed rather than held open: its job was to verify, and it produced a
  definitive result for every clause. The stamp names the failed clause and its
  step (DEC-019 — a stamp that overstates poisons every later reading).
- Files touched: `MANUAL.md` (two fence entries narrowed to the confirmed defect
  and the deliberate Bash gap; live-hook entry narrowed to F01 and F14),
  `adocs/audit/2026-08-06_adversarial.md` (post-report verification section, no
  finding altered), `adocs/plan_todo/S016_fence_agent_type.md` (live re-probe
  added to accepts), `adocs/testing.md` (+5 rows, one of them a fail),
  `adocs/status.md`, `plan_current/S012` moved to `plan_done/`.
- Tests added: none. These are live-session observations no suite can make.
- Verified: `--validate` green, suite 112 tests OK.
- Commit: 5ae769c.
- Next: S014, prompt logging never fails silently.

## 2026-08-06T15:04+02:00 prompt

> Scan the project and list what is the next item in the plan if any

## 2026-08-06T15:08+02:00 prompt

> Read the repo goals and the repo plan, verify the implementation plan and rearange it if necessary or if better plan can be generated. Add to the plan :
> 
> * Planning fase during initialization.
> * How to handle plugin initialization if it was initialized on a different machine already?

## 2026-08-06 recap — plan review, S028 and S029 added

- Planning turn: verified S014..S027 order and added two steps at the tail.
- Order held under review: S016 (fence match) precedes S017 (fence gives way
  to reconciliation); S020 (same-day suffix) precedes S027 which uses it;
  S021 (test_command marker key) precedes S023 (surface guard covers marker
  keys); S025/S026 doc passes precede the S027 bump. No rearrangement.
- S028: init drives a guided planning phase after scaffolding, with a
  --session-start nudge while specs.md prime directive or plan.md steps are
  empty. Gap: today's post-scaffold sequence is five unguided lines and a
  skipped planning phase is invisible.
- S029: init verifies instead of re-scaffolding when the marker is already
  enabled — fresh clone of a repo initialized on another machine gets
  --validate, the derived next step, and template drift reported; refresh
  only on an explicit yes. Gap: today's enabled branch only runs --validate.
- Both queued behind S014..S027: audit correctness fixes outrank features.
- Files: adocs/plan.md, adocs/plan_todo/S028_init_planning_phase.md,
  adocs/plan_todo/S029_init_preinitialized_repo.md, adocs/status.md.
- Tests added: none, planning only. Suite 112 OK, --validate green.
- Commit: 21a3581.
- Next: S014, prompt logging never fails silently.

## 2026-08-06T15:15+02:00 prompt

> next step

## 2026-08-06 recap — S014 prompt logging never fails silently

- S014 done, closing audit finding F14 (which stays `planned` until S027 re-runs
  the audit; fixing without re-running does not close a finding).
- `mode_log_prompt` now creates `adocs/` before appending. `open(..., "a")` does
  not create parents, so a marked repository without the docs tree discarded
  every prompt at exit 0.
- A failed append writes `.git/moltke_log_failure.json` (`since`, `count`,
  `error`); `--session-start` reports it once in `additionalContext` and deletes
  it. Reporting once keeps it self-healing: a persisting failure rewrites the
  breadcrumb on the next prompt, a fixed one goes quiet with nothing to clear
  by hand. Nothing is written outside `.git/`, because an untracked file at the
  repo root reads as a source change to `--stop`. No `.git` means stderr only.
- Lost prompts are not recovered. Max chose no spill: the breadcrumb records
  that logging failed, not what was said. Recovery would have put prompt text in
  a second unpruned location that DEC-024's secret check does not scan.
- Red observed before the fix, all three new assertions:
  `AssertionError: False is not true : prompt lost: .../adocs/worklog.md was never created`
  and twice `AssertionError: 'not appended' not found in 'moltke stack ...'`.
  The failure is forced by making `adocs/worklog.md` a directory, which raises
  `IsADirectoryError` at any privilege level, unlike `chmod 0` under root.
- The report test asserts the append really failed before asserting the report,
  so it cannot pass for the wrong reason (AGENTS.md §6).
- Files: `bin/moltke.py`, `tests/test_s005_hooks.py`, `adocs/specs.md` (dated
  note), `adocs/testing.md` (+4 rows), `MANUAL.md`, `README.md` (112 to 116
  tests), `adocs/status.md`, `plan_current/S014` moved to `plan_done/`.
- Tests added: 4, three of them observed red. Suite 116 OK, `--validate` green.
- Open, raised by Max this turn and not yet decided: drop the append-only
  immutability requirement on `worklog.md` (INV-8). Scope not settled — whether
  `decisions.md` keeps it — so no code, spec, or AGENTS.md change was made.
  Affects INV-8, AGENTS.md §2/§9/§11, `templates/AGENTS.md`, and S018's scope.

## 2026-08-06 recap — DEC-025 and S030, worklog leaves INV-8

- Planning turn following S014. Max decided the append-only immutability rule
  covers `decisions.md` only; `adocs/worklog.md` becomes convention.
- DEC-025 recorded with the rejected option: dropping INV-8 entirely. Rejected
  because `DEC-<nnn>` ids are cited from code comments, commit messages,
  `specs.md`, and step files, so a rewritten entry silently changes what those
  citations mean.
- S030 created for the change itself: `APPEND_ONLY_FILES`, INV-8's wording,
  AGENTS.md sections 2/9/11, `templates/AGENTS.md` identically, and the S004
  tests re-targeted rather than deleted — the worklog case now asserts the check
  abstains, after first establishing that the same tampering against
  `decisions.md` still violates, so it cannot pass on a broken checker.
- S030 placed at position 18 in `plan.md`, ahead of S018, so S018 does not build
  a committed-baseline check for a requirement about to be dropped. S018's
  accepts and excludes amended to drop `worklog.md` and to name DEC-025.
- DEC-024 is not void: detection in the suite still beats redaction at write
  time. Its escape procedure gets simpler — cleaning a leaked secret from the
  worklog no longer needs a decisions.md entry authorising it. S022 stays
  wanted. S015 is unaffected; its recap gate keys on a recap heading after the
  last logged prompt, not on immutability.
- No code, spec, or AGENTS.md change made this turn. The decision is recorded
  ahead of the change, which section 8 allows; S030 applies it.
- Files: `adocs/decisions.md` (DEC-025), `adocs/plan.md` (reordered),
  `adocs/plan_todo/S030_drop_worklog_immutability.md`,
  `adocs/plan_todo/S018_immutable_baseline.md`, `adocs/status.md`.
- Tests added: none, planning only. Suite 116 OK, `--validate` green.
- Next: S015, Stop's recap gate fires in a live session.

## 2026-08-06T15:48+02:00 prompt

> next

## 2026-08-06 recap — S015 Stop's recap gate fires in a live session

- S015 done, closing audit finding F01 (stays `planned` until S027 re-runs the
  audit).
- `mode_stop` no longer compares worklog size against `git show HEAD:`. New
  `recap_pending` walks `## ` headings in order: a heading containing `recap`
  sets the flag, a heading ending in `prompt` clears it, so the answer is "does
  a recap follow the last logged prompt". Read through `strip_guidance`, so a
  recap heading inside a fenced block is an example, not a recap.
- Recap wins when a heading reads as both. Found before it bit: this repo's own
  S014 recap heading is `## 2026-08-06 recap — S014 prompt logging never fails
  silently`, which the first ambiguous version classified as the last prompt.
  Red observed against that version:
  `AssertionError: 2 != 0 : moltke: source changed but adocs/worklog.md has no
  recap heading after the last logged prompt`.
- Regression caught by the existing suite: the old code abstained implicitly
  because `git show HEAD:` fails with no commit, so a fresh scaffold passed.
  `test_s006_scaffold.py` failed with `AssertionError: 2 != 0 : a freshly
  scaffolded repo must not block the first stop`. The abstain is now explicit and
  tested in both directions, matching INV-7 and INV-8's no-baseline abstain.
- Red observed on the main gate: `AssertionError: 0 != 2 : ` with empty stderr —
  the gate produced no message at all, which is exactly F01.
- Every `TestStop` fixture now calls `log_prompt` before stopping, so no Stop
  test states a precondition a live session never has.
- Behaviour worth knowing, recorded in MANUAL: a recap for an earlier turn does
  not discharge a later one. Committing the change satisfies the gate as well as
  a recap does, and the refusal message says so, keeping INV-12.
- Removes `--stop`'s last dependence on the worklog's git baseline, which
  DEC-025 and S030 are about to drop anyway.
- Files: `bin/moltke.py`, `tests/test_s005_hooks.py`, `adocs/specs.md` (dated
  note), `adocs/testing.md` (+6 rows), `MANUAL.md`, `README.md` (116 to 120
  tests), `adocs/status.md`, `plan_current/S015` moved to `plan_done/`.
- Tests added: 6, all observed red. Suite 120 OK, `--validate` green.
- Next: S016, reviewer fence matches the scoped agent_type.

## 2026-08-06T15:57+02:00 prompt

> next

## 2026-08-06 recap — S016 reviewer fence matches the scoped agent_type

- S016 done, closing audit finding F02 (stays `planned` until S027 re-runs the
  audit).
- The observation the step demanded first: `agent_type` is
  `'moltke:adversarial_reviewer'` for a plugin-spawned subagent, with `agent_id`
  present; `'general-purpose'` for a built-in subagent; and both keys are absent
  on the main thread. So F02 was namespacing, not an absent field, and a suffix
  match is sufficient.
- How it was observed, since hooks turned out not to be observable any other way:
  hook *registrations* do not reload mid-session — a PreToolUse dump hook added to
  `.claude/settings.local.json` never fired — but hook *commands* re-execute per
  call, so the installed 0.2.0 script itself was instrumented to dump its
  payload. Max chose this over restarting the session. Backed up first, restored
  byte-identical afterwards, md5 `c52956752a8b022715f7dfdf49ca52d9` before and
  after, instrumentation grep-verified gone. The local settings hook and all
  three probe files were removed.
- The first reviewer spawn, asked to write outside the fence, declined on its own
  instructions and said so: a self-refusal is not evidence about the hook,
  because a compliant subagent and a working fence look identical from outside.
  It was right. The payload was captured from an in-fence write instead, which
  needs no violation at all. Recorded in `testing.md` as not-evidence rather than
  as a pass.
- Fix: `(payload.get("agent_type") or "").split(":")[-1] == REVIEWER_AGENT`.
  Suffix rather than an exact pair, so installing the plugin under another name
  cannot silently reopen the fence. Cost, recorded in MANUAL and specs: another
  plugin's agent named `adversarial_reviewer` would also be fenced. Deliberate
  direction — a wrong block is loud, a wrong pass is F02.
- Red observed with the real value: `AssertionError: 0 != 2 :
  ('moltke:adversarial_reviewer', '')`, empty stderr, the fence emitting nothing.
- Files: `bin/moltke.py`, `tests/test_s008_audit.py`, `adocs/specs.md` (dated
  note), `adocs/testing.md` (+6 rows, one of them not-evidence), `MANUAL.md`,
  `README.md` (120 to 121 tests), `adocs/status.md`, `plan_current/S016` moved to
  `plan_done/`.
- Tests added: 3 new, 2 widened to cover both `agent_type` forms; red observed.
  Suite 121 OK, `--validate` green.
- Next: S017, `--audit check` reconciles what an audit changed.

## 2026-08-06T16:11+02:00 prompt

> next

## 2026-08-06 recap — S017 --audit check reconciles what an audit changed

- S017 done, closing audit finding F03 (stays `planned` until S027 re-runs the
  audit). Implements DEC-022: prevention gives way to detection.
- `--audit new` records `.git/moltke_audit_baseline.json` as
  `{path: [porcelain status, sha256]}`, captured *before* the report is written
  so the report is part of the run's footprint rather than invisible.
- `--audit check` splits the footprint: this run's report and new files under
  `tests/` are expected; a modified existing test, a source change, and a
  reverted pre-existing change are unexpected, exit 1, and are listed with
  instructions to `git diff` each before acting on any finding.
- Per-file sha256, not just porcelain status: a file edited before the audit and
  edited again during it keeps status ` M` throughout, so status alone cannot see
  it. Tested directly.
- Red observed during the build, and worth keeping: with plain
  `git status --porcelain` the check reported `adocs/audit/: ??` and exited 1 —
  git collapses a wholly untracked directory into one entry, hiding the report
  inside it. Fixed with `-uall`.
- Fence widened: reviewer may write under `adocs/audit/` and may create new files
  under `tests/`, because a red-first regression test is evidence while editing
  an existing test is a patch. `(root / rel).exists()` is the discriminator.
- Doc claims corrected rather than deleted: the S008 specs sentence saying the
  hook "is the only place the limit can be real" is marked superseded in place.
  `agents/adversarial_reviewer.md` and `skills/audit/SKILL.md` no longer say the
  fence is enforcement; both now say `Bash` is unconstrained and the run is
  reconciled afterwards. MANUAL gained the `--audit check` row plus a section on
  what the check cannot see (ignored paths), and its fence entry lists three
  residual limits. README gained the audit gate commands.
- The surface guard bit exactly as designed: `AssertionError: Lists differ:
  ['--audit check'] != []` until specs and MANUAL described the new operation.
  Golden refreshed afterwards, not before.
- Files: `bin/moltke.py`, `tests/test_s008_audit.py`, `tests/golden/cli_surface.txt`,
  `agents/adversarial_reviewer.md`, `skills/audit/SKILL.md`, `adocs/specs.md`,
  `adocs/testing.md` (+9 rows), `MANUAL.md`, `README.md`, `adocs/status.md`,
  `plan_current/S017` moved to `plan_done/`.
- Tests added: 11, red observed. Suite 132 OK, `--validate` green.
- Next: S030, INV-8 covers decisions.md only.

## 2026-08-06T16:24+02:00 prompt

> next

## 2026-08-06 recap — S030 INV-8 covers decisions.md only

- S030 done, applying DEC-025. No audit finding: this was Max's decision, taken
  during S014.
- `APPEND_ONLY_FILES` is now `(adocs/decisions.md,)`. Rewriting, trimming, or
  deleting `adocs/worklog.md` is no longer a violation. INV-7 and `plan_done/`
  untouched.
- The INV-8 refusal message now states why decisions.md is enforced: DEC ids are
  cited from code, commits, and specs, so a rewritten entry changes what those
  citations mean, and a reversal is a new entry marking the old one VOID.
- The S004 worklog test was re-targeted, not deleted, and asserts the
  decisions.md violation first so a green worklog result cannot come from a
  broken checker. Red observed: `AssertionError: 1 != 0 : VIOLATION: INV-8:
  adocs/worklog.md changed earlier bytes`.
- Caught by the existing suite: the first draft cited `(DEC-025)` in AGENTS.md
  prose, which ships as `templates/AGENTS.md` into repositories where that id
  means something else entirely. `AssertionError: Lists differ: ['DEC-025',
  'DEC-025'] != []`. The ruleset stays id-free by design; traceability lives in
  specs.md and decisions.md, which are per-project.
- AGENTS.md changed in three places — the file-map write mode, the append-only
  sentence in section 2, section 9's opening, and the section 11 prohibition —
  then copied to `templates/AGENTS.md` byte-identically.
- MANUAL: the daily-use line now says the worklog may be corrected and only
  decisions.md is enforced; INV-8's git-baseline entry names decisions.md.
  README checked, no change needed — it never claimed the worklog was immutable.
- Consequence for DEC-024, already recorded there: cleaning a leaked secret from
  the worklog no longer needs a decisions.md entry authorising it. S022's
  detection is still wanted.
- Files: `bin/moltke.py`, `tests/test_s004_invariants.py`, `AGENTS.md`,
  `templates/AGENTS.md`, `adocs/specs.md`, `adocs/testing.md` (+3 rows),
  `MANUAL.md`, `adocs/status.md`, `plan_current/S030` moved to `plan_done/`.
- Tests added: none; one re-targeted, three unchanged and now load-bearing as the
  precondition. Suite 132 OK, `--validate` green.
- Next: S018, plan_done and append-only immutability survives a commit.

## 2026-08-06T16:35+02:00 prompt

> next

## 2026-08-06 recap — S018 immutability survives a commit

- S018 done, closing findings F04 and F12 (both stay `planned` until S027 re-runs
  the audit).
- Root cause was not the comparison, it was the baseline: HEAD moves at every
  step completion, and AGENTS.md section 5 has the agent commit at every step
  completion. So the guarantee only ever held inside the uncommitted window,
  which this workflow deliberately keeps as short as possible.
- Both invariants now check two baselines. HEAD covers what is not committed yet;
  `git log` covers what is. INV-7 reads `--name-status` over `plan_done/` and
  treats any status other than `A` as a violation, naming the commit. INV-8 reads
  `--numstat` over `decisions.md` and treats any commit that removed lines as a
  violation.
- `--numstat` is line granularity, not bytes. That is sufficient: an in-place
  byte edit still reads as one line removed and one added.
- `--no-renames` on both, which is what keeps the S013 `project/` to `adocs/`
  rename legal — a move into the directory reads as the addition it is, a move
  out as the deletion it is. Verified against this repository's real history
  rather than assumed: all 18 `plan_done` entries report `A` and nothing else,
  and no commit has ever removed a line from `decisions.md`.
- Red observed on all four committed-tampering tests as
  `AssertionError: 0 != 1 : moltke: all checks pass` — the audit's own
  reproduction, and the exact shape of F04.
- Each committed-tampering test asserts the uncommitted violation first, so a
  green result cannot come from the check having stopped working.
- F12 closed in the same commit: INV-7's "byte-identical to its state at session
  start" is marked superseded in place. It promised a session-scoped guarantee
  the code never implemented.
- Two limits recorded in MANUAL rather than fixed: a file created and deleted
  inside one commit leaves nothing to detect, and `Bash` writes reach
  `plan_done/` without meeting the PreToolUse fence — the history check is what
  notices afterwards. Neither check reverts anything; the fix is a new commit
  restoring the content, never a rewrite, since rewriting history would remove
  the evidence along with the tampering.
- Files: `bin/moltke.py`, `tests/test_s003_invariants.py`,
  `tests/test_s004_invariants.py`, `adocs/specs.md`, `adocs/testing.md` (+7 rows),
  `MANUAL.md`, `README.md` (132 to 138 tests), `adocs/status.md`,
  `plan_current/S018` moved to `plan_done/`.
- Tests added: 6, red observed. Suite 138 OK, `--validate` green.
- Next: S019, fenced guidance never discharges a finding.

## 2026-08-06T17:09+02:00 prompt

> newxt

## 2026-08-06 recap — S019 fenced guidance never discharges a finding

- S019 done, closing audit finding F05 (stays `planned` until S027 re-runs the
  audit). Smallest fix of the session: one call to `strip_guidance`.
- `finding_references` was the only scanner reading `decisions.md` raw, while the
  `strip_guidance` docstring and the specs both state the rule universally. So a
  finding id inside a fenced example discharged a real open finding — and the
  scaffolded `templates/adocs/decisions.md` ships exactly such an example, which
  is what made this reachable rather than theoretical.
- Both new violation tests assert the baseline first, the way the audit
  reproduced it: unreferenced open finding is a violation, then adding only a
  fenced mention must still be a violation. Otherwise exit 1 could just mean the
  check is broken.
- Red observed: `AssertionError: 0 != 1 : moltke: all checks pass` for the fenced
  and comment cases, and for `--audit list`:
  `2026-08-01_adversarial-F01  open  (referenced in decisions.md)`.
- Checked the tightening does not orphan anything here: `--audit list` still
  attributes all 14 findings of the 2026-08-06 report to S014..S026 and exits 0,
  so none was relying on a fenced reference.
- specs gained a dated note saying the universal rule had one exception until
  now. This is the fifth appearance of the same defect, which the S008 note
  already counted four times.
- Files: `bin/moltke.py`, `tests/test_s008_audit.py`, `adocs/specs.md`,
  `adocs/testing.md` (+5 rows), `README.md` (138 to 142 tests),
  `adocs/status.md`, `plan_current/S019` moved to `plan_done/`.
- MANUAL checked, no change needed: it never described how a finding is
  discharged.
- Tests added: 4, red observed. Suite 142 OK, `--validate` green.
- Next: S020, an audit can be re-run the same day.

## 2026-08-06T17:26+02:00 prompt

> next

## 2026-08-06 recap — S020 an audit can be re-run the same day

- S020 done, closing audit finding F09 (stays `planned` until S027 re-runs the
  audit). This is the step S027 depends on: closing the 2026-08-06 findings
  requires re-running that audit today.
- `--audit new` now takes a sequence suffix when today's report exists:
  `YYYY-MM-DD_<type>.2.md`, `.3.md`. The no-overwrite property is unchanged, and
  the test that used to assert the refusal was re-targeted to assert the suffix
  plus the untouched first report, not deleted.
- Second-order effect found while designing it, not after: the suffix makes the
  first report's stem a prefix of the re-run's, so INV-10's
  `finding_id.startswith(report.stem)` would let a re-run's finding id sit
  unnoticed inside the first report. Tightened to an exact `<stem>-F<nn>` match
  and covered by its own test.
- Red observed: `AssertionError: 1 != 0 : moltke: adocs/audit/2026-08-06_adversarial.md
  already exists; ... Use a different type name, or re-run the audit tomorrow.`
  — the refusal quoted in the finding, and the advice that corrupts the stem.
- Docs: specs CLI row and a dated note; MANUAL's `--audit new` row; AGENTS.md
  section 10 plus `templates/AGENTS.md` byte-identically; the audit skill's
  steps 1 and 5, which told the agent to wait for a new date.
- Files: `bin/moltke.py`, `tests/test_s008_audit.py`, `AGENTS.md`,
  `templates/AGENTS.md`, `skills/audit/SKILL.md`, `adocs/specs.md`,
  `adocs/testing.md` (+4 rows), `MANUAL.md`, `README.md` (142 to 145 tests),
  `adocs/status.md`, `plan_current/S020` moved to `plan_done/`.
- Tests added: 3 new plus 1 re-targeted, red observed. Suite 145 OK,
  `--validate` green.
- Next: S021, optional test_command gate on --step done.

## 2026-08-06T17:54+02:00 prompt

> next

## 2026-08-06 recap — S021 optional test_command gate on --step done

- S021 done, closing audit finding F07 (stays `planned` until S027 re-runs the
  audit). Implements DEC-023.
- `.moltke.json` gains an optional `test_command`. `--step done` runs it after
  every other gate and before touching anything, from the repository root, with a
  shell, under a 600 second timeout, and refuses on non-zero with the command,
  the exit code, and the last 20 lines of combined output. A timeout or a command
  that cannot start is a refusal, not a pass.
- Absent, behaviour is unchanged and `--step done` now says out loud that nothing
  ran the suite. That is the honest half of the fix: AGENTS.md sections 4 and 11
  require a green suite, nothing enforced it, and MANUAL disclosed only the
  weaker README/MANUAL mechanical-gate problem, which read as though the suite
  check was real.
- A non-string or blank `test_command` is a marker violation. Blank goes beyond
  the step's stated acceptance deliberately: a gate that silently checks nothing
  is the exact defect being removed here.
- Schema stays 1 — the key is validated only when present, and every other test
  in the suite still runs on a marker without it.
- Dogfooded: this repository's marker now sets
  `python3 -m unittest discover -s tests`, and S021's own completion ran through
  the gate, printing `moltke: running the suite gate` before moving the step.
- Deviation from the step's `touches`: `templates/moltke.json` was left alone.
  Shipping the key with an empty value would be a marker violation by the rule
  above, and shipping a guessed command would fail on first use in most projects.
  The `init` skill now asks the user for the test command instead, which is where
  a project-specific value belongs.
- Red observed: `AssertionError: 0 != 1 : moltke: S003 completed and moved to
  plan_done/` for the failing-command case, `AssertionError: 'test_command' not
  found in ...` for the unconfigured notice, and `moltke: all checks pass` for the
  non-string marker.
- Files: `bin/moltke.py`, `tests/test_s007_step.py`, `.moltke.json`, `AGENTS.md`,
  `templates/AGENTS.md`, `skills/init/SKILL.md`, `adocs/specs.md`,
  `adocs/testing.md` (+8 rows), `MANUAL.md`, `README.md` (145 to 151 tests),
  `adocs/status.md`, `plan_current/S021` moved to `plan_done/`.
- Tests added: 6, red observed. Suite 151 OK, `--validate` green.
- Next: S022, worklog secret-shape check runs in the suite.

## 2026-08-06T18:17+02:00 prompt

> next

## 2026-08-06 recap — S022 worklog secret-shape check runs in the suite

- S022 done, closing audit finding F08 (stays `planned` until S027 re-runs the
  audit). Implements DEC-024.
- New `tests/test_s022_secrets.py` fails when a prefixed key shape or a PEM
  private-key header appears in `adocs/worklog.md`. Eleven shapes: AWS, GitHub
  classic and fine-grained, Anthropic, OpenAI, Slack, Google, Stripe live, npm,
  PEM, JWT.
- Non-vacuity is not a comment, it is two tests: every shape must first match its
  own synthetic example, and the scan must report a planted one at the right line.
  That guard earned itself on the first run — the Google example was 36 characters
  against a 35-character pattern:
  `AssertionError: None is not true : Google API key no longer matches its own
  example; the check below would pass by failing to look`. Without it the shape
  would have sat there matching nothing.
- Red observed on the real file, not just a fixture: planted a synthetic AWS key
  in `adocs/worklog.md`, ran the check, restored the file and verified the restore.
  `AssertionError: Lists differ: [('AWS access key id', 709, 'AKIAIOSF')] != []`,
  exit 1. The report gives label, line, and 8 characters — never the whole value.
- No entropy or bare-hex rule, deliberately: every recap here carries a commit sha
  and several carry md5 digests, so those heuristics would make the suite red
  every turn. A benign-strings test locks that in.
- S030 had already removed the worse half of F08. The worklog left INV-8, so
  cleaning a leak is an ordinary edit — no invariant to work around, no decision
  entry needed to authorise it. MANUAL's escape procedure says rotate the
  credential first, then edit, and explains why history rewriting is not the fix:
  the value stays recoverable from any clone regardless.
- Gap found and not papered over: the check lives in moltke's own suite, so a
  repository that installs the plugin does not inherit it. That is independent
  work, so it went to `plan_todo/` as S031 rather than being done now. Its
  acceptance requires a decision on where the check runs, because a false positive
  on someone else's worklog must not be able to deadlock their session.
- Files: new `tests/test_s022_secrets.py`, `MANUAL.md`, `adocs/specs.md`,
  `adocs/testing.md` (+4 rows), `README.md` (151 to 155 tests), `adocs/plan.md`,
  new `adocs/plan_todo/S031_worklog_secret_check_ships.md`, `adocs/status.md`,
  `plan_current/S022` moved to `plan_done/`.
- Tests added: 4. Suite 155 OK, `--validate` green, and completion ran through
  S021's suite gate.
- Next: S023, surface guard covers skills, hooks, and marker keys.

## 2026-08-06T18:26+02:00 prompt

> next

## 2026-08-06 recap — S023 surface guard covers skills, hooks, and marker keys

- S023 done, closing audit finding F10 (stays `planned` until S027 re-runs the
  audit).
- Baseline observed before writing anything, because F10's sharpest claim deserved
  confirmation: deleting the `Stop` event from `hooks/hooks.json` left the entire
  suite green — `suite exit with Stop hook deleted: 0`, `OK`. The old assertion was
  satisfied by any one surviving event.
- The golden gained three lines: declared skills, declared hook events, and
  `MARKER_KEYS`. The specs-and-MANUAL cross-check now applies to each, exactly as
  it does to flags.
- A skill counts as documented only where it is named as a component,
  `/moltke:<name>` or in backticks. Matching the bare word would be meaningless
  here: "step" and "audit" appear constantly in this prose.
- New `MARKER_KEYS` in `bin/moltke.py`, pinned load-bearing by a test that gives
  every declared key an invalid value and requires `check_marker` to name it. So
  the list cannot drift into decoration. An undeclared key stays ignored rather
  than rejected, with its own test, so no existing marker breaks.
- Declarations centralised in a new `tests/surface.py`, read by both the golden and
  `tests/test_s010_plugin.py`, whose hardcoded `SKILLS` tuple was what made a
  fourth skill invisible.
- Red observed for all three tamper kinds:
  `'skills: audit,bogus,init,step' != 'skills: audit,init,step'` plus
  `Lists differ: ['skill bogus'] != []`;
  `'hooks: PostToolUse,PreToolUse,SessionStart,UserPromptSubmit' != '...,SessionStart,Stop,UserPromptSubmit'`;
  `'enabled,lint_command,plan_active_max,...' != 'enabled,plan_active_max,...'`.
  The marker-key tamper also tripped the load-bearing pin:
  `lint_command is in MARKER_KEYS but check_marker ignores it, so the golden
  guards a key that means nothing`. Every tampered file was restored and verified.
- MANUAL needed no change, and that is a result rather than an omission: it already
  named every skill, hook event, and marker key, which is why the widened
  cross-check passed on its first run against both documents.
- Files: `bin/moltke.py`, new `tests/surface.py`, `tests/test_s009_surface.py`,
  `tests/test_s010_plugin.py`, `tests/golden/cli_surface.txt`, `adocs/specs.md`,
  `adocs/testing.md` (+7 rows), `README.md` (155 to 160 tests, golden description
  widened, layout line), `adocs/status.md`, `plan_current/S023` moved to
  `plan_done/`.
- Tests added: 5. Suite 160 OK, `--validate` green.
- Next: S024, a plan.md id with no step file is a violation.

## 2026-08-06T18:37+02:00 prompt

> next

## 2026-08-06 recap — S024 a plan.md id with no step file is a violation

- S024 done, closing audit finding F11 (stays `planned` until S027 re-runs the
  audit).
- INV-3 was one-directional: every step file had to appear in `plan.md`, but not
  the reverse. `derived_next` returns the first id in plan order whether or not a
  file exists, so a mistyped id became the next step permanently, and because
  `--step status` writes that same value into `status.md`, the two agreed and
  nothing looked wrong.
- The reverse check reads ids through `strip_guidance` like everything else, and
  that mattered immediately: the scaffolded `plan.md` ships a commented example
  step, so counting it would have made every fresh repository violate INV-3 on
  creation. Covered by its own test, with a completed-step test as the
  non-vacuity anchor.
- Red observed: `AssertionError: 0 != 1 : moltke: all checks pass`.
- Probed in a throwaway repo whose plan lists `S099` first, to check the claim in
  the acceptance rather than assume it: `--validate` exit 1, `--post-write` exit 2,
  `--stop` exit 2, each printing the phantom by name.
- Residual recorded rather than fixed: `--session-start` still reports
  `Derived next step: S099`, because this step's excludes rule out changing
  `derived_next`. So a phantom is loud in three channels but a resumed session
  still sees it announced first. In specs and in the testing ledger.
- Files: `bin/moltke.py`, `tests/test_s003_invariants.py`, `adocs/specs.md`
  (INV-3 wording plus a dated note), `adocs/testing.md` (+5 rows), `README.md`
  (160 to 163 tests), `adocs/status.md`, `plan_current/S024` moved to
  `plan_done/`.
- MANUAL checked, no change needed: it never describes INV-3 by direction.
- Tests added: 4. Suite 163 OK, `--validate` green.
- Next: S025, documented exit-code semantics match the code.

## 2026-08-06T20:08+02:00 prompt

> what is left from the plan?

## 2026-08-06T20:09+02:00 prompt

> next

## 2026-08-06 recap — S025 documented exit-code semantics match the code

- S025 done, closing audit finding F06 (stays `planned` until S027 re-runs the
  audit).
- The documented rule — exit 1 with violations on stdout — held for two modes out
  of eleven. `refuse` prints to stderr and returns 1, and it is the return path
  for every `--step` refusal, `--audit new` on an existing report, the
  `test_command` gate, and an unknown operation.
- Derived the real mapping by probing rather than by reading: eleven invocations
  across two throwaway repositories, one without git and one with, recording exit
  code and which streams carried output. The README and MANUAL tables were written
  from that matrix.
- The mapping: findings exit 1 on stdout (`run_validate`, `audit_list`,
  `audit_check`); refusals exit 1 on stderr (`refuse`); blocks exit 2 on stderr
  (`mode_pre_write`, `mode_stop`, `mode_post_write`). Exit 1 alone does not tell a
  script which stream to read, so both documents now say to capture both.
- Two details the probe turned up that no document mentioned. `--post-write`
  returns 2 while being non-blocking by contract, since the tool it follows has
  already run. And stderr carries a warning on an exit 0 path: `--audit new`
  outside a git worktree says `--audit check` cannot reconcile the run, and still
  succeeds. Both now documented, because each breaks an assumption a script would
  otherwise make.
- Deviation from the step's `touches`, which listed only the two documents: added
  `tests/test_s025_exit_codes.py`. A doc claim is a claim about code (AGENTS.md
  section 7), and nothing pinned streams, so the same drift could recur silently.
  Red observed by routing `refuse` to stdout — exactly what README used to claim:
  three failures, `AssertionError: '' is not true : a refusal must say why, on
  stderr`. File restored and verified byte-identical.
- No stream was changed. The step's excludes rule it out, because something may
  already parse them.
- Files: new `tests/test_s025_exit_codes.py`, `README.md` (exit-code line replaced
  with a four-row table, 163 to 173 tests), `MANUAL.md` (one-line claim replaced
  with a table plus a scripting warning), `adocs/testing.md` (+6 rows),
  `adocs/status.md`, `plan_current/S025` moved to `plan_done/`.
- specs needed no edit: no behaviour changed and it never made a stream claim.
- Tests added: 10. Suite 173 OK, `--validate` green.
- Next: S026, documentation drift pass.

## 2026-08-06T20:29+02:00 prompt

> next

## 2026-08-07 recap — S026 documentation drift pass

- S026 done, closing audit finding F13 (stays `planned` until S027 re-runs the
  audit). Last of the fourteen fixes; S027 is the re-run that closes them.
- Item 1, MANUAL's install section: the stale "once the repository is hosted"
  conditional is gone. It now leads with
  `claude plugin marketplace add https://github.com/macsimbodnar/moltke` and keeps
  the local-checkout form for developing moltke itself. The URL was fetched
  unauthenticated first and returned the repository page, so it is checked rather
  than assumed.
- Item 2, `plugin.json` gains `"repository"`. Verified against the live plugin
  reference before adding it, as the acceptance required: the manifest field table
  lists `repository`, type string, "Source code URL". `claude plugin validate .`
  passes with it present.
- Item 3 had partly resolved itself: `adocs/plan_todo/` exists now because
  S014..S031 live there. But it was empty when the audit ran and will be empty
  again, so `.gitkeep` went into `plan_todo/`, `plan_current/`, and `plan_done/`.
  `adocs/audit/.gitkeep` was already tracked. `SCAFFOLD_DIRS` names all four, so
  moltke finally matches the layout it scaffolds.
- The sweep for "no live doc statement the code contradicts" found two more that
  the finding did not list:
  - README claimed "Developed and tested on Python 3.12" while every run this
    session was on the system 3.9.6. Ran the suite on both `python3` (3.9.6) and
    `/opt/homebrew/bin/python3.14` (3.14.6): 173 OK on each. README now says
    exactly that, and claims no lower bound because none was tested.
  - Twelve Python 3.12 `.pyc` files were tracked, committed in `1064774` during
    S013. Under DEC-020 the repository root is the plugin root, so they were
    copied into every install. Removed, and `__pycache__/` added to `.gitignore`.
    That is also where the stale 3.12 claim came from.
- Re-verified three other README claims against code rather than leaving them:
  no environment variables (`grep` for `os.environ|getenv|environ` finds nothing),
  five hook events, three skills — the last two now pinned by the S023 golden.
- Infrastructure note, not a code problem: the host suspended repeatedly during
  this step. `time` reported 18 and 32 minutes wall clock at 0-1% CPU while
  unittest's own timer said 28.7s and 29.1s, 173 OK both times. Long commands
  were moved to the background rather than fought.
- Files: `.claude-plugin/plugin.json`, `MANUAL.md`, `README.md`, `.gitignore`,
  three new `.gitkeep` files, twelve `.pyc` files removed, `adocs/testing.md`
  (+7 rows), `adocs/status.md`, `plan_current/S026` moved to `plan_done/`.
- Tests added: none; this step is documentation and repository hygiene, and the
  rows record observations. Suite 173 OK, `--validate` green.
- Next: S027, bump 0.3.0, re-run the audit, close findings.

## 2026-08-07T10:29+02:00 prompt

> yes i know about that, i put it on sleep. Let's go with next task

## 2026-08-07T11:08+02:00 prompt

> next

## 2026-08-07 recap — S027 bump 0.3.0, re-run the audit, close findings

- S027 done. `plugin.json` is 0.3.0, `claude plugin validate .` passes, and the
  2026-08-06 audit is closed out from a real re-run rather than from assertions.
- Verdicts on all fourteen prior findings, each decided against the code and not
  against the step files or commit messages: twelve `closed`, F03 `accepted`
  under DEC-022 because it still reproduces exactly as written and that was the
  decision, F02 held `planned` because the installed plugin here is still pinned
  to 0.2.0 at `1064774` whose bare equality is the defect. F02 closes when 0.3.0
  is installed and a live spawn re-probes the fence, which is Max's under DEC-014.
- Three of the twelve closures carry a caveat the report records rather than
  buries: the S015 recap gate can be silently disabled again by the new F02, the
  suite gate still fails open on a malformed `test_command`, and one path still
  contradicts the exit-code mapping S025 documented.
- Eleven new findings, four of them high, each mapped one-to-one to a step,
  S032..S042, ordered by severity ahead of the remaining feature work per §3.
  S044 added as the next closure run. `--audit list` exits 0.
- The two that matter most are both defects this session introduced. S018's
  history baselines gave the immutability invariants no legal terminal state: one
  committed accident makes `--validate` permanently red and the prescribed fix
  does not clear it, with DEC-013's own authorised reorder as the worked example.
  And S019's `strip_guidance` deletes to end-of-file on an unbalanced fence — the
  re-run's own report reproduced it on itself, hiding nine of eleven findings from
  `--audit list` while it exited 0.
- `--audit check` reported exactly one unexpected change, `adocs/worklog.md`, and
  it was right to be suspicious and wrong about the culprit: the plugin's own
  `UserPromptSubmit` appended two prompts during the run. The reviewer had already
  filed that as a finding, and it then reproduced live on this very run. `git diff`
  confirmed two prompt headings and nothing else.
- Negative result worth keeping: the reviewer mutated twelve of the new behaviours
  in a copy of the repository and got twelve reds, no survivors. "The suite is
  green" and "the suite would notice" are different claims.
- Found while regenerating status at the very end, and not by any check: a
  description paragraph naming `S028, S029, and S031` above the ordered list made
  `--step status` write `Next: S028` while the list began at S034. `derived_next`
  takes the first id in document order, and `--validate` stayed green because
  INV-3's reverse direction is satisfied by ids that do have files. Prose ids
  removed, `Next: S034` restored, weakness planned as S045 — which also inherits
  the three pre-existing prose ids in this file as its fixtures.
- Deviation from the step's accepts: the re-run took a new date rather than
  S020's same-day suffix, because midnight passed mid-session. S020 is still what
  made a same-day close possible; it simply was not needed today.
- Files: `.claude-plugin/plugin.json`, `adocs/audit/2026-08-07_adversarial.md`,
  `adocs/audit/2026-08-06_adversarial.md` statuses plus a closure section,
  twelve new step files, `adocs/plan.md`, `adocs/testing.md` (+7 rows),
  `adocs/status.md`, `plan_current/S027` moved to `plan_done/`.
- README and MANUAL checked, no change needed: the version lives in plugin.json
  and both already describe it as the thing that gates updates.
- Tests added: none; this step re-runs and triages. Suite 173 OK, `--validate`
  green, `--audit list` exit 0.
- Next: S045, then S034 and the rest of the 2026-08-07 findings.

## 2026-08-07T11:57+02:00 prompt

> what is left to do?

## 2026-08-07T12:26+02:00 prompt

> Proceed one by one untill completion or when you think would be good to run another audit

## 2026-08-07 recap — S045 plan order comes from the list

- S045 done. Not an audit finding: this was found at the end of S027 by
  regenerating `status.md` and reading the result, which no check would have
  caught.
- `derived_next` now reads plan order through a new `plan_order`, which matches
  list entries only — a line starting `1.`, `-`, or `*`. Bullets are accepted as
  well as numbers so a repository that writes its plan as a bullet list does not
  silently lose its order.
- INV-3 is untouched and still scans the whole file in both directions. A prose
  id with no step file is still a typo worth reporting; it just no longer decides
  what to work on next.
- Red observed: `AssertionError: 'S002' != 'S003'`.
- Verified on the real plan, not only on fixtures: inserted a sentence naming
  S044 and S028 above the description, and `--session-start` still reported
  `Derived next step: S045`. File restored byte-identical.
- Deviation from the step's `touches`: added two sentences to
  `templates/adocs/plan.md`. The code no longer misreads prose, but a user
  writing their first plan should know where order is read from, and that is the
  file they are looking at.
- Files: `bin/moltke.py`, `tests/test_s007_step.py`, `adocs/specs.md`,
  `templates/adocs/plan.md`, `adocs/testing.md` (+6 rows), `README.md`
  (173 to 177 tests), `adocs/status.md`, `plan_current/S045` moved to
  `plan_done/`.
- MANUAL checked, no change needed: it never describes how plan order is parsed.
- Tests added: 4. Suite 177 OK, `--validate` green.
- Next: S034, which needs a recorded decision before it can start.

## 2026-08-07 recap — S034 a committed immutability violation has a legal way back to green

- S034 done, closing 2026-08-07_adversarial-F03, the worst thing the re-run found
  and a defect S018 introduced.
- Max chose the terminal state: a repair commit clears it. DEC-026 records that,
  with the two rejected options and their costs.
- Both invariants now judge current content against a fixed historical version
  rather than the existence of a bad commit. INV-7 compares each `plan_done/`
  file against the version at the commit that added it; INV-8 compares
  `decisions.md` against the version at its first commit. Blobs come from one
  batched `git cat-file`, so both stay at two or three git processes per run.
- The mechanism took three attempts and each was measured, not argued.
  Requiring every past version to be a prefix is unsatisfiable after a repair,
  because the tampered version is itself history — that is the same permanence
  defect wearing a different shape. Forgiving a version when a longer one is a
  prefix cleared the repair but also cleared a genuine same-position rewrite, and
  the existing `test_committing_a_rewrite_does_not_hide_it` caught it. Pairwise
  adjacent checks did not clear a correct repair. All three results are in
  DEC-027 so the next person does not re-derive them.
- The chosen rule is weaker than the one it replaces in one stated way, and the
  gap was measured in a throwaway repository rather than guessed: legitimate
  append exit 0, post-baseline rewrite uncommitted exit 1, the same rewrite
  committed exit 0, baseline rewrite committed exit 1. Planned as S046 and
  written into specs and MANUAL, not left in a code comment.
- Red observed on both invariants, and both tests assert the violation before the
  repair so a green result cannot come from the check having stopped working.
- Files: `bin/moltke.py` (new `git_blobs`, rewritten history halves of
  `inv_7_done_immutable` and `inv_8_append_only`), `tests/test_s003_invariants.py`,
  `tests/test_s004_invariants.py`, `adocs/decisions.md` (DEC-026, DEC-027),
  `adocs/plan.md`, new `adocs/plan_todo/S046_inv8_post_baseline_rewrites.md`,
  `adocs/specs.md`, `adocs/testing.md` (+8 rows), `MANUAL.md`, `README.md`
  (177 to 182 tests), `adocs/status.md`, `plan_current/S034` moved to `plan_done/`.
- Tests added: 5. Suite 182 OK, `--validate` green.
- Next: S046, then S035.

## 2026-08-07T14:04+02:00 prompt

> go

## 2026-08-07 recap — S046 INV-8 catches a committed post-baseline rewrite

- S046 done. Not an audit finding: this is the gap S034 created and measured
  rather than hid, planned the same turn it was found.
- INV-8's history check now keeps a high-water mark. Versions are walked oldest
  first; one that still contains, in order, every line the mark requires becomes
  the new mark, one that dropped something is a tampering and is skipped. The
  file as it stands must contain the mark's lines, in order.
- Two more candidates were implemented and measured before this one stuck, which
  is the whole reason the rule looks the way it does. Comparing against every
  past version by line subsequence catches the rewrite but still fails after a
  repair, because a rewrite introduces a line the repair rightly discards, so the
  tampered version is not a subsequence of the corrected file either — observed as
  `VIOLATION: INV-8: ... no longer contains, in order, the lines it had at commit
  10cbde36`. Comparing against the longest past version misses a rewrite that
  lengthens the file, which is the common shape of an in-place edit. DEC-028
  records both, and DEC-027 stays as the record of the fixed-baseline attempt.
- Skipping tampered versions is what reconciles the two halves: a repair restores
  the mark and clears the whole history at once, while a removal, an in-place
  rewrite, and a line moved to the end are each caught, because in every one a
  required line is no longer in order.
- The five states DEC-027 measured were re-measured, not assumed: the gap row
  moved from exit 0 to exit 1 and the other four are unchanged.
- Two behaviours stated rather than left to be discovered: mid-file insertion
  passes, since only removal and reordering break a subsequence, and reordering
  entries is a violation until reversed — which is what DEC-013's authorised
  reorder would be today.
- The commit for this step was delayed by a transient tool outage between
  completing the step and writing this recap; nothing about the work changed.
- Files: `bin/moltke.py` (new `lines_survive`, rewritten history half of
  `inv_8_append_only`), `tests/test_s004_invariants.py`, `adocs/decisions.md`
  (DEC-028), `adocs/specs.md`, `adocs/testing.md` (+4 rows), `MANUAL.md`,
  `README.md` (182 to 184 tests), `adocs/status.md`, `plan_current/S046` moved to
  `plan_done/`.
- Tests added: 2. Suite 184 OK, `--validate` green.
- Next: S035, the linked worktree and submodule case.

## 2026-08-07T14:43+02:00 prompt

> next

## 2026-08-07 recap — S035 moltke works in a linked worktree and a submodule

- S035 done, closing 2026-08-07_adversarial-F04.
- Three separate helpers each decided "is there git here" by testing whether
  `.git` is a directory. In a linked worktree and in a submodule it is a file, so
  all three failed at once and silently: no audit baseline, no prompt-failure
  breadcrumb, and no `Stop` deadlock cap — while `--validate` reported all checks
  pass and `--audit new` claimed there was no git worktree inside a worktree
  where git works.
- The cap is the one that matters. INV-12 and DEC-006 make no-deadlock an
  invariant, and combined with the S034 defect a session in a worktree could have
  been wedged with no way out.
- One `git_dir` helper now asks `git rev-parse --absolute-git-dir`. It returns the
  per-worktree git directory, which is what these files want to be anyway, and
  its failure is the real "no git here" signal rather than a guess about a
  filename.
- Red observed live before the fix, in a real `git worktree add`: `[2,2,2,2,2]`
  against a clone's `[2,2,2,0,0]`, plus
  `AssertionError: 'no git' unexpectedly found in 'moltke: no git worktree here...'`.
- Verified after the fix across three real repositories rather than one: clone,
  linked worktree, and submodule all `[2,2,2,0,0]`, with `.git` confirmed a file
  in the latter two. The submodule case was in the finding and had no test of its
  own, so it was checked by hand.
- The `--audit new` warning now says "no git repository", which is what it means.
  README's copy of that phrase was corrected in the same commit.
- Files: `bin/moltke.py` (new `git_dir`, three call sites, the warning text),
  `tests/test_s005_hooks.py`, `tests/test_s008_audit.py`, `adocs/specs.md`,
  `adocs/testing.md` (+4 rows), `MANUAL.md`, `README.md` (184 to 187 tests and the
  warning phrase), `adocs/status.md`, `plan_current/S035` moved to `plan_done/`.
- Tests added: 3. Suite 187 OK, `--validate` green.
- Next: S033, the unbalanced code fence.

## 2026-08-07T14:51+02:00 prompt

> next

## 2026-08-07 recap — S033 an unbalanced code fence cannot hide content

- S033 done, closing 2026-08-07_adversarial-F02, the finding the reviewer
  reproduced on its own report while writing it.
- `strip_guidance` paired ``` markers globally and non-greedily, so one stray
  marker shifted every later pairing and deleted the real content between two
  unrelated fences. A rule written to make guidance invisible was making evidence
  invisible.
- Now markers must open a line and are paired in order, and an unpaired trailing
  marker is text rather than swallowing to end of file. Line-anchoring matters on
  its own: every worklog prompt is quoted, so a pasted fence arrives as a quoted
  marker and was being counted as a fence.
- What could not be fixed, and why, measured rather than argued: two unclosed
  fences are byte-identical to one closed fence. I tried to resolve it by
  refusing to swallow heading lines, then checked whether that was safe — it is
  not. `templates/audit_report_template.md`, `templates/adocs/decisions.md`, and
  `AGENTS.md` each put a markdown heading inside a fence deliberately, and hiding
  exactly those is what `strip_guidance` was built for. Parity does not help
  either: two unclosed fences are an even count.
- So the ambiguity is reported instead of guessed. New INV-13: an odd number of
  fence markers in `plan.md`, `decisions.md`, `worklog.md`, or any audit report is
  a violation naming the file.
- Deviation from the step's `touches`, which asked for a suite check: this is an
  invariant instead. A suite check would protect moltke's own repository and
  nobody else's, and F02 is high severity in every repository that installs the
  plugin. Not in `CHEAP_CHECKS`, because the worklog grows without bound and this
  reads it whole.
- Two strip-level tests were re-targeted once the templates settled the question,
  rather than deleted. They now assert the ambiguity explicitly and point at the
  INV-13 tests as the safety net.
- Both live reproductions from the finding were re-run. The recap gate now blocks
  where the finding measured an allow, and `--validate` names the unclosed fence.
- Checked before adding the invariant that this repository has no odd counts, so
  INV-13 was not layered on top of an existing violation.
- Files: `bin/moltke.py` (`strip_guidance`, new `inv_13_balanced_fences`, the
  registry), new `tests/test_s033_fences.py`, `adocs/specs.md` (INV-13 and a
  dated note), `adocs/testing.md` (+7 rows), `MANUAL.md`, `README.md` (187 to 200
  tests), `adocs/status.md`, `plan_current/S033` moved to `plan_done/`.
- Tests added: 13. Suite 200 OK, `--validate` green.
- Next: S032, `--audit check` sees a change the run commits.

## 2026-08-07T15:08+02:00 prompt

> next

## 2026-08-07 recap — S032 --audit check sees a change the run commits

- S032 done, closing 2026-08-07_adversarial-F01.
- The check diffed two `git status` snapshots. A clean tracked file that the run
  patched and committed was in neither, so it was not misclassified, it was
  absent — and the check printed "no change since --audit new" for a run that had
  rewritten source. DEC-022 traded the write fence away for this check, so
  `git commit` defeated the thing that replaced the fence, and the audit skill
  tells the operator a clean check means the report is uncontaminated.
- `--audit new` now records the `HEAD` sha next to the worktree snapshot, and
  `--audit check` reports `git diff --name-status --no-renames` from it as part of
  the footprint. Commits are classified by the same rule as working-tree changes:
  the report and files added under `tests/` are expected, anything else is not.
- An unreachable baseline `HEAD` is reported rather than skipped, because that
  means history was rewritten under the run — silence there would be the same
  class of defect as the one being fixed.
- The second failure the finding noted inside the first is fixed too: the exit-0
  message claimed the report had not been written yet while it had been written
  and committed. It now names both halves of what it checked.
- Red observed as the finding's own message, verbatim:
  `AssertionError: 0 != 1 : no change since --audit new; the report itself has
  not been written yet.`
- The finding's F1 scenario was re-run end to end: exit 1, `src/main.py: M in a
  commit made during this run` listed as unexpected, the report's own commit
  still expected.
- MANUAL's claim that a committed change "shows up as reverted or committed,
  which is flagged as unexpected rather than hidden" was false for the common
  case and is gone; that branch only ever fired for a file already dirty at
  baseline.
- Files: `bin/moltke.py` (`audit_new` records `head`, `audit_check` reads
  commits), `tests/test_s008_audit.py`, `adocs/specs.md`, `adocs/testing.md`
  (+6 rows), `MANUAL.md`, `README.md` (200 to 204 tests), `adocs/status.md`,
  `plan_current/S032` moved to `plan_done/`.
- Tests added: 4. Suite 204 OK, `--validate` green.
- Next: S038, the malformed test_command.

## 2026-08-07T15:17+02:00 prompt

> next

## 2026-08-07 recap — S038 a malformed test_command refuses completion

- S038 done, closing 2026-08-07_adversarial-F07.
- `check_marker` had always flagged a malformed `test_command`. The defect was
  wiring: `--validate`, `--post-write`, and `--stop` were handed the marker
  violations and `--step` was not, so the one command that gates completion was
  the one that could not see the marker it depends on. `--step done` completed
  green and reported that the key was absent while it was present and wrong.
- Fixed at the dispatch rather than inside the gate: `mode_step` now takes the
  marker violations and refuses any operation while they exist. That covers
  `start`, `new`, and `status` too, which is right — a repository with a broken
  marker should not be moving its plan around at all.
- Red observed on all four of the finding's values, each completing the step:
  `AssertionError: 0 != 1 : moltke: no "test_command" in .moltke.json ...
  moltke: S003 completed and moved to plan_done/`.
- Re-measured after the fix: `''`, `'   '`, a list, and `0` all give exit 1 with
  the step still in `plan_current/`, where the finding measured exit 0 and a
  completed step in every case.
- The wrong message was half the finding and is asserted against directly, not
  just fixed in passing.
- Files: `bin/moltke.py` (`mode_step` signature and guard, the `main` dispatch),
  `tests/test_s007_step.py`, `adocs/specs.md`, `adocs/testing.md` (+5 rows),
  `MANUAL.md`, `README.md` (204 to 206 tests), `adocs/status.md`,
  `plan_current/S038` moved to `plan_done/`.
- Tests added: 2, with four subtests. Suite 206 OK, `--validate` green.
- Next: S039, status.md staleness judged on the whole file.

## 2026-08-07T15:26+02:00 prompt

> next

## 2026-08-07 recap — S039 status.md staleness is judged on the whole file

- S039 done, closing 2026-08-07_adversarial-F08.
- Only the `Next:` line was compared, and that is the one field the file and the
  filesystem rarely disagree about, because both derive it the same way. The
  in-progress stack is the field a crashed session corrupts, which is the exact
  scenario AGENTS.md section 1 says the check exists for.
- All four derived fields are now compared against what `--step status` would
  write, sharing one `status_lines` so the check reads the writer rather than a
  second description of it. `Updated:` and everything from `- Parked:` onward are
  the human's and are ignored.
- The stricter comparison immediately exposed two things that were wrong and are
  fixed rather than worked around. A freshly scaffolded repository read as stale,
  because the template says `no steps planned yet` while the code said `no steps
  left in plan.md` — different states, and the template's wording is the right one
  for a repo that has planned nothing, so `status_lines` distinguishes them. And
  `Last done` was picked from every id in `plan.md` including prose, the same
  defect S045 fixed for `derived_next` and missed here; it reads `plan_order` now.
- The test fixture's `status.md` was an approximation that the old check never
  noticed. It is now byte-for-byte what the tree derives, with a comment saying
  why, since an approximation would make every fixture repository read as stale.
- Red observed on four tests, including `AssertionError: 0 != 2` for the Stop
  case.
- The finding's own state was reproduced and is now named:
  `status.md is stale (In progress says 'none', filesystem says 'S003 active')`,
  with `--stop` exiting 2, where the finding measured silence from both.
- Files: `bin/moltke.py` (`status_fields`, `status_disagreements`, `status_lines`
  split out of `step_status`, both hook call sites; `status_next` removed),
  `tests/test_s005_hooks.py`, `tests/fixtures.py`, `adocs/specs.md`,
  `adocs/testing.md` (+6 rows), `MANUAL.md`, `README.md` (206 to 212 tests),
  `adocs/status.md`, `plan_current/S039` moved to `plan_done/`.
- Tests added: 6. Suite 212 OK, `--validate` green.
- Next: S037, the Stop gate's `.claude` prefix.

## 2026-08-07T15:39+02:00 prompt

> next

## 2026-08-07 recap — S037 the Stop recap gate stops treating .claude-plugin/ as not-source

- S037 done, closing 2026-08-07_adversarial-F06. Smallest fix of this batch: one
  tuple, `RECAP_EXEMPT`, matching two directories with their separators instead
  of sharing a seven-character stem.
- `.claude` as a bare prefix exempted `.claude-plugin/plugin.json`, the manifest
  whose `version` decides what every installed copy of moltke executes. A release
  could be cut with no worklog recap of it — and the working tree was carrying
  exactly that change, uncommitted, while the finding was being written. It also
  exempted `.clauderc` and anything else beginning `.claude`.
- Table-driven test over nine representative paths, one subtest each, so the
  question "which paths count as source" has one answer in one place rather than
  being inferred from a regex. Three rows were red.
- The table includes `adocsfoo/notes.md` as well, since `adocs/` had the same
  shape of risk and only avoided it by having a trailing slash already.
- The finding's own six-row measurement was re-run: `.claude-plugin/plugin.json`
  and `.claudefoo` moved from allow to block, the other four unchanged.
- Files: `bin/moltke.py` (`RECAP_EXEMPT`, `mode_stop`), `tests/test_s005_hooks.py`,
  `adocs/specs.md`, `adocs/testing.md` (+4 rows), `MANUAL.md`, `README.md`
  (212 to 213 tests), `adocs/status.md`, `plan_current/S037` moved to `plan_done/`.
- Tests added: 1, covering nine paths. Suite 213 OK, `--validate` green.
- Next: S036, --audit check blaming the hook's own worklog write on the reviewer.

## 2026-08-07T15:53+02:00 prompt

> next

## 2026-08-07 recap — S036 --audit check does not blame the hook's worklog writes on the reviewer

- S036 done, closing 2026-08-07_adversarial-F05.
- `UserPromptSubmit` appends to the worklog on every prompt, so every audit that
  spanned a prompt had a worklog change in its footprint, attributed to a reviewer
  that is fenced out of that file and never touched it. The finding's point was
  not the noise but the consequence: a gate that is wrong every time is one people
  learn to wave through, and F01 is what it was letting past while it cried wolf.
- `--audit new` now records the worklog's length and content hash, and the check
  treats a worklog change as expected only while the file still starts with
  exactly those bytes. Length plus hash proves growth without keeping a copy of
  the file.
- Scoped to appends rather than to the path, which is the whole distinction: an
  append is what the hook does, a truncation or rewrite is what covering your
  tracks looks like and stays reported. Applied to the committed side too, or
  S032's commit comparison would have brought the false positive straight back.
- Red observed as the finding's own output:
  `unexpected, not attributable to writing the report: adocs/worklog.md: M`.
- The finding's isolation sequence was re-measured: clean immediately after
  `--audit new`, clean after one user prompt where it had been exit 1, and exit 1
  again once the worklog is truncated.
- Worth recording because it nearly fooled me: my first probe used a one-line
  baseline worklog, so "truncating" it to longer text that started the same way
  was a genuine append and correctly passed. The probe was wrong, not the code.
  The unit tests use a worklog with prior content, which is what makes a
  truncation detectable at all.
- Also observed, not a defect: `--audit check` in this repository still reports a
  large footprint, because the baseline is S027's and that run finished ten steps
  ago. The worklog appears there as unexpected precisely because that baseline
  predates this step and carries no worklog record, so the exemption fails closed.
  The next `--audit new`, in S044, replaces the baseline.
- Files: `bin/moltke.py` (`worklog_prefix`, `worklog_only_grew`, `audit_new`,
  `audit_check`), `tests/test_s008_audit.py`, `adocs/specs.md`,
  `adocs/testing.md` (+5 rows), `MANUAL.md`, `README.md` (213 to 217 tests),
  `adocs/status.md`, `plan_current/S036` moved to `plan_done/`.
- Tests added: 4. Suite 217 OK, `--validate` green.
- Next: S041, the reviewer fence and relative paths.

## 2026-08-07T16:00+02:00 prompt

> nexy

## 2026-08-07 recap — S041 the reviewer fence normalises paths before matching

- S041 done, closing 2026-08-07_adversarial-F10.
- `pathlib` does not normalise `..`, so `rel.parts` only had to begin with an
  allowed component: `tests/../bin/moltke.py` was permitted for the reviewer while
  the absolute form of the same path was blocked, because absolute paths were
  already resolved. The inconsistency is what made it a hole rather than a design.
- Fixed by resolving once, before any rule reads the path. That matters more than
  the fence alone: the same `rel` feeds the `plan_done` rule and the step-file
  rule, so all three were affected. Red was observed on two of the three.
- Acceptance narrowed, and recorded rather than quietly dropped. The step file I
  wrote said "any path escaping the root is refused"; the finding only claimed the
  in-repository case. A path resolving outside the repository stays unpoliced,
  which is the existing documented boundary — moltke governs the repository it is
  marked in — and widening it would newly block writes in unrelated repositories.
  My own two tests contradicted each other on this until the suite said so.
- Red observed: `AssertionError: 0 != 2 : ('tests/../bin/moltke.py', '')` and
  `AssertionError: 0 != 2 : ('adocs/plan_todo/../plan_done/S001_base.md', '')`.
- The finding's table was re-measured: both allowed rows now block, the absolute
  equivalent still blocks, and `tests/test_new.py` still passes.
- Files: `bin/moltke.py` (`mode_pre_write` path resolution),
  `tests/test_s008_audit.py`, `tests/test_s005_hooks.py`, `adocs/specs.md`,
  `adocs/testing.md` (+6 rows), `MANUAL.md`, `README.md` (217 to 223 tests),
  `adocs/status.md`, `plan_current/S041` moved to `plan_done/`.
- Tests added: 6. Suite 223 OK, `--validate` green.
- Next: S040, an audit type cannot write outside adocs/audit/.

## 2026-08-07T16:06+02:00 prompt

> next

## 2026-08-07 recap — S040 an audit type cannot write outside adocs/audit/

- S040 done, closing 2026-08-07_adversarial-F09.
- The type went straight into a filename and `audit_new` creates the parent
  directories, so `../../outside/pwned` wrote a report outside the
  `audit_dir.glob("*.md")` that both `inv_10_audit_findings` and `audit_list`
  read. The report looked filed and was counted by nothing, a stray directory was
  left behind, and the finding-id stem degraded to the last path component.
- The printed path made it worse rather than revealing it: `relative_to` is
  lexical, so the message always claimed the report had landed under
  `adocs/audit/`.
- `--audit new` now refuses anything that is not `[A-Za-z0-9_-]+`, checked in
  `mode_audit` before `audit_new` runs, so nothing is created by a refused type.
  The tests assert that directly rather than only checking the exit code.
- A dot is refused too, which the finding noted separately: `UPPER.2` would
  collide with the `.2` namespace S020 reserved for same-day re-runs.
- Red observed across nine cases, including
  `AssertionError: 0 != 1 : moltke: created adocs/audit/2026-08-07_sec;rm.md`.
- Non-vacuity matters here more than usual, since a too-strict rule would break
  documented usage: `adversarial`, `security`, `bugs`, `perf-2`, and `dep_scan`
  are all asserted to still work.
- The audit skill described types as free-form, which was a doc claim the code now
  contradicts, so it was corrected in the same commit.
- Files: `bin/moltke.py` (`mode_audit`), `tests/test_s008_audit.py`,
  `skills/audit/SKILL.md`, `adocs/specs.md`, `adocs/testing.md` (+5 rows),
  `MANUAL.md`, `README.md` (223 to 227 tests), `adocs/status.md`,
  `plan_current/S040` moved to `plan_done/`.
- Tests added: 4, one with seven subtests. Suite 227 OK, `--validate` green.
- Next: S042, the test_command refusal stream — last of the eleven.

## 2026-08-07T18:10+02:00 prompt

> where we are in the plan?

## 2026-08-07T18:11+02:00 prompt

> next

## 2026-08-07 recap — S042 the test_command refusal obeys the documented stream mapping

- S042 done, closing 2026-08-07_adversarial-F11. Last of the eleven findings from
  the 2026-08-07 re-run to be fixed in code.
- The suite-gate banner printed to stdout while `refuse` wrote to stderr, so one
  refusal arrived split across both streams. A consumer following the mapping
  README and MANUAL document — read stderr on exit 1 — got the refusal but not
  the banner; one switching streams on the exit code got half the message.
- The sharper half of the finding was about the test, not the code: S025's
  `TestRefusalsGoToStderr` states the rule as an assertion and covered a step
  refusal, an unknown operation, and `--audit check` without a baseline — the
  three paths that satisfied it — while the one path that would have failed it was
  absent. A test that states a rule and omits the case that breaks it is not
  covering the rule. That case is now in the class.
- Banner moved to stderr. It is progress, not a finding, and on a passing gate it
  is stderr output on an exit 0 path, which S025 already documents as a real case.
- The "no `test_command` configured" notice stays on stdout: it accompanies a
  successful completion rather than a refusal, and S021's test pins it there.
- Red observed: `AssertionError: 'moltke: running the suite gate: ...' is not
  false : a refusal must not go to stdout`.
- Re-measured: exit 1, `stdout: ''`, banner first on stderr.
- MANUAL needed no change, and that is the point of this one: its exit-code table
  already documented the rule. The code was wrong, not the documentation.
- Files: `bin/moltke.py` (`run_test_command`), `tests/test_s025_exit_codes.py`,
  `adocs/specs.md`, `adocs/testing.md` (+3 rows), `README.md` (227 to 228 tests),
  `adocs/status.md`, `plan_current/S042` moved to `plan_done/`.
- Tests added: 1. Suite 228 OK, `--validate` green.
- Next: S044, bump 0.4.0 and re-run the audit to close the eleven.

## 2026-08-07T18:18+02:00 prompt

> next, keep for last my decision

## 2026-08-07 recap — S044 bump 0.4.0, re-run the audit, close the findings

- S044 done. `plugin.json` is 0.4.0, and the 2026-08-07 audit is closed out from a
  re-run rather than from the eleven step files claiming success.
- Ten of eleven no longer reproduce, each decided by running the tool in throwaway
  repositories. F02 stays `planned`, and the reason is a real miss of mine: S033
  fixed the odd-marker case and the recap-gate case and pointed at INV-13 for the
  rest, but two unclosed fences are an *even* count, so INV-13 never fires and the
  original transcript reproduces verbatim. The specs note I wrote for S033 said
  the ambiguity was "reported rather than guessed"; it was reported only half the
  time. S049 covers the remainder, S051 the MANUAL sentence that already claims it
  is fixed.
- The re-run exercised S020 for real: today already had a report, so this one
  became `2026-08-07_adversarial.2.md` with its own finding-id stem.
- `--audit check` reconciled clean, exit 0, on a run spanning several prompts.
  That is S036 working on its first real audit — the same worklog append was
  reported as unexpected on every previous run.
- Ten new findings, two high, and both high ones are consequences of this batch
  rather than old code. The Stop waiver keys on a `prompt_id` that nothing in the
  repository establishes exists, and without it the counter is global and
  persistent, so from the fourth blocked turn onward every Stop check is off and
  stays off across sessions. And S045's narrowing of `plan_order` left INV-3
  reading the whole file, so a step named only in prose passes validation while
  being invisible to `derived_next` — a prime-directive violation I introduced
  while fixing a prime-directive violation.
- The reviewer also mutation-tested: 17 behaviours deleted in copies outside the
  repository, 16 caught, one survivor. The README/MANUAL stamp gate can be deleted
  outright with 228 tests still green. That is now part of S050.
- 2026-08-06_adversarial-F02 stays `planned` for a second run, and this time the
  installed-plugin claim was proved rather than inferred: the `PostToolUse` hook
  reported 8 of the reviewer's 10 findings, and running both copies of
  `bin/moltke.py` over the same input reproduces exactly that split.
- One process slip worth recording: my status-update script matched the finding-id
  in the report's own fenced format example before the real heading, and set that
  to `closed`. Caught by reading `--audit list`, restored, and the real F01 set
  instead. The same guidance-is-not-data rule that INV-10 respects does not apply
  to a regex written in a hurry.
- Files: `.claude-plugin/plugin.json`, `adocs/audit/2026-08-07_adversarial.2.md`,
  `adocs/audit/2026-08-07_adversarial.md` statuses plus a closure section, eleven
  new step files, `adocs/plan.md`, `adocs/testing.md` (+8 rows), `adocs/status.md`,
  `plan_current/S044` moved to `plan_done/`.
- Tests added: none; this step re-runs and triages. Suite 228 OK, `--validate`
  green, `--audit list` exit 0.
- Next: S047, the Stop deadlock waiver.

## 2026-08-08T00:04+02:00 prompt

> next

## 2026-08-07 recap — S047 the Stop deadlock waiver cannot become an off switch

- S047 done, closing 2026-08-07_adversarial.2-F01, the worse of the two high
  findings from the second re-run.
- The waiver counted consecutive blocks per `prompt_id`, a Stop payload field
  nothing in this repository establishes exists. Absent, the key was the empty
  string for every turn, so the counter was global, persisted on disk, and from
  the fourth blocked turn onward every Stop check was waved through — invariants,
  stale `status.md`, the recap gate, the README and MANUAL stamp — and stayed
  waved through across sessions. Two fail-open routes reach the empty key
  regardless of what Claude Code sends: an unparseable payload and a tty.
- Redesigned rather than confirmed. The alternative was to instrument the
  installed plugin again and observe a live Stop payload, the way S016 did for
  `agent_type`. That would settle one field and still fail open on both
  `hook_input` fallbacks, so the dependency was removed instead. "The same turn"
  is `prompt_id` and `session_id` when present, plus the count of prompt headings
  in the worklog, which `UserPromptSubmit` advances exactly once per turn.
- Two things the accepts asked for and that stand on their own: the count resets
  when the problem set changes, so fixing one thing and hitting another does not
  spend an attempt, and the waived turn prints the problems first. Being waved
  through should not mean being told nothing.
- DEC-029 records the choice and three rejected alternatives, including keying on
  the problem fingerprint alone, which resets correctly on progress but would
  waive a persistently broken repository from its fourth turn onward.
- A coupling worth naming: the worklog is now load-bearing for a hook decision.
  DEC-011 says it is forensic and never a context source; this reads its shape,
  not its content, but the coupling is real and is in the decision entry.
- `mode_stop` now reads stdin once and shares the payload, because a second
  `hook_input()` in the same process gets an empty dict.
- Red observed as the finding's own sequence:
  `AssertionError: Lists differ: [2, 2, 2, 0, 0, 0, 0, 0] != [2, 2, 2, 2, 2, 2, 2, 2]`.
- Re-measured: eight turns now `2 2 2 2 2 2 2 2`; eight retries inside one turn
  still `2 2 2 0 0 0 0 0`, which is the no-deadlock property working; five turns
  with an unparseable payload `2 2 2 2 2`; the waived turn prints `INV-3`.
- Files: `bin/moltke.py` (`stop_turn_key`, `mode_stop`), `tests/test_s005_hooks.py`,
  `adocs/decisions.md` (DEC-029), `adocs/specs.md` (amended in place, superseded
  wording marked), `adocs/testing.md` (+6 rows), `MANUAL.md`, `README.md`
  (228 to 233 tests), `adocs/status.md`, `plan_current/S047` moved to `plan_done/`.
- Tests added: 5. Suite 233 OK, `--validate` green.
- Next: S048, INV-3 and plan_order disagreeing about what "listed" means.

## 2026-08-08T00:11+02:00 prompt

> ok let's start with decisions. Let's do all open points in an iterative way

## 2026-08-08T00:20+02:00 prompt

> I don't care about the security of the decision immutability. this is a tool to help me to avoid repeat always the same instructions to agents and to keep the memory between agents and sessions. I don't want to over engineer it, or to make it more complicated. Practicality and correctenes in work are priority over immutability.

## 2026-08-07 recap — DEC-030 and S054, the threat model is accident, not malice

- Max set the scope when asked to choose on INV-8: moltke exists so he does not
  repeat the same instructions to every agent and so memory survives between
  agents and sessions. Practicality and correctness of the work come first;
  immutability for its own sake does not, and the tool should not grow to defend
  against a hostile author.
- Recorded as DEC-030 rather than applied silently, because it is a triage rule
  for every future finding of that shape, not a one-off answer.
- S054 done, closing 2026-08-07_adversarial.2-F07 by moving the documentation
  rather than the code. INV-8 now reads "no line `decisions.md` has ever held is
  removed or reordered", with the superseded "earlier bytes are unchanged" marked
  in place, and both violation messages reworded to describe their own comparison
  instead of restating the aspiration.
- No behaviour changed, and the suite proves it: 233 tests green with no change to
  `inv_8_append_only`'s logic.
- One thing found while rewording that is worth having in writing: the two halves
  of INV-8 do not agree with each other. The uncommitted window is a byte-prefix
  comparison against HEAD, so a mid-file insertion is reported until it is
  committed and then stops being reported. That asymmetry is now in specs rather
  than smoothed over, and under DEC-030 it is not worth code to remove.
- The accepted cost is stated on INV-8's own line, which is where `AGENTS.md`
  section 3 points a new agent first: the ordering of the decision log is a
  convention, and a careless edit can break it without the tool noticing.
- Process note: running the suite directly and then completing the step in one
  shell command ran it twice and hit the two-minute limit, killing the gate
  mid-run. The testing rows had landed and the step had not. Re-run alone with a
  longer timeout, which is the right shape now that the gate itself takes a minute.
- Files: `bin/moltke.py` (two message strings), `adocs/decisions.md` (DEC-030),
  `adocs/specs.md` (INV-8 line plus a dated note), `adocs/testing.md` (+5 rows),
  `MANUAL.md`, `adocs/status.md`, `plan_current/S054` moved to `plan_done/`.
- Tests added: none; this is a documentation correction by design.
- Next: the remaining open decisions, then S048.

## 2026-08-08T00:40+02:00 prompt

> next

## 2026-08-07 recap — S048 INV-3 and plan_order agree on what listed means

- S048 done, closing 2026-08-07_adversarial.2-F02, and it is my regression: S045
  narrowed `plan_order` to list entries and left INV-3 matching any mention, so
  the two disagreed about what "listed in plan.md" means. A step file named only
  in the description satisfied the invariant while being invisible to
  `derived_next` — `--validate` said all checks pass, `status.md` said no steps
  were left, and `--session-start` printed no derived-next line at all. A fix for
  one prime-directive defect introduced another, which is worth saying plainly
  and is now in specs in those words.
- One definition now, used in both directions: a list entry. Prose ids are prose,
  checked in neither direction. That is what makes the two agree, and it is
  simpler than the alternative of teaching INV-3 a second notion of "mentioned".
- The reverse message also dropped its claim that a phantom "is the derived next
  step". S045 made that false and I did not notice at the time; the audit did.
- Red observed on all three: `AssertionError: 0 != 1 : moltke: all checks pass`
  for the invisible step, and `'is the derived next step' unexpectedly found` for
  the stale message.
- The finding's own fixture was re-measured: `--validate` exits 1 naming
  `adocs/plan_todo/S002_next.md`.
- `templates/adocs/plan.md` restated too. The rule a user needs is one sentence —
  every step file is a list entry, every list entry has a step file — and the
  previous wording said prose ids were still checked, which is no longer true.
- Files: `bin/moltke.py` (`inv_3_steps_in_plan`), `tests/test_s003_invariants.py`,
  `adocs/specs.md` (INV-3 line plus a dated note), `templates/adocs/plan.md`,
  `adocs/testing.md` (+5 rows), `README.md` (233 to 236 tests), `adocs/status.md`,
  `plan_current/S048` moved to `plan_done/`.
- Tests added: 3. Suite 236 OK, `--validate` green.
- Next: S049, two unclosed fences.

## 2026-08-08T00:46+02:00 prompt

> next in the plan

## 2026-08-08T00:50+02:00 prompt

> explain

## 2026-08-08T00:55+02:00 prompt

> let's go with the recommended one

## 2026-08-08T11:06+02:00 prompt

> next

## 2026-08-08T11:19+02:00 prompt

> run all the steps untill you need my inputl

## 2026-08-08T12:13+02:00 prompt

> let's go over them in an iteractive way, put a little explanation on top of the question

## 2026-08-08T13:21+02:00 prompt

> let's proceed with the plan with the findings fix and after all of the fixes let's create a new version. Do not care about migration or backward compatibility

## 2026-08-08T15:53+02:00 prompt

> let's solve open points and then start impliementing the fixes one by one. During the next audit pay attention to not to start finding only minor things in that case it means that you can not find any big issue so no more actions needed because you will start to drift

## 2026-08-08T16:16+02:00 prompt

> i want to add two new rules. 
> 
> * the agent that run the audit must be with clear context. So it does not carry any bias from the old session. They must work like red/blu teams.
> * After each work done i want the agent to print in console a short recap of work done

## 2026-08-08T16:24+02:00 prompt

> the recap that i mention in the last rule should be short, like a couple of sentences. Just to get an idea of what was done. Plus i want to add some visual representation where we are on the roadmap. Something simple not like tables but like or a gant that can be printed in console jsut ot get an idea what's next and what was done

## 2026-08-08T16:35+02:00 prompt

> wher we are in the plan?

## 2026-08-08T16:37+02:00 prompt

> ok execute all the remainning steps then run an audit

## 2026-08-08T22:24+02:00 prompt

> what is left of the plan?

## 2026-08-08T22:24+02:00 prompt

> execute all of them one after the other without interruption

## 2026-08-08T23:38+02:00 prompt

> perform an adversarial check of the latest development

### recap 2026-08-09  audit run 4 and triage

Fourth adversarial run, spawned clean per DEC-036 with only the report path, the
commit 2b8bfac, the type, and the scope boundary.

- Report: adocs/audit/2026-08-08_adversarial.4.md, seven findings, one high,
  four medium, two low. Baseline before any of them: 376 tests OK, --validate
  all checks pass.
- The eight findings of 2026-08-08_adversarial.3 no longer reproduce and moved
  to closed. The reviewer also reverted twelve S050..S087 behaviours one line at
  a time and ran the suite against each; all twelve were caught, so none of
  those tests is vacuous.
- Seven steps created, one per finding: S088 closes .4-F01, S089 F02, S090 F03,
  S091 F04, S092 F05, S093 F06, S094 F07. The seven findings moved to planned.
- plan.md reordered: the seven correctness steps go ahead of S059, which is
  release verification and now runs last.
- DEC-035's stopping rule does not fire: one high and four medium.
- Files: adocs/audit/2026-08-08_adversarial.4.md (new),
  adocs/audit/2026-08-08_adversarial.3.md (statuses), adocs/plan.md,
  adocs/plan_todo/S088..S094 (new), adocs/status.md.
- No tests added; no code changed. Suite green at 376 tests.

## 2026-08-09T00:36+02:00 prompt

> I peformed the command command line claude plugin install moltke@moltke on claude code cli

## 2026-08-09T00:37+02:00 prompt

> I peformed the command command line claude plugin install moltke@moltke on claude code cli

## 2026-08-09T00:40+02:00 prompt

> whats next?

## 2026-08-09T00:42+02:00 prompt

> what's next?

## 2026-08-09T00:44+02:00 prompt

> it is not clear to me what are you doing. Should i do something or you will do the necessary tests?

## 2026-08-09T00:47+02:00 prompt

> go

## 2026-08-09T09:50+02:00 prompt

> ok so what's next?

## 2026-08-09T01:20+02:00 recap

S059 complete. The installed plugin is 0.6.0 at gitCommitSha c2e6ad3, this
checkout's HEAD, and the cached bin/moltke.py is byte-identical to the working
tree, so the parked note claiming neither release was ever installed is false and
is removed. All five hook events observed in a live session and recorded verbatim
in adocs/audit/2026-08-09_verification.md. 2026-08-06_adversarial-F02 moves from
planned to closed on a live moltke:adversarial_reviewer spawn: blocked on
adocs/probe_fence_outside.md, permitted on adocs/audit/, both sides seen.

The first Stop refusal found a defect. The gate reported the README and MANUAL
check missing from a stamp that recorded it: parse_step_file (bin/moltke.py:86)
matches per line, so a field's indented continuation lines are discarded and every
field is silently truncated to its first line. The gate was right about what it
could see. Planned as S095 rather than fixed here, since S059 excludes changing
behaviour the live session reveals. The stamp was rewritten as one line, the
convention every plan_done/ file already follows.

Not live-observed: the PostToolUse refusal path, which needs a real invariant
violation in the repository to trigger. Stated as such in the record and in the
stamp; it stays suite-covered.

Files: adocs/audit/2026-08-09_verification.md (new), adocs/audit/2026-08-06_adversarial.md
(F02 planned to closed), adocs/testing.md (7 rows), adocs/status.md, adocs/plan.md,
adocs/plan_todo/S095_multiline_step_fields.md (new),
adocs/plan_done/S059_verify_installed_0_5_0.md (moved from plan_todo via plan_current).
No code changed. Suite 376 OK, --validate green.

## 2026-08-09T11:05+02:00 prompt

> next

## 2026-08-09T01:55+02:00 recap

S088 complete. `--step new` and `--step block` now refuse a short name outside
`[A-Za-z0-9_]+`, before either touches the filesystem. Closes
2026-08-08_adversarial.4-F01.

The name went unchecked into `f"{step_id}_{name}.md"` while STEP_FILE_RE requires
that character set. Red observed: `--step new fix-parser` created
`S004_fix-parser.md`, listed S004 in plan.md, and left `--validate` at exit 0 over
a plan naming an id no visible step file carries — the listed-but-absent half of
INV-3, produced by the tool whose job is to keep those two in step. Worse,
`--step new ../../../escaped` created `S004_../../../escaped.md`, outside the plan
directory entirely.

The check sits in `mode_step`, not inside `step_new`/`step_block`: both write the
plan entry before the step file (S083), so a refusal halfway would leave plan.md
naming a step that does not exist. The name is indexed inside the existing try, so
a missing argument still prints usage rather than raising — pinned by a test.
`--audit new` has refused its type this way since S040 and is the model copied.

Files: bin/moltke.py (STEP_NAME_RE, step_name_problem, mode_step dispatch),
tests/test_s007_step.py (TestStepNameValidation, 7 tests), adocs/testing.md (6 rows),
adocs/specs.md (dated note), README.md (376 to 383), MANUAL.md (both --step rows),
adocs/plan_done/S088_validate_step_names.md, adocs/status.md.
Suite 383 OK, --validate green.

## 2026-08-09T13:14+02:00 prompt

> execute all next steps until my input is required

## 2026-08-09T02:20+02:00 recap

S089 complete. `--step done` and `--step start` refuse when the destination is
already carried by a file with that id. Closes 2026-08-08_adversarial.4-F02.

The completion write is a plain `write_text` into plan_done/. Red observed: with
S003 in both plan_current/ and plan_done/, `--step done S003` reported success and
overwrote the finished step, original `done:` stamp included — history destroyed by
the command whose own success message calls that directory immutable. `--step
start`'s `path.rename` is the same shape, silent on POSIX, and reachable because
locate_step searches plan_todo/ first.

Both checks run before anything is written and before the suite gate spends its
wall clock, which a test pins by asserting the gate's side-effect file never
appears. Both refuse rather than resolve: ids are never reused (DEC-008), so one of
the two files is misnumbered, and choosing which is not the command's call.

Worth recording: the start test first passed for the wrong reason — plan_active_max
refused before any rename could happen, so it proved nothing about clobbering. The
fixture now raises the limit so the rename is what the test reaches.

Files: bin/moltke.py (step_done twin check, step_start twin check),
tests/test_s007_step.py (TestDestinationNeverClobbered, 4 tests),
adocs/testing.md (4 rows), adocs/specs.md (dated note), README.md (383 to 387),
MANUAL.md (--step start and --step done rows),
adocs/plan_done/S089_done_never_clobbers.md, adocs/status.md.
Suite 387 OK, --validate green.

## 2026-08-09T02:50+02:00 recap

S090 complete. INV-1 now reports a `paused_by` naming a step that is in no plan
directory, and `--step unpause <id>` clears it. Closes 2026-08-08_adversarial.4-F03.
DEC-040 records the surface addition and what was rejected.

Red observed: a step in plan_current/ with `paused_by: S999`, no S999 anywhere,
and `--validate` said `moltke: all checks pass`. The step was parked behind work
that did not exist, `--step done` on the parent refused and pointed at S999, and
no `--step` operation reached the field — hand-editing was the only way out.

`unpause` is narrow on purpose: it refuses a pause whose named step exists and
points at completing that one instead. A general unpause would be a way around
INV-1, not a repair. S070's stale-pause path (pauser already in plan_done/) is
unchanged and now pinned by a test.

Two of the five tests were written wrong first: they set `paused_by` with a string
replace against a line the fixture never writes, so they asserted nothing. Both
rebuilt with step_file.

New public operation, so the CLI golden was refreshed — after the specs surface
table and MANUAL carried it, which is the order README requires.

Files: bin/moltke.py (pauser_id, inv_1_active_max, step_unpause, STEP_OPS,
dispatch, usage), tests/test_s003_invariants.py (TestPauserMustExist, 5 tests),
tests/golden/cli_surface.txt, adocs/decisions.md (DEC-040), adocs/testing.md (5 rows),
adocs/specs.md (dated note plus surface table row), README.md (387 to 392),
MANUAL.md (--step unpause row), adocs/plan_done/S090_paused_by_must_exist.md,
adocs/status.md.
Suite 392 OK, --validate green.

## 2026-08-09T03:15+02:00 recap

S091 complete. `--scaffold` and `--decline` refuse with exit 1 instead of raising,
and a failed scaffold leaves nothing half-applied. Closes 2026-08-08_adversarial.4-F04.

Red observed on all three: an unwritable directory produced
`PermissionError: [Errno 13] Permission denied: '.../readonly/.moltke.json'` with a
full traceback on stderr, from both modes, against a MANUAL paragraph claiming no
mode ends in a traceback since 0.6.0. With `adocs` present as a regular file the
marker was written first and then `FileExistsError: [Errno 17] File exists` landed
partway through, leaving an enabled `.moltke.json` over a tree that was never built.

Both modes are dispatched before main's backstop and have to be — that backstop runs
after the marker gate they exist to create — so each guards its own writes. The
scaffold rollback removes only what the failing run created, which is safe because
scaffolding never overwrites; anything that could not be removed is named in the
refusal rather than left silent.

The permission tests skip with a message under root instead of passing silently.

Files: bin/moltke.py (mode_scaffold try/rollback, mode_decline guard),
tests/test_s006_scaffold.py (TestSetupModesRefuseInsteadOfRaising, 4 tests, os import),
adocs/testing.md (5 rows), adocs/specs.md (dated note), README.md (392 to 396),
MANUAL.md (no-traceback paragraph), adocs/plan_done/S091_setup_modes_refuse.md,
adocs/status.md.
Suite 396 OK, --validate green.

## 2026-08-09T03:35+02:00 recap

S092 complete. `git_prefix` is computed once per root and cached. Closes
2026-08-08_adversarial.4-F05.

Red observed: 29 `git rev-parse --show-prefix` spawns for one run_checks over a
fixture with eight completed steps. On this repository it was 257, on every prompt,
through the Stop and post-write hooks, for an answer that cannot change while a run
is in flight.

Measured against the stashed working tree: `--validate` 9.54s to 0.72s, `--stop`
9.79s to 0.78s.

The cache key is the root, so a process checking two roots still asks once for each.
S081's monorepo behaviour — what the prefix exists for — is unchanged and green.

The test asserts at least one prefix lookup before asserting the count, so a fixture
without git history cannot pass by abstaining.

Files: bin/moltke.py (_GIT_PREFIX_CACHE, git_prefix),
tests/test_s003_invariants.py (TestGitPrefixIsComputedOncePerRoot, 1 test),
adocs/testing.md (4 rows), adocs/specs.md (dated note with the measurements),
README.md (396 to 397), adocs/plan_done/S092_cache_git_prefix.md, adocs/status.md.
MANUAL checked, no change: the caching is invisible at the surface it documents.
Suite 397 OK, --validate green.

## 2026-08-09T03:55+02:00 recap

S093 complete. INV-8's high-water-mark violation now prints the git blob spec
rather than the root-relative path. Closes 2026-08-08_adversarial.4-F06.

Red observed: `git show 7fee078b:adocs/decisions.md` answered
`fatal: path 'packages/foo/adocs/decisions.md' exists, but not 'adocs/decisions.md'`.
S081 threaded the top-level prefix through every other reader of decisions.md and
missed this one message; the deletion message beside it was already correct, which
is what made the gap easy to miss.

One word, `spec` for `rel`. The second test holds the ordinary case where the marked
root is the git top level, so an unconditional prefix would fail it.

Files: bin/moltke.py (inv_8_append_only high-water-mark message),
tests/test_s003_invariants.py (TestInv8HighWaterMarkRemedyResolves, 2 tests),
adocs/testing.md (3 rows), adocs/specs.md (dated note), README.md (397 to 399),
adocs/plan_done/S093_inv8_remedy_path.md, adocs/status.md.
MANUAL checked, no change: it does not quote this message.
Suite 399 OK, --validate green.
