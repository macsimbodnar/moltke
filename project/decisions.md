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

## DEC-016  2026-08-01  Build moltke rather than adopt an existing tool
Tags:         scope, ecosystem
Context:      before S002, Max asked whether an existing tool makes this redundant. Web evaluation of 2026-08-01: GitHub Spec Kit (~93k stars, constitution + specify/plan/tasks loop), GSD Core (STATE.md/CONTEXT.md phase loop, ex-GSD after archive/fork churn), BMAD (multi-agent personas), OpenSpec (change proposals with deltas), Beads (git-backed graph issue tracker as agent memory), SpillwaveSolutions/project-memory (memory-files skill, explicitly no enforcement). All are convention- or prompt-based: none ships marker-gated blocking enforcement, an append-only decision log with mandatory rejected options, report-before-fix audit discipline, or a red-first testing ledger.
Decision:     proceed with moltke as planned. (Max, after agent-supplied evaluation)
Rejected:     Spec Kit or GSD Core plus Beads (~70% coverage — planning structure and task state — at zero build cost, but compliance stays advisory and the evidence discipline is absent); adopting project-memory (no enforcement, no plan lifecycle, no testing ledger).
Consequences: the differentiator to protect is DEC-006 enforcement plus the evidence discipline; AGENTS.md as single source (DEC-003) matches the now-standard convention; the S002..S011 plan stands unchanged.

## DEC-017  2026-08-01  Setup modes are exempt from the INV-11 marker gate
Tags:         marker, cli, invariants
Context:      INV-11 requires every mode to exit 0 immediately when the marker is absent, but `--scaffold` exists precisely to create the marker in a repository that has none. Surfaced during S002, resolved at S006.
Decision:     INV-11 applies to every mode except the setup modes `--scaffold` and `--decline`, which run before the gate. `--decline` is added to the surface so declining is mechanical and durable rather than hand-written JSON. (Max, agent-supplied analysis)
Rejected:     dropping the gate for all modes (unmarked third-party checkouts would gain friction, defeating DEC-005); having the skill hand-write the declined marker (untestable, and the decline path is exactly what must be reliable).
Consequences: specs INV-11 carries a dated amendment; the CLI surface grows `--decline`, which the S009 golden test must cover; both setup modes still refuse to touch a repository whose marker says `enabled: false`.

## DEC-018  2026-08-01  Cursor pointer kept thin; Cursor reads AGENTS.md natively
Tags:         cursor, tools, templates
Context:      DEC-003 planned a `.cursor/rules` pointer. Cursor documentation checked 2026-08-01 states Cursor reads `AGENTS.md` natively and calls it a simple alternative to `.cursor/rules`; the legacy `.cursorrules` file is gone and project rules are `.cursor/rules/*.mdc` with `description`, `globs`, `alwaysApply` frontmatter.
Decision:     scaffold a minimal always-applied `.cursor/rules/moltke.mdc` that points at `AGENTS.md` and states no rules of its own. (agent-supplied analysis and choice, low-stakes; reversible by deleting the template)
Rejected:     dropping the pointer entirely (native support makes it redundant, but the pointer costs five lines and covers Cursor versions or configurations where native reading is off); a full parallel ruleset for Cursor (DEC-003 forbids it: guaranteed drift).
Consequences: the pointer must never carry rule content, only a reference, so `AGENTS.md` stays the single source of truth.

## DEC-019  2026-08-01  S010 narrowed to what the agent can verify; install checks become S012
Tags:         plan, verification, git
Context:      S010's acceptance included "marketplace entry installs on a second machine" and "DEC-002 confirmed before the first push". DEC-014 reserves all GitHub and environment configuration to Max: the agent commits and nothing else. Installing the plugin also mutates the local Claude Code configuration, which is outside "create commits".
Decision:     S010 covers what is mechanically verifiable without changing any environment: the manifest, the marketplace entry, component discoverability, and `claude plugin validate --strict`. Real installation, first-session hook firing, and second-machine verification move to S012, owned by Max, with the agent supplying exact commands. (agent-proposed under DEC-014, applied to the plan)
Rejected:     installing the plugin locally to satisfy the criterion (changes Max's Claude configuration without being asked, and a self-install is not the second-machine check the criterion actually wanted); marking S010 complete while claiming an unverified install (a completion stamp that overstates what was checked poisons every later reading of plan_done).
Consequences: `plan.md` gains S012 after S011; until it passes, the hooks and skills in this repository remain wired but never exercised by a live session, which is recorded in `status.md` rather than assumed away.

## DEC-020  2026-08-01  The plugin ships this repository's own workflow state
Tags:         plugin, layout, dogfood
Context:      `claude plugin validate --strict` on the plugin root warns that `CLAUDE.md` there is not loaded as project context. It is a symptom of a deliberate layout: DEC-012 self-hosts the workflow, so the repository root is simultaneously the plugin root, and `project/`, `tests/`, `.moltke.json`, `AGENTS.md`, and `CLAUDE.md` are copied into every install's plugin cache.
Decision:     keep the layout and record the consequence as a known issue in MANUAL rather than restructuring. (agent-supplied analysis; reversible)
Rejected:     moving the plugin into a `plugin/` subdirectory with `source: "./plugin"` (removes the cruft, but breaks the layout specs describe, splits the self-hosting story, and rewrites every hook and test path for a cosmetic gain); deleting the root `CLAUDE.md` (it is what makes Claude Code read `AGENTS.md` in this repository, per DEC-003).
Consequences: installs carry inert extra files, including this repository's worklog and plan history; the repository is public by DEC-002, so nothing is exposed that was not already. If the cache size or the confusion ever matters, the `plugin/` subdirectory move is the escape hatch.
