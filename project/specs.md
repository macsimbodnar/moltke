# Specs: moltke

2026-08-01: created from `bootstrap.md` (DEC-012). The locked decisions of §2
moved to `project/decisions.md` as DEC-001..DEC-012; the first plan of §8 moved
to `project/plan.md` and step files S001..S011. Facts otherwise preserved.

2026-08-01: project renamed `max_agent_workflow` → `moltke` (DEC-015): CLI
`bin/moltke.py`, marker `.moltke.json`, skills `init`, `step`, `audit`.

## Prime directive

Project state is always derivable from tracked files alone. An agent that
trusts nothing but the filesystem knows what to do next and why — in any
session, any tool, any machine.

## Invariants

Enforced by `bin/moltke.py` in marked repositories:

- INV-1  `plan_current/` holds at most `plan_active_max` non-paused steps.
- INV-2  stack depth in `plan_current/` never exceeds `plan_stack_max`.
- INV-3  every step file in `plan_todo/` and `plan_current/` appears in `plan.md`.
- INV-4  no step moves to `plan_done/` while another step names it in `blocks:`.
- INV-5  no step reaches `plan_done/` without a `done:` stamp and at least one `testing.md` row referencing its id.
- INV-6  step ids are unique across all three plan directories.
- INV-7  `plan_done/` is byte-identical to its state at session start.
- INV-8  `worklog.md` and `decisions.md` grow only by appending; earlier bytes are unchanged.
- INV-9  every `decisions.md` entry has a unique `DEC-<nnn>` id.
- INV-10 every audit finding is `open`, `planned`, `closed`, or `accepted`, and no report has `open` findings without a step or decision referencing them.

Properties of the checker itself:

- INV-11 every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is false.
- INV-12 every blocking exit carries a message stating exactly what to do to unblock (DEC-006: a `Stop` hook has a cap on consecutive blocks; an unactionable message deadlocks the session).

2026-08-01 (S004): INV-8 uses the same git HEAD baseline as INV-7: the
committed content must be a byte-prefix of the current file; untracked files
have no baseline, so the check abstains. INV-10 fixes the audit finding
format ahead of S008: a finding is a `### <report>-F<nn>` heading followed by
a `Status: <value>` line in its section; the S008 report template must conform.

2026-08-01 (S003): INV-7 is checked against git HEAD: tracked files under
`plan_done/` are never modified or deleted; additions are the one legal change
(append by move only). Repos without git history have no baseline, so the
check abstains. INV-3 additionally treats a missing `plan.md` in an enabled
repo as a violation.

Each invariant gets a test, and each test gets a `testing.md` row. Red-first
applies: write the test, watch it fail against a deliberately broken fixture
repository, record what it printed, then implement.

## What is being built

A Claude Code plugin that installs and enforces a document-driven development
workflow in any repository. The workflow gives an agent durable, cross-session,
cross-tool memory of a project: what to do next, why past choices were made,
what has been audited, and what is verified.

Name: `moltke`
Distribution: git repository plus a plugin marketplace entry, installed on each dev machine.

Before implementing hooks, plugins, or skills, fetch the current Claude Code
documentation and verify the APIs. This spec was written on 2026-08-01 and the
plugin and hook surfaces change. Do not trust the shapes below over the live docs.

## Plugin layout

```
moltke/
  .claude-plugin/plugin.json
  AGENTS.md                       # live rules for this repo
  CLAUDE.md                       # @AGENTS.md
  README.md                       # layout, build, test, exact commands
  MANUAL.md                       # install, operate, known bugs
  .moltke.json                    # this repo is itself marked
  skills/
    init/SKILL.md
    step/SKILL.md
    audit/SKILL.md
  agents/
    adversarial_reviewer.md
  hooks/
    hooks.json
  bin/
    moltke.py                     # single entry point for all checks
  templates/
    AGENTS.md                     # shipped copy of the ruleset
    CLAUDE.md
    cursor_rules
    moltke.json
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

## bin/moltke.py

One script, several modes. Every hook shells out to it. Keeping the logic in
one place means other tools (Codex, Cursor) can run the same checks manually,
which is the only enforcement available outside Claude Code.

| Mode | Called from | Behavior |
|---|---|---|
| `--session-start` | SessionStart hook | print `plan_current/` contents and the derived next step; flag `status.md` as stale if it disagrees |
| `--log-prompt` | UserPromptSubmit hook | append timestamp and verbatim prompt to `project/worklog.md` |
| `--pre-write PATH` | PreToolUse on Write and Edit | exit 2 if the path is under `plan_done/`, or is a step file outside the three plan directories |
| `--post-write` | PostToolUse | cheap invariant scan, non-blocking |
| `--stop` | Stop hook | exit 2 with an actionable message if source changed without a worklog recap, a stale `status.md`, a completed step lacking `testing.md` rows, or unchecked README and MANUAL |
| `--validate` | manual, any tool | run every invariant, report all violations, exit non-zero |
| `--scaffold` | `init` skill | create `project/` and `.moltke.json` from templates |

Every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is
false (INV-11).

Language: Python, standard library only. It runs on every prompt, so startup
cost matters and dependencies are unacceptable.

## Skills

**`init`.** Detects a missing or disabled marker, asks once whether to set the
workflow up, and either scaffolds from `templates/` or writes
`{"enabled": false}` and never asks again. Scaffolding writes `AGENTS.md`,
`CLAUDE.md`, the Cursor pointer, `.moltke.json`, and a populated `project/`.
Acceptance: running it twice is idempotent; declining is durable across
sessions; a repository with an existing `AGENTS.md` is never overwritten
without asking.

**`step`.** Manages the lifecycle: create a step, promote to current, pause a
parent and promote a blocking child, complete a step, regenerate `status.md`
from the filesystem. Acceptance: every transition leaves invariants 1 to 7
satisfied; completion is refused when the gate conditions are unmet, with the
specific missing condition named.

**`audit`.** Runs an audit through the `adversarial_reviewer` subagent, writes
a dated report with per-finding ids and severities, then proposes plan steps
carrying `closes:` links. Acceptance: the report is written before any fix;
findings map one-to-one to steps or to decisions with a stated reason;
re-running the audit is what moves a finding to `closed`.

## Subagent and hooks

`adversarial_reviewer` runs with read tools plus write access limited to
`project/audit/`. It cannot edit source. This is deliberate: a reviewer that
can fix what it finds stops producing evidence and starts producing patches.

Hooks in `hooks/hooks.json`, all delegating to `moltke.py`: `SessionStart`,
`UserPromptSubmit`, `PreToolUse` matching Write and Edit, `PostToolUse`,
`Stop`. Verify event names and the JSON schema against current documentation
before writing the file.

## Non-goals

- Enforcement outside Claude Code. Codex and Cursor read the rules and can ignore them. `--validate` is the only lever, invoked manually.
- Any project-specific content in templates. See DEC-002.
- Migrating existing repositories automatically. `init` scaffolds fresh; adopting an in-flight project is a manual exercise for now.

## Open items

- Confirm DEC-002 (public repository) before the first push. Resolves when Max pushes (DEC-014).
- Decide whether `status.md` earns its place after a few weeks of real use, or whether `plan_current/` plus the derived next step is sufficient on its own.
