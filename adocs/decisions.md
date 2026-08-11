# Decisions

Compacted (S106, DEC-042): ids stable, never reused, newest last. Full context and rejected options live in this file's git history.

## Index

- DEC-001 2026-08-01 — Package as a plugin, not a loose skill
- DEC-002 2026-08-01 — Repository is public, with an explicit version field
- DEC-003 2026-08-01 — AGENTS.md is the single source of truth for the rules
- DEC-004 2026-08-01 — The workflow directory is project/, not agents/
- DEC-005 2026-08-01 — Marker file .workflow.json at target repo root
- DEC-006 2026-08-01 — Enforcement is blocking, gated on the marker
- DEC-007 2026-08-01 — plan_current/ is a stack, not a set
- DEC-008 2026-08-01 — Step ids are stable and never renumbered
- DEC-009 2026-08-01 — status.md added; ideas.md and history/ rejected
- DEC-010 2026-08-01 — The public-surface golden test is mandatory
- DEC-011 2026-08-01 — worklog.md is forensic, never a context source
- DEC-012 2026-08-01 — This repository self-hosts the workflow
- DEC-013 2026-08-01 — decisions.md orders oldest first, newest appended at bottom
- DEC-014 2026-08-01 — GitHub configuration is Max's own; agent git surface is commits only
- DEC-015 2026-08-01 — Project renamed to moltke
- DEC-016 2026-08-01 — Build moltke rather than adopt an existing tool
- DEC-017 2026-08-01 — Setup modes are exempt from the INV-11 marker gate
- DEC-018 2026-08-01 — Cursor pointer kept thin; Cursor reads AGENTS.md natively
- DEC-019 2026-08-01 — S010 narrowed to what the agent can verify; install checks become S012
- DEC-020 2026-08-01 — The plugin ships this repository's own workflow state
- DEC-021 2026-08-02 — The workflow directory is renamed project/ to adocs/
- DEC-022 2026-08-06 — The reviewer's write fence gives way to post-hoc reconciliation
- DEC-023 2026-08-06 — --step done gains an optional test_command gate
- DEC-024 2026-08-06 — Worklog secrets are detected in the suite, never redacted at write time
- DEC-025 2026-08-06 — worklog.md drops out of INV-8; decisions.md keeps append-only
- DEC-026 2026-08-07 — A committed immutability violation clears when the content is restored
- DEC-027 2026-08-07 — INV-8 judges one fixed baseline, and the gap that leaves is accepted for now
- DEC-028 2026-08-07 — INV-8 tracks a high-water mark of legitimate content
- DEC-029 2026-08-07 — The Stop waiver counts retries within a turn, derived from the worklog rather than from an unobserved payload field
- DEC-030 2026-08-07 — moltke defends against drift and forgetting, not against a hostile author
- DEC-031 2026-08-07 — No deadlock cap without git, accepted and scoped
- DEC-032 2026-08-07 — The worklog secret check becomes an invariant, so it travels
- DEC-033 2026-08-08 — A report may not hide a finding it names, checked by heading rather than by fence
- DEC-034 2026-08-08 — Release 0.5.0, close the .2 findings by re-running, and stop planning after that
- DEC-035 2026-08-08 — The audit loop stops when a re-run finds nothing above low
- DEC-036 2026-08-08 — The auditor runs on a clean context: red team, blue team, no handover
- DEC-037 2026-08-08 — Every unit of work ends with a short console recap
- DEC-038 2026-08-08 — The console recap is two sentences, and the roadmap is drawn by the tool
- DEC-039 2026-08-08 — The Stop cap exists wherever moltke can write its state, not wherever git is
- DEC-040 2026-08-09 — A stranded pause is cleared by its own command, not by hand
- DEC-041 2026-08-09 — The audit loop stops here, by decision rather than by severity
- DEC-042 2026-08-11 — Memory is current state; git is the archive


## DEC-001  2026-08-01  Package as a plugin, not a loose skill
Decision: plugin in a git repo, installed via marketplace.

## DEC-002  2026-08-01  Repository is public, with an explicit version field
Decision: public repository, explicit `version` in `plugin.json` so updates require a deliberate bump, branch protection on `main`, 2FA on the account, no blind PR merges.

## DEC-003  2026-08-01  AGENTS.md is the single source of truth for the rules
Decision: rules live in `AGENTS.md` at the target repo root; `CLAUDE.md` contains only `@AGENTS.md`; Cursor gets a thin `.cursor/rules` pointer.

## DEC-004  2026-08-01  The workflow directory is project/, not agents/
Decision: `project/`.

## DEC-005  2026-08-01  Marker file .workflow.json at target repo root
Decision: `.workflow.json` at root carries `schema`, `enabled`, `plan_active_max`, `plan_stack_max`, `surface_guard`.

## DEC-006  2026-08-01  Enforcement is blocking, gated on the marker
Decision: hooks block rather than warn, but only in marked repositories.

## DEC-007  2026-08-01  plan_current/ is a stack, not a set
Decision: blocking discoveries are promoted as children with `blocks:` and `paused_by:` links; `plan_active_max` non-paused steps (default 1), `plan_stack_max` total depth (default 3).

## DEC-008  2026-08-01  Step ids are stable and never renumbered
Decision: `S<nnn>_short_name.md` allocated in creation order; plan order lives only in `plan.md`.

## DEC-009  2026-08-01  status.md added; ideas.md and history/ rejected
Decision: keep `status.md` (session pointer, rewritten in place).

## DEC-010  2026-08-01  The public-surface golden test is mandatory
Decision: a golden test over whatever `surface_guard` names, failing until MANUAL and specs are updated in the same commit.

## DEC-011  2026-08-01  worklog.md is forensic, never a context source
Decision: agents never read `worklog.md` to determine state or reasoning.

## DEC-012  2026-08-01  This repository self-hosts the workflow
Decision: `max_agent_workflow` is the first project to use the workflow, with `bootstrap.md` becoming its `project/specs.md` and this build becoming its first plan.

## DEC-013  2026-08-01  decisions.md orders oldest first, newest appended at bottom
Decision: newest last.

## DEC-014  2026-08-01  GitHub configuration is Max's own; agent git surface is commits only
Decision: Max handles GitHub configuration personally: visibility, remotes, branch naming and protection, pushes, app installs.

## DEC-015  2026-08-01  Project renamed to moltke
Decision: full rename: plugin and repository `moltke`; skills `init`, `step`, `audit` (commands /moltke:init, /moltke:step, /moltke:audit); CLI `bin/moltke.py`; marker `.moltke.json`; template `templates/moltke.json`.

## DEC-016  2026-08-01  Build moltke rather than adopt an existing tool
Decision: proceed with moltke as planned.

## DEC-017  2026-08-01  Setup modes are exempt from the INV-11 marker gate
Decision: INV-11 applies to every mode except the setup modes `--scaffold` and `--decline`, which run before the gate.

## DEC-018  2026-08-01  Cursor pointer kept thin; Cursor reads AGENTS.md natively
Decision: scaffold a minimal always-applied `.cursor/rules/moltke.mdc` that points at `AGENTS.md` and states no rules of its own.

## DEC-019  2026-08-01  S010 narrowed to what the agent can verify; install checks become S012
Decision: S010 covers what is mechanically verifiable without changing any environment: the manifest, the marketplace entry, component discoverability, and `claude plugin validate --strict`.

## DEC-020  2026-08-01  The plugin ships this repository's own workflow state
Decision: keep the layout and record the consequence as a known issue in MANUAL rather than restructuring.

## DEC-021  2026-08-02  The workflow directory is renamed project/ to adocs/
Decision: rename the directory to `adocs/` everywhere — scaffold output, every path in `bin/moltke.py`, the hook messages, the templates, the rules, the tests, and this repository's own state.

## DEC-022  2026-08-06  The reviewer's write fence gives way to post-hoc reconciliation
Tags: audit, reviewer, enforcement, hooks
Decision: mutation during an audit is legitimate — the reviewer needs to create tests and reproduce defects, and git is the backstop. Prevention gives way to detection. `--audit new` records a working-tree baseline; a new `--audit check` reports what the run actually changed and flags anything beyond this run's report and new files under `tests/`.
Why: the 2026-08-06 adversarial audit found (F03) that `adversarial_reviewer` holds `Bash` alongside `Write` while the fence is a `Write|Edit` PreToolUse matcher, so any shell redirect writes anywhere in the repository.

## DEC-023  2026-08-06  --step done gains an optional test_command gate
Tags: testing, cli, marker, enforcement
Decision: add an optional `test_command` key to `.moltke.json`. When present, `--step done` runs it and refuses on a non-zero exit, naming the failure. When absent, behaviour is exactly as today and the refusal path says the gate is not configured.
Why: the 2026-08-06 adversarial audit found (F07) that AGENTS.md section 4 and section 11 require a full green suite before a step completes, while `--step done` checks only that a `testing.md` row exists and that the stamp mentions README and MANUAL.

## DEC-024  2026-08-06  Worklog secrets are detected in the suite, never redacted at write time
Tags: security, worklog, testing, invariants
Decision: detect, do not redact. A suite test fails when a prefixed key shape or a PEM private-key header appears in the worklog, and it is non-vacuous by construction: it first asserts a known-bad fixture string is caught. MANUAL records the exposure and the escape procedure for a real leak — a decisions.md entry authorising a one-time redaction, exactly as DEC-013 authorised a one-time reorder.
Why: the 2026-08-06 adversarial audit found (F08) that `--log-prompt` writes every prompt verbatim into `adocs/worklog.md`, a tracked file, and INV-8 then forbids altering earlier bytes — so a pasted secret is committed and cannot be removed without violating the workflow's own invariant, while AGENTS.md section 11 bars rewriting history outright.

## DEC-025  2026-08-06  worklog.md drops out of INV-8; decisions.md keeps append-only
Tags: worklog, invariants, immutability, decisions
Decision: narrow INV-8 to `decisions.md` alone. The worklog stays append-only by convention and is no longer checked, so it can be trimmed, corrected, or redacted without violating anything. `decisions.md` keeps enforcement because `DEC-<nnn>` ids are cited from code comments, commit messages, `specs.md`, and step files, and a rewritten entry silently changes what every one of those citations means.
Why: INV-8 covers `adocs/worklog.md` and `adocs/decisions.md` in one rule, and AGENTS.md section 11 bars rewriting either.

## DEC-026  2026-08-07  A committed immutability violation clears when the content is restored
Tags: invariants, immutability, git, audit
Decision: the invariants judge current content against history, not the existence of a bad commit. A `plan_done/` file is clean when its bytes match the version at the commit that added it; `decisions.md` is clean when its current content still starts with every version it has ever had. Restoring what was removed, in a new commit, therefore clears the violation, and leaving it tampered keeps reporting it.
Why: the 2026-08-07 adversarial audit found (F03) that S018's history baselines gave INV-7 and INV-8 no legal terminal state.

## DEC-027  2026-08-07  INV-8 judges one fixed baseline, and the gap that leaves is accepted for now
Tags: invariants, immutability, git, decisions
Decision: INV-8's history check compares the current content against one fixed baseline, the version at the file's first commit, exactly as INV-7 compares against the version at the commit that added the file. Restoring the baseline content clears it; leaving it rewritten keeps reporting it. The HEAD comparison for the uncommitted window is unchanged.
Why: DEC-026 chose "a repair commit clears it" and described INV-8 as "current content still starts with every version it has ever had".

## DEC-028  2026-08-07  INV-8 tracks a high-water mark of legitimate content
Tags: invariants, immutability, git, decisions
Decision: INV-8 walks the versions oldest first and maintains a high-water mark: a version that still contains, in order, every line the mark requires becomes the new mark, and a version that dropped something is a tampering and is skipped rather than becoming the mark. The file as it stands must then contain the mark's lines, in order. Restoring the text puts the mark back and clears the whole history at once; a removal, an in-place rewrite, and a line moved to the end are each caught, because in every one of them a required line is no longer in order.
Why: DEC-027 settled INV-8 on one fixed baseline, the first committed version, and accepted a measured gap: a rewrite of text appended after that commit was reported while uncommitted and not once committed.

## DEC-029  2026-08-07  The Stop waiver counts retries within a turn, derived from the worklog rather than from an unobserved payload field
Tags: hooks, stop, invariants, deadlock
Decision: the waiver counts retries within one turn, and "the same turn" is `prompt_id` and `session_id` when the payload carries them, plus the number of prompt headings in `adocs/worklog.md`, which `UserPromptSubmit` advances exactly once per turn. The count also resets when the set of problems changes, so making partial progress does not spend attempts. The waived turn prints the problems before allowing the stop.
Why: the 2026-08-07 re-run found (.2-F01) that the deadlock waiver counted consecutive blocks per `prompt_id`, a Stop payload field nothing in this repository establishes exists.

## DEC-030  2026-08-07  moltke defends against drift and forgetting, not against a hostile author
Tags: scope, principle, invariants, security, triage
Decision: the threat model is accident and drift, not malice. Checks exist to stop an agent forgetting, contradicting a decision, or letting documentation diverge from code — not to make tampering impossible for someone with a shell and intent. Where those two goals conflict, the simpler behaviour wins, and the documentation is corrected to describe what actually runs rather than the code being grown to match an aspirational sentence.
Why: the 2026-08-07 re-runs produced a class of findings about what a determined author could get past the checks — a forged decision entry inserted mid-file (.2-F07), the reviewer appending to the worklog through Bash (.2-F09), the fence boundary at the repository edge (.2-F10).

## DEC-031  2026-08-07  No deadlock cap without git, accepted and scoped
Tags: hooks, stop, invariants, git, scope
Decision: accept the gap and scope the property to repositories with git. A repository without git is already outside most of what moltke does: INV-7 and INV-8 abstain there, `--audit check` refuses, and the prompt-failure breadcrumb has nowhere to go. Adding a state file outside the repository to serve that one case is the first thing moltke would keep outside the project, and it is not worth it.
Why: the 2026-08-07 re-run found (.2-F06) that a marked repository with no git at all has no `Stop` deadlock cap: the counter lives beside the git directory, there is none, so every `Stop` blocks and the agent cannot end its turn.

## DEC-032  2026-08-07  The worklog secret check becomes an invariant, so it travels
Tags: security, worklog, invariants, distribution
Decision: the shapes move into `bin/moltke.py` and run as an invariant, so `--validate` reports them and the `Stop` hook refuses on them, in every marked repository. The suite test stays and imports the shapes, so the detector keeps exactly one definition and its non-vacuity guard — each shape asserted against its own example before anything is scanned — keeps covering the version that ships. (Max, choosing from agent-supplied options.)
Why: DEC-024 chose detection over redaction and S022 built it as `tests/test_s022_secrets.py`.

## DEC-033  2026-08-08  A report may not hide a finding it names, checked by heading rather than by fence
Tags: audit, invariants, fences, evidence
Decision: add INV-14, which compares the `### <id>` headings a report states in its raw text against the ones that survive `strip_guidance`, scoped to the report's own stem. A heading naming this file's own report that no scanner can read is a violation, whatever the markers around it meant. It runs in `--post-write` as well, so the reviewer learns on save.
Why: S033 closed one half of 2026-08-07_adversarial-F02 and recorded the other as unresolvable: two unclosed fences are two markers, so they pair as one closed fence, the count stays even, INV-13 is silent, and the finding between them is stripped before INV-10 or `--audit list` sees it.
Findings: 2026-08-07_adversarial-F02

## DEC-034  2026-08-08  Release 0.5.0, close the .2 findings by re-running, and stop planning after that
Tags: release, audit, plan, versioning
Decision: one step bumps to 0.5.0 and re-runs the audit, closing every finding the re-run no longer reports; a second, separate step verifies the installed 0.5.0 in a live session, since that can only happen after Max reinstalls the plugin. Nothing is planned beyond those two: the plan stops empty on purpose, and the next input is real use rather than invented work. 0.5.0 rather than 0.4.1 because INV-15 turns on a new blocking check in every repository that installs the plugin and S028/S029 change what `init` does, neither of which is a patch. (Max, choosing from agent-supplied options.)
Why: the plan emptied: all 55 steps are in `plan_done/` and `plan.md` has nothing after them.

## DEC-035  2026-08-08  The audit loop stops when a re-run finds nothing above low
Tags: audit, process, stopping, drift
Decision: when a re-run reports no `high` and no `medium` finding, the loop stops. The lows are recorded in the report as always and then discharged as `accepted` by a decision entry rather than planned one step each, and no further audit is scheduled: the next input becomes real use in another repository, per DEC-034. A regression introduced by the batch being audited does not count towards continuing either — it is fixed, but it is evidence that the batch was wrong, not that the codebase has more to give.
Why: four adversarial runs have produced 14, 11, 10, 6 and now 12 findings, and each release triggers the next re-run because §10 closes a finding only on evidence.

## DEC-036  2026-08-08  The auditor runs on a clean context: red team, blue team, no handover
Tags: audit, process, bias, subagent
Decision: the auditor is spawned with a clean context and learns the repository only from the repository. The spawning prompt carries the report path, the commit, the type of audit, and the scope boundary — nothing about what changed, what the session believes, what to prioritise, or which findings it expects. Verdicts on prior findings stay in scope, because those live in the tracked reports the auditor reads for itself.
Why: the reviewer has always been a separate subagent, but the prompt spawning it was written by the session that had just done the work.

## DEC-037  2026-08-08  Every unit of work ends with a short console recap
Tags: process, output, worklog
Decision: after every completed unit of work — a step reaching `plan_done/`, a planning session, an audit run — the agent prints a short recap to the console: what was done, what changed, what proves it, and the commit sha. Short means a handful of lines, not a report. It is additional to the worklog recap, not a replacement, and it is the agent's own output rather than something the tool prints.
Why: the worklog gets a recap on every work turn (§9) and the user gets whatever the agent chooses to write at the end of a turn, which has ranged from one line to several screens.

## DEC-038  2026-08-08  The console recap is two sentences, and the roadmap is drawn by the tool
Tags: process, output, roadmap, cli
Decision: the recap narrows to a couple of sentences: what was done and what it means, no more. Anything longer is a report and is written when asked for. The roadmap becomes a `--roadmap` mode in `bin/moltke.py`, printed after the recap, rendering the plan as one timeline strip with the current step named beneath it.
Why: DEC-037 asked for a short console recap and defined short as "a handful of lines, not a report".

## DEC-039  2026-08-08  The Stop cap exists wherever moltke can write its state, not wherever git is
Tags: hooks, stop, invariants, state, scope
Decision: the crash is a defect and is fixed — nothing in `mode_stop` may raise, the problems are printed before anything that can fail, and a state write that fails says so in its own words. The missing cap is not a defect: DEC-031 already weighed this exact trade for a repository with no git and accepted it, so the property is scoped to "wherever moltke can write its state beside the git directory" rather than "wherever git is". An unwritable `.git` gets the same treatment as no git at all: every `Stop` blocks until the problem is fixed, with correct and actionable messages behind it, and the message names the missing cap so nobody has to work out why the waiver never came.
Why: 2026-08-08_adversarial.3-F01: the retry state write is the one unguarded write in `mode_stop`, so with `.git` unwritable the `OSError` escaped to `main`'s backstop, which returns before the problems are printed and before the cap is consulted.
Findings: 2026-08-08_adversarial.3-F01

## DEC-040  2026-08-09  A stranded pause is cleared by its own command, not by hand
Tags: plan, cli, invariants
Decision: Report it from INV-1, and add --step unpause <id> as the way out. The violation names the step, the missing pauser, and that command. unpause is narrow: it clears a pause whose named step is in no plan directory and refuses one whose step exists, pointing at --step done on the pauser instead. Agent-proposed, from the options the finding itself listed; Max approves the surface addition by accepting this step's plan.
Why: 2026-08-08_adversarial.4-F03.
Findings: 2026-08-08_adversarial.4-F03

## DEC-041  2026-08-09  The audit loop stops here, by decision rather than by severity
Tags: audit, process, release
Decision: Stop auditing. 0.8.0 is bumped at a green tree — 444 tests, --validate exit 0, --audit list exit 0, --audit check exit 0 — and the project is declared complete and stable until new orders. Max's decision; the agent supplied the state above and the cost below.
Why: DEC-035 ends the audit loop when a re-run reports no high and no medium.

## DEC-042  2026-08-11  Memory is current state; git is the archive
Tags: context, documents, invariants, philosophy
Decision: The always-read documents hold current state only and are bounded by construction. History lives in git and in plan_done/, which are never read into context. Concretely: INV-8 is retired (number never reused); decisions.md is compacted freely with stable ids; specs.md carries current wording only, the narrative living in step stamps and commit messages; worklog.md is trimmable; --step done prunes plan.md to the last 5 completed entries.
Why: The token analysis measured the always-read set at ~180 KB and growing 1.4 KB per completed step without bound, with 84% of specs.md being dated history notes and decisions.md unshrinkable because INV-8 enforced append-only.

## DEC-044  2026-08-11  Review has three tiers: fast check by habit, audit by consent
Tags: review, audit, process
Decision: After every completed step, one small subagent reviews that step's diff — no report file, no finding ids; trivial findings fixed on the spot, real ones become steps. A full adversarial audit runs when the user asks, or when the user accepts an agent proposal made on real risk; postponed proposals park as one status.md line. Findings close on a re-run or by recorded decision, so the loop always has a user-controlled end; the reviewer fence and clean-context rule keep binding actual audit runs.
Why: mandatory full audits produced an endless loop (DEC-041 stopped it by hand); a per-chunk fast check catches most defects at a fraction of the ceremony.

## DEC-043  2026-08-11  Two override surfaces: machine-local file, project rules section
Tags: context, overrides, local
Decision: .moltke.local.md at the marked root holds machine-local instructions — created by --session-start when absent, excluded through .git/info/exclude rather than .gitignore so the exclusion itself stays uncommitted, injected verbatim into the SessionStart context, never overwritten once it exists. A "## Project rules" section at the end of the scaffolded AGENTS.md holds committed project-specific rule overrides. Precedence: machine over project over base ruleset.
Why: the same repository is developed on machines with different tools and paths, and a project must be able to loosen or harden the shipped rules without forking the template.
