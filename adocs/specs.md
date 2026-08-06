# Specs: moltke

2026-08-01: created from `bootstrap.md` (DEC-012). The locked decisions of §2
moved to `adocs/decisions.md` as DEC-001..DEC-012; the first plan of §8 moved
to `adocs/plan.md` and step files S001..S011. Facts otherwise preserved.

2026-08-01: project renamed `max_agent_workflow` → `moltke` (DEC-015): CLI
`bin/moltke.py`, marker `.moltke.json`, skills `init`, `step`, `audit`.

2026-08-02 (S013): the workflow directory is renamed `project/` → `adocs/`,
agent documentation (DEC-021). Every path in this file, in `bin/moltke.py` via
the single `DOCS` constant, in the hook messages, and in the templates reads
`adocs/`. No migration path exists because no repository other than this one
had the plugin installed. Paths inside `plan_done/`, and inside `worklog.md`
and `decisions.md` entries predating DEC-021, still read `project/`: they are
immutable or append-only history and are never rewritten.

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
- INV-7  a file under `plan_done/` never changes or disappears after the commit that added it. 2026-08-06 (S018, F12): the original wording, "`plan_done/` is byte-identical to its state at session start", is superseded — it promised a session-scoped guarantee the code never implemented, and the 2026-08-01 amendment below redefined it without saying so.
- INV-8  `decisions.md` grows only by appending; earlier bytes are unchanged. 2026-08-06 (S030, DEC-025): narrowed from "`worklog.md` and `decisions.md`", which is superseded. The worklog is append-only by convention and no longer checked.
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

2026-08-06 (S018): INV-7 and INV-8 each check two baselines, because HEAD alone
was never a baseline — it moves at every step completion, so committing the
tampering erased the violation (finding F04). The working-tree comparisons above
stay, covering the uncommitted window; git history covers everything already
committed. INV-7 reads `git log --name-status` over `plan_done/` and treats any
status other than `A` as a violation, naming the commit. INV-8 reads
`git log --numstat` over `decisions.md` and treats any commit that removed lines
as a violation, which is line granularity rather than bytes: an in-place edit
still reads as one line removed and one added, so it is caught either way. Both
pass `--no-renames`, so a move into the directory reads as the addition it is —
this is what keeps the S013 `project/` to `adocs/` rename legal — and a move out
reads as the deletion it is. Both still abstain with no history. Neither is in
`CHEAP_CHECKS`, so `--post-write` does not pay for them.

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
    adocs/
      status.md
      specs.md
      plan.md
      decisions.md
      testing.md
      worklog.md
    step_template.md
    audit_report_template.md
  tests/
  adocs/                        # this repo's own workflow state
```

## bin/moltke.py

One script, several modes. Every hook shells out to it. Keeping the logic in
one place means other tools (Codex, Cursor) can run the same checks manually,
which is the only enforcement available outside Claude Code.

| Mode | Called from | Behavior |
|---|---|---|
| `--session-start` | SessionStart hook | print `plan_current/` contents and the derived next step; flag `status.md` as stale if it disagrees |
| `--log-prompt` | UserPromptSubmit hook | append timestamp and verbatim prompt to `adocs/worklog.md` |
| `--pre-write PATH` | PreToolUse on Write and Edit | exit 2 if the path is under `plan_done/`, or is a step file outside the three plan directories |
| `--post-write` | PostToolUse | cheap invariant scan, non-blocking |
| `--stop` | Stop hook | exit 2 with an actionable message if source changed without a worklog recap, a stale `status.md`, a completed step lacking `testing.md` rows, or unchecked README and MANUAL |
| `--validate` | manual, any tool | run every invariant, report all violations, exit non-zero |
| `--scaffold` | `init` skill | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `adocs/` from templates; never overwrites an existing file |
| `--decline` | `init` skill | write `{"schema": 1, "enabled": false}`, durably; refuses to disable an already-enabled repository |
| `--audit OP ...` | `audit` skill | 2026-08-01 (S008): `new <type>` opens `adocs/audit/YYYY-MM-DD_<type>.md` from the template and refuses to overwrite; `list` prints every finding with its status and what references it, exiting non-zero while an open finding has neither a step nor a decision. 2026-08-06 (S017): `new` also records a working-tree baseline in `.git/moltke_audit_baseline.json`, and `check` reconciles the run against it, printing expected and unexpected changes and exiting 1 on anything unexpected |
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

2026-08-06 (S030, DEC-025): `APPEND_ONLY_FILES` holds `decisions.md` alone.
Rewriting, trimming, or deleting `adocs/worklog.md` is no longer a violation:
nothing cites a worklog line by id, it is forensic and never a context source
(DEC-011), and enforcing it is what made a secret pasted into a prompt
unremovable. `decisions.md` keeps enforcement because `DEC-<nnn>` ids are cited
from code comments, commit messages, `specs.md`, and step files, so a rewritten
entry silently changes what every one of those citations means; the refusal now
says so. INV-7 and `plan_done/` are untouched.

2026-08-06 (S017, DEC-022): prevention gives way to reconciliation. `--audit new`
records a working-tree baseline in `.git/moltke_audit_baseline.json` — captured
before the report is written, so the report is part of the run's footprint and is
classified rather than invisible — as `{path: [porcelain status, sha256]}` over
`git status --porcelain -uall`. `-uall` because plain porcelain collapses a wholly
untracked directory into one entry, which would hide the report inside
`adocs/audit/`. The hash is what catches a file edited before the audit and edited
again during it, whose status never moves. `--audit check` then prints the
footprint split in two: this run's own report and new files under `tests/` are
expected, everything else — including a modified existing test, and a
pre-existing change reverted — is unexpected, exits 1, and says to review each
change with `git diff` before acting on any finding. Pre-existing dirt is in the
baseline, so it is never attributed to the run. Without git, or before `--audit
new` has run, `check` refuses and names what to run; ignored paths are outside
`git status` and so outside this check.

The fence widens to match: the reviewer may write under `adocs/audit/` and may
create new files under `tests/`, since a red-first regression test is evidence
while editing an existing test is a patch. `Bash` stays unconstrained by design
(DEC-022 rejected inspecting command strings as unparseable), so the fence is a
fast clear failure on the common path, never the guarantee.

2026-08-06 (S016): the reviewer write fence matches the scoped `agent_type`.
Observed live, by instrumenting the installed 0.2.0 hook to dump its PreToolUse
payload and spawning each agent through the plugin: a plugin subagent sends
`agent_type: "moltke:adversarial_reviewer"` plus an `agent_id`, a built-in
subagent sends `agent_type: "general-purpose"`, and the main thread sends neither
key. So bare equality never matched and the fence failed open (F02). The match is
now on the part after the last colon, which keeps working if the plugin is
installed under another name; the cost is that another plugin's agent named
`adversarial_reviewer` would also be fenced, chosen deliberately because that
blocks loudly while the alternative fails open silently. An absent `agent_type`
is the main thread and is never fenced. The fence covers `Write` and `Edit` only:
the reviewer also holds `Bash`, whose writes no PreToolUse matcher sees, which is
DEC-022's territory and S017's.

2026-08-06 (S015): `--stop`'s recap gate no longer reads worklog growth. Growth
cannot be the signal, because `UserPromptSubmit` appends the prompt before the
turn begins, so by the time `Stop` runs the worklog has always grown and the
comparison was always false (finding F01). The gate now asks whether a `## …`
heading containing `recap` follows the last heading ending in `prompt`. A heading
matching both reads as a recap, so a recap titled after prompt handling still
counts. Headings inside fenced blocks are guidance, not data. The gate abstains
when the repository has no `HEAD` commit: there is no history a recap would sit
alongside, and a fresh `--scaffold` is not work — the same abstain INV-7 and
INV-8 make. This removes `--stop`'s last dependence on the worklog's git
baseline, which DEC-025 is about to drop.

2026-08-06 (S014): `--log-prompt` creates `adocs/` before appending, so a marked
repository whose docs tree is missing still records the prompt. When the append
fails anyway it writes `.git/moltke_log_failure.json` (`since`, `count`,
`error`), and `--session-start` reports that once in `additionalContext` and then
removes it: `UserPromptSubmit` must exit 0, so stderr reaches nobody, and
`SessionStart` is the only channel that reaches the model. Reporting once rather
than until cleared keeps it self-healing — a failure that persists rewrites the
breadcrumb on the next prompt, one that is fixed goes quiet. Nothing is written
outside `.git/`, because an untracked file at the repo root reads as a source
change to `--stop`. Without a `.git` directory there is no breadcrumb and the
failure is stderr-only. Lost prompts are not recovered: the breadcrumb records
that logging failed, not what was said (finding F14).

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
hook is the only place the limit can be real. — Superseded 2026-08-06 (S017,
DEC-022): the last sentence was wrong. The hook only sees the tools its matcher
names, and the reviewer also holds `Bash`, so the fence was never the limit; see
the S017 note below.

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
`CLAUDE.md`, the Cursor pointer, `.moltke.json`, and a populated `adocs/`.
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
`adocs/audit/`. It cannot edit source. This is deliberate: a reviewer that
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
