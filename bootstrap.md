# Bootstrap: max_agent_workflow plugin

Handoff document. Everything below was designed in a separate planning session. Read it fully before writing anything.

Companion file: `AGENTS.md`, in this same directory. It is the finished ruleset and it is both the live rules for this repository and the artifact this plugin ships.

## How to use this file

```
mkdir max_agent_workflow && cd max_agent_workflow
git init
# copy bootstrap.md and AGENTS.md in
claude
> read bootstrap.md and AGENTS.md, then set up this repository per section 8
```

Before implementing hooks, plugins, or skills, fetch the current Claude Code documentation and verify the APIs. This document was written on 2026-08-01 and the plugin and hook surfaces change. Do not trust the shapes below over the live docs.

## 1. What is being built

A Claude Code plugin that installs and enforces a document-driven development workflow in any repository. The workflow gives an agent durable, cross-session, cross-tool memory of a project: what to do next, why past choices were made, what has been audited, and what is verified.

Name: `max_agent_workflow`
Distribution: git repository plus a plugin marketplace entry, installed on each dev machine.

## 2. Locked decisions

Seed these into `project/decisions.md` as the first entries, preserving ids. They are already decided; do not relitigate them during implementation.

**DEC-001 Package as a plugin, not a loose skill.**
Context: the workflow must work on several dev machines. Decision: plugin in a git repo, installed via marketplace. Rejected: personal skill in `~/.claude/skills/` (per machine, unversioned, drifts); dotfiles symlink (no versioning, no update path). Consequences: skills are namespaced `/max_agent_workflow:name`; updates land only when `version` in `plugin.json` is bumped.

**DEC-002 Repository is public, with an explicit version field.**
Context: public exposes the workflow but not any project data. The real risk is write access, not read access, because plugin hooks execute shell commands on every machine where the plugin is installed. Decision: public repository, explicit `version` in `plugin.json` so updates require a deliberate bump, branch protection on `main`, 2FA on the account, no blind PR merges. Rejected: private repo (hides internal conventions, but the templates carry no project-specific content, and private adds a credential requirement on each new machine). Consequences: templates must stay generic. Nothing about any employer, product, or internal architecture goes into this repository. Confirm this decision with Max before the first push.

**DEC-003 `AGENTS.md` is the single source of truth for the rules.**
Context: Codex and Cursor may run in the same repositories. Decision: rules live in `AGENTS.md` at the target repo root; `CLAUDE.md` contains only `@AGENTS.md`; Cursor gets a thin `.cursor/rules` pointer. Rejected: maintaining parallel rule files per tool (guaranteed drift). Consequences: Claude Code reads `CLAUDE.md`, not `AGENTS.md`, so the import line is mandatory and must be verified against current docs.

**DEC-004 The workflow directory is `project/`, not `agents/`.**
Context: `agents/` collides with `AGENTS.md`, with `.claude/agents/` for subagent definitions, and with the plugin layout's own `agents/` directory. Decision: `project/`. Consequences: this repository, being a plugin, has a real `agents/` directory for subagents, and it must not be confused with workflow state.

**DEC-005 Marker file `.workflow.json` at target repo root.**
Context: hooks need one fixed path to check, and declining setup must be recordable without creating the directory the user declined. Decision: `.workflow.json` at root carries `schema`, `enabled`, `plan_active_max`, `plan_stack_max`, `surface_guard`. Consequences: every hook exits 0 immediately when the file is absent or `enabled` is false. No marker, no friction.

**DEC-006 Enforcement is blocking, gated on the marker.**
Context: Max asked for maximum strictness conditional on correct setup. Decision: hooks block rather than warn, but only in marked repositories. Rejected: warn-only (ignored in practice); always-on (unusable in third-party checkouts). Consequences: every blocking message must state exactly what to do to unblock, because a `Stop` hook has a cap on consecutive blocks and an unactionable message deadlocks the session.

**DEC-007 `plan_current/` is a stack, not a set.**
Context: work discovered mid-step often blocks the step in progress. Decision: blocking discoveries are promoted as children with `blocks:` and `paused_by:` links; `plan_active_max` non-paused steps (default 1), `plan_stack_max` total depth (default 3). Rejected: simply raising a concurrency counter (loses the dependency, conflates blocking work with parallel work). Consequences: exceeding the depth limit is a signal the plan is wrong at design level and routes to a decision plus a replan.

**DEC-008 Step ids are stable and never renumbered.**
Context: position-encoding filenames make insertion and reordering expensive. Decision: `S<nnn>_short_name.md` allocated in creation order; plan order lives only in `plan.md`. Consequences: reordering is a one-line edit; ids stay valid as references from commits, decisions, and audit findings.

**DEC-009 `status.md` added; `ideas.md` and `history/` rejected.**
Context: a prior working system used all three. Decision: keep `status.md` (session pointer, rewritten in place). Rejected: `ideas.md` (its function is covered by a Parked section in `status.md` and by recorded rejected options in `decisions.md`); `history/` (`plan_done/` plus git already is the history, and a second copy invites resuming retired checklists). Consequences: the rule "never resume a checklist from `plan_done/`" carries the weight `history/` would have carried.

**DEC-010 The public-surface golden test is mandatory.**
Context: documentation drifts silently from code. Decision: a golden test over whatever `surface_guard` names, failing until MANUAL and specs are updated in the same commit. Opting out requires `surface_guard: "none"` plus a recorded reason. Consequences: this repository's own surface is the `workflow_check` CLI, so `surface_guard` here is `cli`.

**DEC-011 `worklog.md` is forensic, never a context source.**
Context: an append-only prompt log grows without bound and would become the largest and least useful file in the repo. Decision: agents never read it to determine state or reasoning. Consequences: anything in it that matters must be promoted into `status.md`, `specs.md`, or `decisions.md`.

**DEC-012 This repository self-hosts the workflow.**
Context: the conventions should be tested somewhere low-stakes before being applied to real work. Decision: `max_agent_workflow` is the first project to use the workflow, with `bootstrap.md` becoming its `project/specs.md` and this build becoming its first plan. Consequences: the root `AGENTS.md` is the live ruleset, `templates/AGENTS.md` is the shipped copy, and a test asserts the two are identical.

## 3. Plugin layout

```
max_agent_workflow/
  .claude-plugin/plugin.json
  AGENTS.md                       # live rules for this repo
  CLAUDE.md                       # @AGENTS.md
  README.md                       # layout, build, test, exact commands
  MANUAL.md                       # install, operate, known bugs
  .workflow.json                  # this repo is itself marked
  skills/
    workflow_init/SKILL.md
    plan_step/SKILL.md
    project_audit/SKILL.md
  agents/
    adversarial_reviewer.md
  hooks/
    hooks.json
  bin/
    workflow_check.py             # single entry point for all checks
  templates/
    AGENTS.md                     # shipped copy of the ruleset
    CLAUDE.md
    cursor_rules
    workflow.json
    project/
      status.md
      specs.md
      plan.md
      decisions.md
      testing.md
      worklog.md
    step_template.md
    audit_report_template.md
  tests/
  project/                        # this repo's own workflow state
```

## 4. `bin/workflow_check.py`

One script, several modes. Every hook shells out to it. Keeping the logic in one place means other tools (Codex, Cursor) can run the same checks manually, which is the only enforcement available outside Claude Code.

Modes:

| Mode | Called from | Behavior |
|---|---|---|
| `--session-start` | SessionStart hook | print `plan_current/` contents and the derived next step; flag `status.md` as stale if it disagrees |
| `--log-prompt` | UserPromptSubmit hook | append timestamp and verbatim prompt to `project/worklog.md` |
| `--pre-write PATH` | PreToolUse on Write and Edit | exit 2 if the path is under `plan_done/`, or is a step file outside the three plan directories |
| `--post-write` | PostToolUse | cheap invariant scan, non-blocking |
| `--stop` | Stop hook | exit 2 with an actionable message if source changed without a worklog recap, a stale `status.md`, a completed step lacking `testing.md` rows, or unchecked README and MANUAL |
| `--validate` | manual, any tool | run every invariant, report all violations, exit non-zero |
| `--scaffold` | `workflow_init` skill | create `project/` and `.workflow.json` from templates |

Every mode exits 0 immediately when `.workflow.json` is absent or `enabled` is false.

Language: Python, standard library only. It runs on every prompt, so startup cost matters and dependencies are unacceptable.

## 5. Invariants the script enforces

1. `plan_current/` holds at most `plan_active_max` non-paused steps.
2. Stack depth in `plan_current/` never exceeds `plan_stack_max`.
3. Every step file in `plan_todo/` and `plan_current/` appears in `plan.md`.
4. No step moves to `plan_done/` while another step names it in `blocks:`.
5. No step reaches `plan_done/` without a `done:` stamp and at least one `testing.md` row referencing its id.
6. Step ids are unique across all three plan directories.
7. `plan_done/` is byte-identical to its state at session start.
8. `worklog.md` and `decisions.md` grow only by appending; earlier bytes are unchanged.
9. Every `decisions.md` entry has a unique `DEC-<nnn>` id.
10. Every audit finding is `open`, `planned`, `closed`, or `accepted`, and no report has `open` findings without a step or decision referencing them.

Each invariant gets a test, and each test gets a `testing.md` row. Red-first applies: write the test, watch it fail against a deliberately broken fixture repository, record what it printed, then implement.

## 6. Skills

**`workflow_init`.** Detects a missing or disabled marker, asks once whether to set the workflow up, and either scaffolds from `templates/` or writes `{"enabled": false}` and never asks again. Scaffolding writes `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, `.workflow.json`, and a populated `project/`. Acceptance: running it twice is idempotent; declining is durable across sessions; a repository with an existing `AGENTS.md` is never overwritten without asking.

**`plan_step`.** Manages the lifecycle: create a step, promote to current, pause a parent and promote a blocking child, complete a step, regenerate `status.md` from the filesystem. Acceptance: every transition leaves invariants 1 to 7 satisfied; completion is refused when the gate conditions are unmet, with the specific missing condition named.

**`project_audit`.** Runs an audit through the `adversarial_reviewer` subagent, writes a dated report with per-finding ids and severities, then proposes plan steps carrying `closes:` links. Acceptance: the report is written before any fix; findings map one-to-one to steps or to decisions with a stated reason; re-running the audit is what moves a finding to `closed`.

## 7. Subagent and hooks

`adversarial_reviewer` runs with read tools plus write access limited to `project/audit/`. It cannot edit source. This is deliberate: a reviewer that can fix what it finds stops producing evidence and starts producing patches.

Hooks in `hooks/hooks.json`, all delegating to `workflow_check.py`: `SessionStart`, `UserPromptSubmit`, `PreToolUse` matching Write and Edit, `PostToolUse`, `Stop`. Verify event names and the JSON schema against current documentation before writing the file.

## 8. First plan

Seed `project/plan.md` with these, in order:

- `S001` scaffold this repository against its own conventions, seed decisions DEC-001 to DEC-012
- `S002` `workflow_check.py` skeleton, marker parsing, `--validate` mode, broken-fixture test harness
- `S003` invariants 1 to 7, red-first, one test each
- `S004` invariants 8 to 10
- `S005` hooks wiring, all five events, verified against live docs
- `S006` `workflow_init` skill and the `templates/` tree
- `S007` `plan_step` skill
- `S008` `adversarial_reviewer` subagent and `project_audit` skill
- `S009` golden test over the `workflow_check` CLI surface, plus the test asserting `AGENTS.md` and `templates/AGENTS.md` are identical
- `S010` plugin manifest, marketplace entry, install verification on a second machine
- `S011` README and MANUAL

Work `S001` first and by hand, because from `S002` onward the workflow is enforcing itself.

## 9. Non-goals

- Enforcement outside Claude Code. Codex and Cursor read the rules and can ignore them. `--validate` is the only lever, invoked manually.
- Any project-specific content in templates. See DEC-002.
- Migrating existing repositories automatically. `workflow_init` scaffolds fresh; adopting an in-flight project is a manual exercise for now.

## 10. Open items

- Confirm DEC-002 (public repository) before the first push.
- Decide whether `status.md` earns its place after a few weeks of real use, or whether `plan_current/` plus the derived next step is sufficient on its own.
