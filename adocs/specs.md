# Specs: moltke

Current state only. The narrative of how each rule got its wording lives in
`adocs/plan_done/` step stamps, commit messages, and git history of this file
(compacted 2026-08-11, S106, DEC-042; the pre-compaction text is at git tag-less
history before that commit). Dated notes are no longer accumulated here.

## Prime directive

Project state is always derivable from tracked files alone. An agent that
trusts nothing but the filesystem knows what to do next and why — in any
session, any tool, any machine.

## Invariants

Enforced by `bin/moltke.py` in marked repositories. Numbers are stable and never
reused; a retired number stays listed so old audit reports keep meaning.

- INV-1  `plan_current/` holds at most `plan_active_max` non-paused steps, and
  every `paused_by` resolves: the pauser exists, is not the step itself, and no
  ring of steps pauses each other. `--step unpause` clears exactly the pauses
  this reports.
- INV-2  stack depth in `plan_current/` never exceeds `plan_stack_max`.
- INV-3  every step file in `plan_todo/` and `plan_current/` is a list entry in
  `plan.md`, and every id `plan.md` lists has a step file in one of the three
  directories. An id named only in prose is prose: neither listed nor a phantom.
  A missing `plan.md` in an enabled repository is a violation. Completed entries
  pruned by `--step done` are not missing: `plan_done/` is their record.
- INV-4  no step moves to `plan_done/` while another step names it in `blocks:`.
- INV-5  no step reaches `plan_done/` without a `done:` stamp recording the
  README and MANUAL check and at least one `testing.md` row referencing its id.
- INV-6  step ids are unique across the three plan directories, and a step
  file's `id:` field, when present, agrees with its filename — the filename is
  what every check acts on.
- INV-7  a file under `plan_done/` never changes or disappears after the commit
  that added it. Checked against git HEAD and history; additions are the one
  legal change. No git history means no baseline, and the check abstains.
- INV-8  retired 2026-08-11 (S105, DEC-042). It held `decisions.md` append-only
  with a high-water mark over git history. The documents hold current state and
  are compacted freely; git is the archive.
- INV-9  every `decisions.md` entry has a unique `DEC-<nnn>` id.
- INV-10 every audit finding is `open`, `planned`, `closed`, or `accepted`, and
  no report has `open` findings without a step or decision referencing them.
- INV-11 every mode exits 0 immediately when `.moltke.json` is absent or
  `enabled` is false — except `--scaffold` and `--decline`, which run before the
  gate because they exist to create the marker; both leave a declined repository
  untouched.
- INV-12 every blocking exit carries a message stating exactly what to do to
  unblock. The `Stop` cap on consecutive blocks lives wherever moltke can write
  its state beside the git directory; where it cannot, the gap is accepted
  (DEC-031, DEC-039) and the message names the missing cap.
- INV-13 `plan.md`, `decisions.md`, and every audit report have an even number
  of code-fence markers, because an unclosed fence hides content from every
  scanner.
- INV-14 no audit report states a finding under its own name that
  `strip_guidance` then removes. Comments come out before the comparison.
- INV-15 retired 2026-08-11 (S120, DEC-046) with the worklog: nothing writes
  prompts verbatim into a tracked file any more.
- INV-16 `specs.md` never states a prime directive that `strip_guidance` then
  removes; the section is compared against its stripped form.

## What is being built

A Claude Code plugin that installs and enforces a document-driven development
workflow: durable plan, decision, testing, and audit state in the repository,
checked by hooks in repositories that opt in via `.moltke.json`.

Name: `moltke`. Distribution: git repository plus a single-plugin marketplace
entry, installed per machine. Updates ship only on a `version` bump in
`.claude-plugin/plugin.json`.

## Plugin layout

```
.claude-plugin/plugin.json       manifest: name, explicit version
.claude-plugin/marketplace.json  single-plugin marketplace entry
bin/moltke.py                    every check and command, one entry point, stdlib only
hooks/hooks.json                 four hook events, all shelling out to bin/moltke.py
skills/init|step|audit/SKILL.md  the three skills, /moltke:<name>
agents/adversarial_reviewer.md   auditor subagent
templates/                       what --scaffold copies into a target repository
tests/                           the suite; tests/surface.py declares the guarded surface
```

## CLI surface

One entry point, `bin/moltke.py`, one mode per invocation. The golden test
(`tests/test_s009_surface.py`) fails on any drift from this table.

| Mode | What it does |
|---|---|
| `--validate` | run every invariant, print all violations to stdout, exit 1 if any |
| `--roadmap` | one timeline strip of the plan: done count from `plan_done/`, the split, the current or derived-next step; always exit 0 |
| `--scaffold` | create marker, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/moltke.mdc`, `adocs/` from templates; never overwrites; reports template drift; rolls back its own partial work on failure |
| `--decline` | write a durable `enabled: false` marker; refuses (exit 1, stderr) to disable an already-enabled repository |
| `--step new <name> [--goal TEXT]` | allocate the next id (refusing past S999), write the step file, list it in `plan.md`; name must match `[A-Za-z0-9_]+`; `--goal` must be one line |
| `--step start <id>` | `plan_todo/` → `plan_current/`; refuses an occupied destination |
| `--step block <parent> <name>` | create a blocking child, pause the parent; same name rule as `new` |
| `--step unpause <id>` | clear a pause that never resolves (phantom, self, or ring) — exactly what `--validate` reports; refuses a pause on reachable live work |
| `--step done <id> --stamp TEXT` | complete: preconditions, `test_command` gate, stamped move to `plan_done/`, parent unpause, prune `plan.md` to the last 5 done entries; `--stamp` must be one line recording the README and MANUAL check |
| `--step status` | regenerate `status.md` from the filesystem; everything below `- Parked:` is carried through verbatim |
| `--audit new <type>` | open `adocs/audit/YYYY-MM-DD_<type>.md` (`.2` suffix on a same-day re-run, never overwrites), record the reconciliation baseline; type must match `[A-Za-z0-9_-]+` |
| `--audit list` | every finding, status, and reference; exit 1 while an open finding has no home or a fence hides one |
| `--audit check` | reconcile the tree against the baseline: report and new `tests/` files expected, anything else listed, exit 1 |
| `--session-start` | SessionStart hook: emit stack, derived next step, staleness, planning nudge as JSON additionalContext |
| `--pre-write` | PreToolUse hook (Write|Edit): refuse writes into `plan_done/`, step files outside the plan directories, reviewer writes outside `adocs/audit/` + new `tests/` files |
| `--post-write` | PostToolUse hook: cheap invariant scan, non-blocking by contract |
| `--stop` | Stop hook: refuse to end a turn on violations, stale `status.md`, or unstamped arrivals; capped against deadlock, counted per problem set |

Exit codes: 0 clean; 1 findings (stdout) or refusals (stderr); 2 blocked
actions (stderr). `--post-write` returns 2 but is non-blocking. Capture both
streams when scripting.

Marker keys (`.moltke.json`): `schema`, `enabled`, `plan_active_max`,
`plan_stack_max`, `surface_guard`, `test_command`. `surface_guard` is one of
`cli`, `api`, `both`, `none` — `none` only alongside a decision saying why.
`test_command` runs from the root with a shell, 600 s timeout, refusing
completion on non-zero exit.

Hook events: `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`. The
UserPromptSubmit hook left with the worklog (S120, DEC-046). Skills: `init`, `step`, `audit`.

## Non-goals

- No daemon, no state outside the repository and `.git/`.
- No network access, no dependencies beyond the Python 3 standard library.
- No automatic fixing: every check refuses or reports; repair is the author's.
- No enforcement of document history (DEC-042): git is the archive.

## Open items

None open.
