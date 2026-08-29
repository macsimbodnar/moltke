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
- DEC-043 2026-08-11 — Two override surfaces: machine-local file, project rules section
- DEC-044 2026-08-11 — Review has three tiers: fast check by habit, audit by consent
- DEC-045 2026-08-11 — moltke is team-first
- DEC-046 2026-08-11 — The worklog is removed
- DEC-047 2026-08-11 — Fence police retired; stripping stays
- DEC-048 2026-08-11 — Completion ceremony slimmed
- DEC-049 2026-08-18 — Watchers arm only through a tested primitive
- DEC-050 2026-08-18 — VOID — watcher work jumped the queue ahead of install verification
- DEC-051 2026-08-18 — Watcher lint scope narrowed against the live Monitor contract
- DEC-052 2026-08-18 — The diverged branches are merged, the newer ids re-issued
- DEC-053 2026-08-18 — Three of the six 2026-08-18 findings do not survive re-triage
- DEC-054 2026-08-18 — INV-17's arm-time blocker survives the fence retirement
- DEC-055 2026-08-19 — Step ids widen to four digits, and the ceiling moves with them
- DEC-056 2026-08-19 — SUPERSEDED by DEC-057 — S138 is postponed: the reviewer subagent does not exist in this session
- DEC-057 2026-08-19 — One install per Claude config root, not one per machine
- DEC-058 2026-08-19 — An audit's red-first tests couple the steps that close them, and a claim still cannot be undone
- DEC-059 2026-08-20 — A blank line in a stamp is refused, not reflowed
- DEC-060 2026-08-20 — AGENTS.md §5 drops "lint", rather than gaining a linter
- DEC-061 2026-08-20 — A release reaches the roots the agent can reach, and says which it did not
- DEC-062 2026-08-23 — v1: the workflow is rules, not enforcement
- DEC-063 2026-08-23 — Project rules are interview answers, recorded per repository
- DEC-064 2026-08-23 — The migration prompt is an operator note in adocs/, not shipped documentation
- DEC-065 2026-08-29 — Machine-local Claude configuration is scrubbed from the living documents, and history is left alone
- DEC-066 2026-08-29 — Seventeen 0.x audit findings close by retirement of their target, named here
- DEC-067 2026-08-29 — The stale machine-local notes file is the operator's to fix, not a plan step


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

## DEC-043  2026-08-11  Two override surfaces: machine-local file, project rules section
Tags: context, overrides, local
Decision: .moltke.local.md at the marked root holds machine-local instructions — created by --session-start when absent, excluded through .git/info/exclude rather than .gitignore so the exclusion itself stays uncommitted, injected verbatim into the SessionStart context, never overwritten once it exists. A "## Project rules" section at the end of the scaffolded AGENTS.md holds committed project-specific rule overrides. Precedence: machine over project over base ruleset.
Why: the same repository is developed on machines with different tools and paths, and a project must be able to loosen or harden the shipped rules without forking the template.

## DEC-044  2026-08-11  Review has three tiers: fast check by habit, audit by consent
Tags: review, audit, process
Decision: After every completed step, one small subagent reviews that step's diff — no report file, no finding ids; trivial findings fixed on the spot, real ones become steps. A full adversarial audit runs when the user asks, or when the user accepts an agent proposal made on real risk; postponed proposals park as one status.md line. Findings close on a re-run or by recorded decision, so the loop always has a user-controlled end; the reviewer fence and clean-context rule keep binding actual audit runs.
Why: mandatory full audits produced an endless loop (DEC-041 stopped it by hand); a per-chunk fast check catches most defects at a fraction of the ceremony.

## DEC-045  2026-08-11  moltke is team-first
Tags: team, plan, invariants
Decision: Branch-per-member is the assumed topology, a shared branch possible. The plan is common: steps are created unowned and claimed at --step start, which stamps author: from git config user.name; INV-1's active limit counts per author. Merge semantics ship with the scaffold (.gitattributes: union for testing.md, ours for status.md which is regenerated); step-id collisions at merge stay INV-6-caught with a merge-aware remedy. Windows is out of scope, documented.
Why: Max: the tool should be built with a team in mind, not a solo dev.

## DEC-046  2026-08-11  The worklog is removed
Tags: worklog, hooks, privacy
Decision: Verbatim prompt logging, the UserPromptSubmit hook, the recap gate, INV-15, and the log-failure breadcrumbs are removed. The Stop cap re-keys to a per-fingerprint retry count in .git/ state. Forensic history is git; recaps live in the console and in commit messages.
Why: highest bug density in the design, a privacy leak and merge-conflict machine for teams, all for a file the rules forbade reading.

## DEC-047  2026-08-11  Fence police retired; stripping stays
Tags: fences, invariants
Decision: INV-13, INV-14, and INV-16 are retired like INV-8. strip_guidance keeps stripping fenced content from id-scanners so quoting stays safe; nothing blocks on fence counts anymore. An unclosed fence can hide content from scanners silently — accepted under DEC-030's drift-not-malice threat model.
Why: the police generated ~15 findings across six audits and trained workarounds; blockers users fight get routed around.

## DEC-048  2026-08-11  Completion ceremony slimmed
Tags: step, testing, ceremony
Decision: The completion stamp stays required but is free text: multi-line accepted and written as indented continuations, no README/MANUAL substring check. INV-5 reduces to stamp-present. testing.md rows are voluntary documentation, pruned with the same last-5 window as plan.md.
Why: substring gates verified mention, not truth, and trained formula; the one-line rule produced unreadable 1.4 KB stamps.

## DEC-049  2026-08-18  Watchers arm only through a tested primitive
Tags: watcher, monitor, background, leak, cli, hooks
Decision: moltke ships `bin/moltke.py --watch LOG REGEX --ceiling DUR [--pid P] [--fail-re RE] [--interval DUR]` with four self-terminating exits: 0 marker seen, 4 failure marker, 3 watched pid died, 124 ceiling. It scans the whole file each poll, so a marker written before arming is still caught, and registers under `.git/moltke_watch/`, writing its outcome on every exit path; acknowledging an outcome is deleting the record. A PreToolUse lint refuses persistent watcher arms that are not the primitive. Rules live in AGENTS.md §12; the shell poll loop is the fallback where the tool is absent.
Why: overnight runs leaked hand-composed `tail -f | grep` monitors that cannot exit, and a prose rule had already failed under habit — the cause is improvised infrastructure plus an obligation recorded nowhere in the filesystem.
Re-issued 2026-08-18 under DEC-052: minted as DEC-022 on the merged branch, which is a different decision here. Context and rejected options are in that branch's history.

## DEC-050  2026-08-18  VOID — watcher work jumped the queue ahead of install verification
Tags: plan, order
Decision: VOID 2026-08-18, superseded by DEC-052. It ordered the merged branch's plan so the watcher steps ran before install verification, and demoted that step to `plan_todo/` by hand. The ids it names mean other work here, and install verification completed long before the merge.
Why: kept because a void entry is never deleted, and because it records the one-time by-hand demotion the step tool has no operation for.
Re-issued 2026-08-18 under DEC-052: minted as DEC-023 on the merged branch.

## DEC-051  2026-08-18  Watcher lint scope narrowed against the live Monitor contract
Tags: watcher, monitor, hooks
Decision: Narrows DEC-049. Block any single-match follow (`tail -f | grep -m N`), bounded or not, since SIGPIPE never arrives on a log that has stopped being written. Block a persistent arm that is not the primitive unless its command carries MOLTKE_UNBOUNDED_OK. Allow bounded streams: an unbounded follow through a filter is Monitor's own documented pattern for per-occurrence events, and a non-persistent arm is already bounded by the harness cap. The blessed overnight form is a persistent arm of the primitive, whose `--ceiling` is then its real timeout.
Why: an unconditional block would fight designed, bounded usage, and false positives corrode a lint until someone disables it.
Re-issued 2026-08-18 under DEC-052: minted as DEC-024 on the merged branch.

## DEC-052  2026-08-18  The diverged branches are merged, the newer ids re-issued
Tags: git, plan, merge, ids
Decision: (Max, chat 2026-08-18: merge them, review, replan; agent-supplied analysis) The branch that continued from the adocs rename with a watcher primitive is merged into the line that reached 0.11.0, keeping both bodies of work. The 0.11.0 line's code, rules, and numbering win every conflict; the other contributes `--watch` and its arm-time lint. Everything minted in a namespace that branch could not see is re-issued: steps S014→S129 and S015→S130, DEC-022/023/024→DEC-049/050/051, INV-13→INV-17, and its two test files renamed to match. `adocs/worklog.md` is deleted with the subsystem (DEC-046) rather than carried across. `plugin.json` goes to 0.12.0, because 0.11.0 is installed already and this adds public surface. The branch `watch-primitive-a304293` holds the pre-merge tip, worklog included.
Why: that branch audited and extended a 136-commit-stale tree, so its ids collided with released ones and half its findings were already answered here; merging is what preserves the watcher work, and re-issuing is the collision remedy the Teams section already prescribes.

## DEC-053  2026-08-18  Three of the six 2026-08-18 findings do not survive re-triage
Tags: audit, findings, merge
Decision: F01 is accepted, not fixed: it rests on a documented field name, and the running Claude Code builds the UserPromptSubmit payload with `prompt` at both call sites — the only `user_prompt` key in that binary is a telemetry span attribute. The mode it targets no longer exists in any case (DEC-046). F03 is accepted: the reviewer write fence already gave way to post-hoc reconciliation (DEC-022) and the fence police are retired (DEC-047), so an unfenced Bash tool is the chosen design, not an oversight. F05 is accepted as already fixed: renames reach both Stop gates through `porcelain_paths` since S050, and the README/MANUAL substring gate it targeted is gone (DEC-048). F02, F04 and F06 stand against the merged code and carry steps.
Why: an audit against a stale tree re-finds fixed bugs and misses the decisions that answered them; recording which findings died, and why, is what stops them being re-derived.

## DEC-054  2026-08-18  INV-17's arm-time blocker survives the fence retirement
Tags: watcher, monitor, hooks, invariants, fences
Decision: (Max, chat 2026-08-18, from agent-supplied options) INV-17 stays a blocker. `--pre-command` keeps refusing at arm time, and `MOLTKE_UNBOUNDED_OK` stays the one escape. DEC-047 does not reach it: that entry retired checks that were wrong and kept the part that worked, and this check has a paved road to point at, was already narrowed against false positives by DEC-051, and refuses a process that outlives the session rather than text hidden from a scanner. Downgrading it to a warning was rejected against DEC-006, which chose blocking over warning as the house style and left the tool no advisory precedent to follow. 2026-08-18_adversarial-F04, re-read under this outcome, stands unchanged at `planned` and is S134's to close: the incidental substring `moltke --watch` is an undocumented second escape that fires by accident, which is a bug in the check rather than evidence the check is unwanted — under DEC-030 drift writes a bare follow, it does not embed the token to get past a gate.
Why: DEC-047's cause was a check that misfired about fifteen times across six audits with no better command to offer; strictness was never the complaint, and one finding is not six.

## DEC-055  2026-08-19  Step ids widen to four digits, and the ceiling moves with them
Tags: plan, ids, invariants
Decision: The recognised step id is three digits or four: `S\d{3,4}`, stated once as `STEP_ID_DIGITS` and reused by every scan that reads an id. `--step new` allocates S1000 after S999 with no ceremony, and refuses past S9999 with the condition named, so the allocator can never mint an id the readers cannot see. An unbounded form (`S\d{3,}`, no ceiling) was rejected: a stray wide token in plan.md prose would then silently push the counter to it, which is the failure S097's refusal exists to make loud, and the refusal is the only thing that keeps writers and readers in step. The id counter is deliberately wider than the readers — any id-shaped filename at any width, any three-or-more-digit token in plan.md — so a width nothing else reads still bumps the counter and lands as the refusal instead of being handed out twice.
Why: allocation and recognition were one rule stated in five places, and at S999 the two ends disagreed silently; a bounded form with a loud edge keeps them one rule.

## DEC-056  2026-08-19  S138 is postponed: the reviewer subagent does not exist in this session
Tags: audit, plugin, agents, skills, plan
Decision: (Max, chat 2026-08-19, from agent-supplied options) S138 is returned to `plan_todo/` unworked, and the merged tree stays unaudited until a session where the plugin's agents load. Observed here: `adversarial_reviewer` is not a spawnable subagent type, under that name or as `moltke:adversarial_reviewer`, and the plugin's skills are absent from the same session's registry — only its hooks are live, and those ran 0.11.0. The agent file is present and well-formed in both the marketplace clone and the 0.12.0 install under `~/.claude/plugins/cache/moltke/moltke/0.12.0/agents/`, so this is a loading question, not a packaging one. Running the audit through `general-purpose` with the role prompt inlined was offered and rejected: the `--pre-write` fence matches on an `agent_type` suffix of `adversarial_reviewer`, so a substitute agent audits unfenced, which is a wider hole than DEC-022 accepted when it left `Bash` unpoliced. Registering the agent under `.claude/agents/` was rejected as unlikely to load mid-session and as untracked repository content the audit baseline would then flag. The stub report `adocs/audit/2026-08-19_adversarial.md` and its baseline in `.git/` are deleted rather than committed: a dated report is evidence of one run, no run happened, and leaving it would push today's real run to a `.2` suffix that implies a second. The move out of `plan_current/` is by hand against §2, because the lifecycle has no un-claim operation — `--step` offers `new`, `start`, `block`, `unpause`, `done`, `status`, and nothing that undoes a claim.
Why: an audit is only evidence if the reviewer arrives cold and fenced, and neither the substitute nor a hand-registered agent gives both; the registry gap is S139's to establish, and postponing costs one unaudited stretch where the alternatives cost the audit's standing.
Superseded by DEC-057: the mechanism was the config root, the postponement is discharged, and S138 runs with the real reviewer.

## DEC-057  2026-08-19  One install per Claude config root, not one per machine
Tags: plugin, install, hooks, agents, skills, docs, watcher
Decision: A moltke install belongs to one Claude config root, and a machine with more than one root needs one install per root. Observed 2026-08-19: a client that sets `CLAUDE_CONFIG_DIR` to a root of its own had no hooks, no skills, and no `moltke:adversarial_reviewer`, because moltke was installed and enabled only in the other root, while a home-directory `CLAUDE.md` still loaded and made the session look configured. `CLAUDE_CONFIG_DIR=<root> claude plugin list` reported the plugin enabled for one root and none installed for the other: one environment variable apart, same binary, same tree. DEC-056 read this correctly as a loading question rather than a packaging one; the mechanism was narrower than it assumed — nothing of the plugin loaded, because the session never read the registry the plugin was in. Installing under the second root discharges that postponement: the reviewer is spawnable and fenced, so S138 runs as designed rather than through a substitute. MANUAL's "Once per machine" is corrected to per config root, and README gains the developer consequence, because a `directory` marketplace source snapshots the whole tree into that root's cache — untracked files included, `.moltke.local.md` among them — so working-tree edits are not what the hooks run until `claude plugin update`. Left unfixed here, as S139 excludes behaviour changes: nothing in a session reports which install is answering, so the same silence returns whenever a root is stale or absent. That becomes its own step.
Why: "once per machine" is false on any machine running both the CLI and the desktop app, and its failure mode is silence rather than an error — the workflow simply stops being enforced while every document still claims it is.

## DEC-058  2026-08-19  An audit's red-first tests couple the steps that close them, and a claim still cannot be undone
Tags: audit, plan, lifecycle, testing, gates
Decision: (Max, chat 2026-08-19, from agent-supplied options) The 2026-08-19 findings F01 and F03 are fixed before the audit lands, rather than the audit landing non-green. Two deviations from §4 follow from the completion gate and are recorded rather than taken silently. First, the gate runs the whole suite, so the first `--step done` in a sequence needs every red test green — including tests belonging to a later step. One reviewer-written file, `tests/test_2026_08_19_adversarial_findings.py`, carries three F01 tests and two F03 tests, so no ordering exists in which S141 completes before F03 is also fixed. Both fixes therefore land before either completion, and each stamp says so; splitting the file would not help, since the gate is the whole suite either way. Bundling both findings into one step was rejected against the audit skill's one-to-one rule, and a blocking child was rejected because `--step block` mints a new id that would duplicate a step the triage already created. Second, S138 is moved from `plan_current/` back to `plan_todo/` by hand so S141 can be claimed at `plan_active_max` 1. That is the same missing operation DEC-056 hit and worked around the same way; the second occurrence makes it a step rather than a footnote.
Why: red-first tests are evidence, and a gate that reads the whole suite makes the steps that own them finish together whether the plan says so or not; naming the coupling costs one entry, and discovering it a third time by hand costs more.

## DEC-059  2026-08-20  A blank line in a stamp is refused, not reflowed
Tags: step, testing, ceremony, docs
Decision: (Max, chat 2026-08-20, from agent-supplied options) DEC-048's free-text multi-line stamp is narrowed: `--step done` refuses a `--stamp` containing a blank line, naming the condition, before anything is written or moved. Multi-line stays accepted and is still written as indented continuations. Teaching `parse_step_file` that an indented whitespace-only line continues a field was rejected: preserving the paragraph break means the fold stops joining continuations with a space, and that fold is shared by `goal:`, `accepts:`, `touches:` and `excludes:` throughout the plan directories, so the blast radius would be every field reader rather than the one field the finding names. The rule counts any blank line, a leading or trailing one included, even though `with_field`'s `rstrip` absorbs a trailing one and a single leading one lands where the `key:` line already ends — two leading ones do not, and a rule that separated the blank line which parses from the blank line which does not would be a second rule with a boundary to get wrong.
Why: a stamp is evidence, so the two honest options were refuse or round-trip and reflowing was never one of them; refusing costs a retype at completion, and round-tripping costs the fold semantics every other multi-line field depends on.

## DEC-060  2026-08-20  AGENTS.md §5 drops "lint", rather than gaining a linter
Tags: rules, gates, testing, ceremony
Decision: (Max, chat 2026-08-20, from agent-supplied options) §5's "build, lint, full suite" becomes "build and the full suite", in `AGENTS.md` and `templates/AGENTS.md` together. There is no lint configuration in the repository, no linter in `test_command`, and none installed, so the word has never checked anything — which is how `def git_dir(root):    return lines`, a definition shadowed three lines later, survived eight days and twenty commits of review (2026-08-19_adversarial-F12). Two alternatives were rejected. A stdlib `ast` self-host check in the suite — redefinitions and doubled assignments, no dependency — would have made a narrower word true, and was declined as more machinery than the defect class earns. `ruff` as a dev dependency was declined as a dependency plus a config file plus a pass over every existing line. The dead definition and the doubled `REVIEWER_AGENT` assignment are deleted in S152 regardless; nothing now stops the next one, and that is the accepted cost.
Why: a rule nothing enforces is worse than no rule, because it reads as a gate at every review and is one at none of them.

## DEC-061  2026-08-20  A release reaches the roots the agent can reach, and says which it did not
Tags: plugin, install, release, docs, git
Decision: (Max, chat 2026-08-20, from agent-supplied options) S155's accepts is amended: 0.13.0 is verified live in the roots an agent can install into, and the roots it cannot are named in MANUAL and in the stamp rather than blocking the release. The accepts assumed every config root takes a release from the checkout. They do not. A root whose marketplace source is a `directory` took 0.13.0 at both its scopes, which the registry is the evidence for — both entries name the 0.13.0 cache, and `--version` reads the manifest beside itself, so it reports that cache's version and cannot say which scope or root is serving it. A root whose source is `git` resolves against `origin/master`, so the bump has to be pushed before that root can see it, and §5 says the agent never pushes; it stayed on 0.12.0 at the commit its cache matches exactly, while master ran well ahead at the same `version`. Counts are not kept here: they decay on the next commit. Pushing before completion was offered and declined; repointing the git-sourced root at the checkout was offered and declined as making the CLI run uncommitted code. Two mechanisms were established live and are written into MANUAL's Install and Known issues sections, because both were stated wrongly or incompletely beforehand. `claude plugin update` compares the manifest `version` and nothing else: against an unbumped checkout it prints `already at the latest version` and copies nothing, cache and `lastUpdated` untouched — so README's and `.moltke.local.md`'s claim that an edit reaches the hooks after an update was false, and both are corrected. The same comparison is why that root's cache never moved while its source branch advanced at an unchanged `version`; the cache is faithful to the commit the install record names, and nothing tracks the branch moving past it. And scope is per install: the first update moved `user` scope only, leaving a live 0.12.0 at `project` scope in the same root, which `--scope project` brought along.
Corrected by the S155 fast check, after the stamp was written and moved into `plan_done/` where it cannot be edited: the stamp's "two commits behind its own recorded source" is wrong on both the number and the anchor, and its "at both user and project scope" is the registry's evidence rather than something `--version` can distinguish. MANUAL carries the corrected wording.
Why: a release that cannot complete until the user pushes makes the plan wait on something outside it, and the honest alternative is to ship what was reached and name what was not — the failure mode DEC-057 exists for is silence, not staleness.

## DEC-062  2026-08-23  v1: the workflow is rules, not enforcement
Tags: scope, architecture, v1
Decision: (Max, chat 2026-08-23) moltke 1.0 ships markdown only: three skills (`init`, `rules`, `audit`), the `adversarial_reviewer` agent, and templates. Deleted with it: `bin/moltke.py`, every hook, the test suite and golden surface, the `step` skill, the `.moltke.json` marker, the watcher subsystem, audit baselines and reconciliation, the testing ledger, and the teams merge semantics. The plan keeps one file per step in the three directories, moved by hand; `plan_done/` is history by stated rule, not by fence. Invariants INV-1..17 retire en bloc with the enforcement product; numbers stay reserved. The prime directive stands unchanged. Making the existing checks advisory instead of deleting them was rejected: it keeps the 3.5k-line maintenance surface that generated most of the project's own work.
Why: the original intent was a cheap orientation protocol for agents, and the enforcement layer had become the project — most steps and all thirteen audits policed the police, while the rules themselves fit on a page.

## DEC-063  2026-08-23  Project rules are interview answers, recorded per repository
Tags: init, rules, v1
Decision: (Max, chat 2026-08-23) `/moltke:init` interviews the user over a fixed catalog — GIT, AGENTS, TESTS, PLAN, DOCS, REVIEW, AUDIT, DEPS, COMMITS — each question carrying options and a default, with an accept-all-defaults fast path. Answers land in `AGENTS.md` under `## Project rules`, one line per rule, stable id first. `/moltke:rules` shows, adds, changes, or drops lines afterwards, and every change is also a `decisions.md` entry. A separate rules file was rejected: the ruleset the agent already reads is where its parameters belong.
Why: per-project rules the user actually chose beat a fixed ruleset nobody remembers agreeing to.

## DEC-064  2026-08-23  The migration prompt is an operator note in adocs/, not shipped documentation
Tags: docs, migration, v1
Decision: (Max, chat 2026-08-23) the 0.x -> 1.0 migration prompt lives at `adocs/migration_prompt.md` so it travels in git and can be copy-pasted on any machine. It is not part of the product: a root `MIGRATION.md` wired into MANUAL and README was drafted and reverted on Max's redirect, before any commit. MANUAL's own Migrating section stays as the shipped summary.
Why: moltke's docs describe the product; how Max drives his own fleet through the migration is his operator memory, and adocs/ is where this project keeps memory.

## DEC-065  2026-08-29  Machine-local Claude configuration is scrubbed from the living documents, and history is left alone
Tags: docs, decisions, privacy, install, git
Decision: (Max, chat 2026-08-29, from agent-supplied options) Detail about one operator's Claude config roots — which root a client uses, what each was named, which account or marketplace source each was pointed at — does not belong in this repository at all: it is environment, it goes stale silently, and it was already stale here. DEC-057 and DEC-061 keep their rule and lose their machine specifics; the parked install-route note in `status.md` goes; S161's accepts stops naming particular roots and scopes and says every root present on the machine instead. `plan_done/`, `adocs/audit/` and git history are left untouched: a rewrite was scoped at 165 of 224 commits and a force-push of a public `master` and `v1`, and Max declined it — nothing secret is in those commits, only home-directory paths and a public clone URL, and the repository's own rules forbid editing a finished stamp or an audit report. MANUAL and the migration prompt keep `~/.claude` and `CLAUDE_CONFIG_DIR`, which are product facts rather than this machine's arrangement.
Why: a document that records one machine's setup is wrong on every other machine and eventually on that one too, and the cost of carrying it is paid at every read.

## DEC-066  2026-08-29  Seventeen 0.x audit findings close by retirement of their target, named here
Tags: audit, findings, v1
Decision: (Max's standing rules, applied by the 2026-08-29 audit) the seventeen `planned` findings that targeted the 0.x enforcement product — `2026-08-11_adversarial-F01..F05` and `2026-08-19_adversarial-F01..F07,F09..F13` — move to `closed`: DEC-062/S160 deleted `bin/moltke.py`, the hooks, the fences, `--watch`, `--audit check`, and the suite wholesale, so each finding's reproduction has nothing left to run against, in the tree or in the shipped product (grep evidence in `adocs/audit/2026-08-29_adversarial.md`). DEC-062 did not name these ids; this entry is the discharge that does. `2026-08-11_adversarial-F06` and `2026-08-19_adversarial-F08` close separately, re-measured against the living files by the same run.
Why: a finding whose target no longer exists cannot be closed by a reproduction re-run, and leaving nineteen `planned` markers pointing at deleted code is drift the next auditor pays for.

## DEC-067  2026-08-29  The stale machine-local notes file is the operator's to fix, not a plan step
Tags: audit, findings, machine-local
Decision: `2026-08-29_adversarial-F08` is accepted: `.moltke.local.md` on this machine still carries 0.x template wording, but the file is untracked, invisible to any clone, and DEC-065 already ruled machine-local state out of this repository's documents — so no step is created; the operator replaces its body directly (done in the same session, after this entry, outside the commit).
Why: a plan step that changes nothing tracked cannot be verified from the repository, which is what steps are for.
