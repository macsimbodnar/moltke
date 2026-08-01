# Decisions

Append only, newest last. Every entry: stable `DEC-<nnn>` id, tags, context,
decision, rejected options, consequences. A reversal marks the old entry `VOID`,
dated, with a pointer to the superseding entry; it never deletes.

DEC-001..DEC-012 seeded during S001 from `bootstrap.md` §2: locked by Max in the
planning session of 2026-08-01, analysis and options supplied by the agent in
that session. Not to be relitigated during implementation. Originally seeded
newest first; reordered oldest first under DEC-013, same day, before any
enforcement existed.

## DEC-001  2026-08-01  Package as a plugin, not a loose skill
Tags:         distribution, plugin
Context:      the workflow must work on several dev machines.
Decision:     plugin in a git repo, installed via marketplace. (Max, planning session)
Rejected:     personal skill in `~/.claude/skills/` (per machine, unversioned, drifts); dotfiles symlink (no versioning, no update path).
Consequences: skills are namespaced `/max_agent_workflow:name`; updates land only when `version` in `plugin.json` is bumped.

## DEC-002  2026-08-01  Repository is public, with an explicit version field
Tags:         distribution, security
Context:      public exposes the workflow but not any project data. The real risk is write access, not read access, because plugin hooks execute shell commands on every machine where the plugin is installed.
Decision:     public repository, explicit `version` in `plugin.json` so updates require a deliberate bump, branch protection on `main`, 2FA on the account, no blind PR merges. (Max, planning session)
Rejected:     private repo (hides internal conventions, but the templates carry no project-specific content, and private adds a credential requirement on each new machine).
Consequences: templates must stay generic. Nothing about any employer, product, or internal architecture goes into this repository. Confirm this decision with Max before the first push.

## DEC-003  2026-08-01  AGENTS.md is the single source of truth for the rules
Tags:         rules, tools
Context:      Codex and Cursor may run in the same repositories.
Decision:     rules live in `AGENTS.md` at the target repo root; `CLAUDE.md` contains only `@AGENTS.md`; Cursor gets a thin `.cursor/rules` pointer. (Max, planning session)
Rejected:     maintaining parallel rule files per tool (guaranteed drift).
Consequences: Claude Code reads `CLAUDE.md`, not `AGENTS.md`, so the import line is mandatory and must be verified against current docs.

## DEC-004  2026-08-01  The workflow directory is project/, not agents/
Tags:         layout, naming
Context:      `agents/` collides with `AGENTS.md`, with `.claude/agents/` for subagent definitions, and with the plugin layout's own `agents/` directory.
Decision:     `project/`. (Max, planning session)
Rejected:     `agents/` (the collisions above).
Consequences: this repository, being a plugin, has a real `agents/` directory for subagents, and it must not be confused with workflow state.

## DEC-005  2026-08-01  Marker file .workflow.json at target repo root
Tags:         marker, hooks
Context:      hooks need one fixed path to check, and declining setup must be recordable without creating the directory the user declined.
Decision:     `.workflow.json` at root carries `schema`, `enabled`, `plan_active_max`, `plan_stack_max`, `surface_guard`. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: every hook exits 0 immediately when the file is absent or `enabled` is false. No marker, no friction.

## DEC-006  2026-08-01  Enforcement is blocking, gated on the marker
Tags:         hooks, enforcement
Context:      Max asked for maximum strictness conditional on correct setup.
Decision:     hooks block rather than warn, but only in marked repositories. (Max, planning session)
Rejected:     warn-only (ignored in practice); always-on (unusable in third-party checkouts).
Consequences: every blocking message must state exactly what to do to unblock, because a `Stop` hook has a cap on consecutive blocks and an unactionable message deadlocks the session.

## DEC-007  2026-08-01  plan_current/ is a stack, not a set
Tags:         plan, concurrency
Context:      work discovered mid-step often blocks the step in progress.
Decision:     blocking discoveries are promoted as children with `blocks:` and `paused_by:` links; `plan_active_max` non-paused steps (default 1), `plan_stack_max` total depth (default 3). (Max, planning session)
Rejected:     simply raising a concurrency counter (loses the dependency, conflates blocking work with parallel work).
Consequences: exceeding the depth limit is a signal the plan is wrong at design level and routes to a decision plus a replan.

## DEC-008  2026-08-01  Step ids are stable and never renumbered
Tags:         plan, naming
Context:      position-encoding filenames make insertion and reordering expensive.
Decision:     `S<nnn>_short_name.md` allocated in creation order; plan order lives only in `plan.md`. (Max, planning session)
Rejected:     position-encoding filenames (renaming cascades on every insertion or reorder).
Consequences: reordering is a one-line edit; ids stay valid as references from commits, decisions, and audit findings.

## DEC-009  2026-08-01  status.md added; ideas.md and history/ rejected
Tags:         layout, status
Context:      a prior working system used all three.
Decision:     keep `status.md` (session pointer, rewritten in place). (Max, planning session)
Rejected:     `ideas.md` (its function is covered by a Parked section in `status.md` and by recorded rejected options in `decisions.md`); `history/` (`plan_done/` plus git already is the history, and a second copy invites resuming retired checklists).
Consequences: the rule "never resume a checklist from `plan_done/`" carries the weight `history/` would have carried.

## DEC-010  2026-08-01  The public-surface golden test is mandatory
Tags:         testing, docs, surface
Context:      documentation drifts silently from code.
Decision:     a golden test over whatever `surface_guard` names, failing until MANUAL and specs are updated in the same commit. Opting out requires `surface_guard: "none"` plus a recorded reason. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: this repository's own surface is the `workflow_check` CLI, so `surface_guard` here is `cli`.

## DEC-011  2026-08-01  worklog.md is forensic, never a context source
Tags:         worklog, context
Context:      an append-only prompt log grows without bound and would become the largest and least useful file in the repo.
Decision:     agents never read `worklog.md` to determine state or reasoning. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: anything in it that matters must be promoted into `status.md`, `specs.md`, or `decisions.md`.

## DEC-012  2026-08-01  This repository self-hosts the workflow
Tags:         process, dogfood
Context:      the conventions should be tested somewhere low-stakes before being applied to real work.
Decision:     `max_agent_workflow` is the first project to use the workflow, with `bootstrap.md` becoming its `project/specs.md` and this build becoming its first plan. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: the root `AGENTS.md` is the live ruleset, `templates/AGENTS.md` is the shipped copy, and a test asserts the two are identical.

## DEC-013  2026-08-01  decisions.md orders oldest first, newest appended at bottom
Tags:         decisions, layout, efficiency
Context:      AGENTS.md mandated newest-first ordering while INV-8 required append-only growth with earlier bytes unchanged; a new entry at the top shifts earlier bytes. Surfaced during S001, routed to S004, resolved by Max the same day.
Decision:     newest last. Entries append at the bottom via shell append, costing no reads; INV-8 stays literal byte-append for both `worklog.md` and `decisions.md`. (Max)
Rejected:     newest-first with an entry-integrity check (every write costs a partial read; INV-8 becomes entry-based — more code, weaker guarantee; recency reads are `tail -n` and lookups are grep either way, so top ordering bought nothing).
Consequences: AGENTS.md §2 and §8 amended; the seeded DEC-001..DEC-012 reordered oldest first in the same commit, authorized by this decision as a one-time exception to the §11 reorder prohibition; the S004 reconcile clause dropped.

## DEC-014  2026-08-01  GitHub configuration is Max's own; agent git surface is commits only
Tags:         git, github, process
Context:      S001 surfaced open items around repository visibility (DEC-002 confirmation), branch naming versus the `main` protection target, and pushing.
Decision:     Max handles GitHub configuration personally: visibility, remotes, branch naming and protection, pushes, app installs. The agent creates commits and nothing else, until new orders. (Max)
Rejected:     agent-driven branch rename and push preparation (offered, declined).
Consequences: DEC-002 confirmation resolves whenever Max pushes; master/main naming is Max's call; status.md parked items updated accordingly.

## DEC-015  2026-08-01  Project renamed to moltke
Tags:         naming, distribution
Context:      Max renamed the project before implementation started. Moltke commanded armies he could not see by writing orders that survived his absence; same problem, smaller scale.
Decision:     full rename: plugin and repository `moltke`; skills `init`, `step`, `audit` (commands /moltke:init, /moltke:step, /moltke:audit); CLI `bin/moltke.py`; marker `.moltke.json`; template `templates/moltke.json`. (Max)
Rejected:     namespace-only rename keeping `workflow_check.py`, `.workflow.json`, and the long skill names (smallest diff, but a generic marker name can collide with other tools, and nothing is coded yet, so the full rename is free now versus a migration later).
Consequences: earlier entries and immutable history naming `max_agent_workflow`, `workflow_check`, or `.workflow.json` (DEC-001, DEC-005, DEC-010, DEC-012, plan_done/S001, old testing.md rows, worklog) read through this entry; specs, AGENTS.md, plan, and step files updated in the same commit; GitHub repository rename and local directory rename are Max's own (DEC-014).
