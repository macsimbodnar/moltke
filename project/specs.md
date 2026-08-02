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

- INV-11 every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is false. 2026-08-01 (S006, DEC-017): except the setup modes `--scaffold` and `--decline`, which run before the gate because they exist to create the marker; both still leave a declined repository untouched.
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
| `--scaffold` | `init` skill | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `project/` from templates; never overwrites an existing file |
| `--decline` | `init` skill | write `{"schema": 1, "enabled": false}`, durably; refuses to disable an already-enabled repository |
| `--audit OP ...` | `audit` skill | 2026-08-01 (S008): `new <type>` opens `project/audit/YYYY-MM-DD_<type>.md` from the template and refuses to overwrite; `list` prints every finding with its status and what references it, exiting non-zero while an open finding has neither a step nor a decision |
| `--step OP ...` | `step` skill | 2026-08-01 (S007): lifecycle operations `new <name> [--goal]`, `start <id>`, `block <parent> <name>`, `done <id> --stamp`, `status`. Each refuses rather than repairs, naming the missing condition; no transition may leave INV-1..INV-7 violated |

Every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is
false (INV-11).

2026-08-01 (S005), verified against live hook docs: `--pre-write`'s PATH is
optional; hooks pass the path via stdin JSON (`tool_input.file_path`).
`--log-prompt` always exits 0 because UserPromptSubmit exit 2 erases the
user's prompt. `--session-start` emits `hookSpecificOutput.additionalContext`
JSON, the only channel that reaches the model. Stop has no documented block
cap anymore, so `--stop` imposes its own: after 3 consecutive blocks for the
same prompt it allows the stop with a warning (state in
`.git/moltke_stop_state.json`), preserving the DEC-006 no-deadlock property.
`--stop`'s README/MANUAL gate is mechanical: a step file newly moved into
`plan_done/` must mention README and MANUAL in its `done:` stamp.

2026-08-02 (S011): `README.md` and `MANUAL.md` exist, so the MANUAL half of the
surface guard is live: it was verified to bite by removing `--decline` and
`--audit list` from MANUAL and observing the failure name exactly those two.

2026-08-01 (S009): the surface guard (`surface_guard: "cli"`, DEC-010) is
`tests/test_s009_surface.py`, holding `tests/golden/cli_surface.txt`. It reads
argparse's actions rather than `--help` prose, so help wording can change but a
flag or `--step`/`--audit` operation cannot be added, renamed, or removed
silently. A separate check requires every flag and operation to appear in the
specs CLI table, and an operation counts only where its own mode is described,
so refreshing the golden alone never makes the suite green. Refresh, after
updating the docs, with `python3 tests/test_s009_surface.py --refresh`. The
same check runs against `MANUAL.md` and is skipped until that file exists in
S011; closing that gap is part of S011.

2026-08-01 (S008): **template guidance is never data.** Every scanner reads
its input through `strip_guidance`, which drops fenced blocks and HTML
comments, so a commented example step is not planned, an example finding is
not open, and an example `DEC-001` does not consume the id. This rule exists
because the same defect appeared four separate times: commented plan steps,
example findings, the `paused_by` placeholder, and a scaffolded project whose
first real decision collided with the template's own example.

2026-08-01 (S008): INV-10 additionally requires a finding id to carry its own
report's name, so ids cannot drift between reports when an audit is re-run.
The reviewer's write fence is enforced in `--pre-write` using the PreToolUse
`agent_type` field: subagent frontmatter has no path-level restriction, so the
hook is the only place the limit can be real.

2026-08-01 (S007): unfilled template placeholders (`<!-- ... -->`) in a step
field read as empty everywhere, so a hand-copied `step_template.md` cannot
silently look paused. INV-4 counts `blocks:` declarations only from open steps:
a completed child's `blocks` field is history, not a live block.

2026-08-01 (S006): step ids are read from `plan.md` with HTML comments and
fenced blocks stripped, so commented-out example steps are not the plan. Found
by scaffolding a real repository: the template's example line produced a
phantom next step, a false stale-`status.md` report, and a Stop block on the
first turn.

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
