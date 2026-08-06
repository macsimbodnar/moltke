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
