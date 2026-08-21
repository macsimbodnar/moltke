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
- INV-5  no step reaches `plan_done/` without a `done:` stamp. Narrowed by
  DEC-048 (S125): the stamp is free text, and `testing.md` rows are voluntary.
- INV-6  step ids are unique across the three plan directories, and a step
  file's `id:` field, when present, agrees with its filename — the filename is
  what every check acts on.
- INV-7  a file under `plan_done/` never changes or disappears after the commit
  that added it. Checked against git HEAD and history; additions are the one
  legal change. No git history means no baseline, and the check abstains.
- INV-8  retired 2026-08-11 (S105, DEC-042). It held `decisions.md` append-only
  with a high-water mark over git history. The documents hold current state and
  are compacted freely; git is the archive.
- INV-9  every `decisions.md` entry has a unique `DEC-<nnn>` id, three digits
  or more; a `## DEC-` heading that is not one is reported, not skipped, since
  a width no scanner reads is an entry no invariant checks.
- INV-10 every audit finding is `open`, `planned`, `closed`, or `accepted`, and
  no report has `open` findings without a step or decision referencing them.
- INV-11 every mode exits 0 immediately when `.moltke.json` is absent or
  `enabled` is false — except four that run before the gate: `--scaffold` and
  `--decline`, which exist to create the marker, and both leave a declined
  repository untouched; `--watch`, whose exit codes are answers about a run that
  the gate's exit 0 would fake; and `--version`, which answers which moltke is
  running and is most useful exactly where checkout and hooks disagree. The
  gated list is derived from the parser, so a new mode is covered on the day it
  is added and an exemption has to be written down to exist.
- INV-12 every blocking exit carries a message stating exactly what to do to
  unblock. The `Stop` cap on consecutive blocks lives wherever moltke can write
  its state beside the git directory; where it cannot, the gap is accepted
  (DEC-031, DEC-039) and the message names the missing cap.
- INV-13 retired 2026-08-11 (S124, DEC-047) with the fence police: nothing
  blocks on fence counts. Stripping stays, so quoting stays safe.
- INV-14 retired 2026-08-11 (S124, DEC-047): a fence-swallowed finding is
  listed as `hidden` by `--audit list` instead of blocking.
- INV-15 retired 2026-08-11 (S120, DEC-046) with the worklog: nothing writes
  prompts verbatim into a tracked file any more.
- INV-16 retired 2026-08-11 (S124, DEC-047); the planning nudge still stays
  quiet when a directive exists on disk, readable or not.
- INV-17 the leaked-watcher class is unarmable: a persistent Monitor arm whose
  executed command is not `--watch` is refused unless its command carries
  `MOLTKE_UNBOUNDED_OK`, and a single-match follow (`tail -f | grep -m N`) is
  refused always — the token is read after that branch, so it exempts the
  persistent-arm rule and never the follow (S146). Executed, not mentioned:
  naming the primitive in a comment or echoing it ahead of a hand-composed
  follow arms nothing (S134). Enforced at arm time by `--pre-command` in Claude
  Code (DEC-049 as narrowed by DEC-051); elsewhere it is a §12 rule with no
  mechanical teeth, like everything else outside Claude Code. 2026-08-18
  (DEC-052): arrived as INV-13 on the merged branch. DEC-054 settled that an
  arm-time blocker does belong here: DEC-047 retired checks that were wrong, not
  checks that are strict, and this one refuses at arm time while naming the
  command to use instead.

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
| `--version` | print the version and the directory it runs from — the answer to "which moltke am I talking to" when hooks and checkout disagree |
| `--validate` | run every invariant, print all violations to stdout, exit 1 if any |
| `--roadmap` | one timeline strip of the plan: done count from `plan_done/`, the split, the current or derived-next step; always exit 0 |
| `--scaffold` | create marker, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/moltke.mdc`, `adocs/` from templates; never overwrites; reports template drift; rolls back its own partial work on failure |
| `--decline` | write a durable `enabled: false` marker; refuses (exit 1, stderr) to disable an already-enabled repository, and leaves an already-declined one byte-identical, saying what `--scaffold` says there |
| `--step new <name> [--goal TEXT]` | allocate the next id — three digits, widening to four past S999, refused past S9999, the widest form every id scan reads — write the step file, list it in `plan.md`; name must match `[A-Za-z0-9_]+`; `--goal` must be one line |
| `--step start <id>` | `plan_todo/` → `plan_current/`; refuses an occupied destination |
| `--step unclaim <id>` | `plan_current/` → `plan_todo/`, the inverse of `start`: clears `author:` and nothing else. Refuses a step that is not claimed, one in `plan_done/`, one carrying a `done:` stamp, an occupied destination, a `paused_by` — routed by where the pauser is, `--step unpause` for a pause that never resolves, `--step start` for a pauser in `plan_todo/`, `--step done` for one in `plan_current/` — and a step another `plan_current/` step declares `blocks:`. Author-blind: it drops a teammate's claim and names them. A blocking child may be unclaimed; the parent it leaves paused is named |
| `--step block <parent> <name>` | create a blocking child, pause the parent; same name rule as `new` |
| `--step unpause <id>` | clear a pause that never resolves (phantom, self, or ring) — exactly what `--validate` reports; refuses a pause on reachable live work |
| `--step done <id> --stamp TEXT` | complete: preconditions, `test_command` gate, stamped move to `plan_done/`, parent unpause, prune `plan.md` to the last 5 done entries; `--stamp` is required free text — multi-line accepted, written as indented continuations, and refused when it contains a blank line, before the `test_command` gate runs, since a field ends at the first blank line and the continuations below it are dropped; a leading or trailing blank line is refused with them, which is stricter than that cause and deliberately one rule (DEC-059) |
| `--step status` | regenerate `status.md` from the filesystem; everything below `- Parked:` is carried through verbatim |
| `--audit new <type>` | open `adocs/audit/YYYY-MM-DD_<type>.md` (`.2` suffix on a same-day re-run, never overwrites), record the reconciliation baseline; type must match `[A-Za-z0-9_-]+` |
| `--audit list` | every finding, status, and reference; exit 1 while an open finding has no home or a fence hides one from the scanners |
| `--audit check` | reconcile the tree against the baseline: report and new `tests/` files expected, anything else listed, exit 1. A rename is judged on both halves — the destination is new, the source departed. It is the end of the run: the baseline is stamped `ended`, and the write fence stops dating against it |
| `--session-start` | SessionStart hook: emit stack, derived next step, staleness, planning nudge as JSON additionalContext |
| `--pre-write` | PreToolUse hook (Write|Edit): refuse writes into `plan_done/`, step files outside the plan directories, and reviewer writes other than the evidence the run produced. Under `adocs/audit/` or `tests/` and not there yet, or arrived after the baseline `--audit new` recorded, is permitted; anything that was already there is not, so an earlier report is never overwritten and the run's own red test can still be corrected. The baseline names this run's report, and git says what arrived since; where there is no git to date a file, the report half permits and the tests half refuses, as each did before there was a baseline to read. A run ends at `--audit check`, and an ended run dates nothing: its report is refused by name, and everything else falls back to the no-baseline halves. A path git cannot see at all — one under `.gitignore`, tracked files excepted — is permitted where it stands, since neither snapshot can hold it and it is not on the evidence trail |
| `--pre-command` | PreToolUse hook (Monitor): INV-17 at arm time — refuse a persistent non-primitive arm without `MOLTKE_UNBOUNDED_OK`, refuse any single-match follow, allow bounded streams, ws arms, and other tools |
| `--post-write` | PostToolUse hook: cheap invariant scan, non-blocking by contract |
| `--stop` | Stop hook: refuse to end a turn on violations, stale `status.md`, or unstamped arrivals; capped against deadlock, counted per problem set |
| `--watch LOG REGEX --ceiling DUR [--pid P] [--fail-re RE] [--interval DUR]` | poll LOG for REGEX every `--interval` (default 30s, s/m/h/d suffixes) and terminate on its own: exit 0 printing the matched line, 4 on a `--fail-re` match, 3 when `--pid` is dead after one final scan, 124 at the required `--ceiling`, which is enforced out of band by an interval timer so a caller regex that backtracks or a read that never returns still exits at the ceiling rather than reporting no match (POSIX only; elsewhere the ceiling is checked between polls). Registers under `moltke_watch/` in the git directory git reports, so a linked worktree and a submodule register per-worktree instead of not at all, on arm, signal handlers installed first, and from that write onward records its outcome on every exit path including a kill; a kill before the record exists leaves none, since nothing was armed to acknowledge. Acknowledging a result is deleting its record. Exempt from the INV-11 gate, since the gate's exit 0 would read as a marker seen; `--pid` refused on Windows, and refused before anything is armed unless it is a positive pid within the `pid_t` `kill(2)` can express — 0 and negatives are process groups that answer alive forever, and a wider value used to raise past the backstop. A liveness probe answers dead for any pid it cannot ask about, so a damaged watch record is reported, never raised |

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
The wiring is guarded, not only the event names: the golden carries which tool
matcher selects each hook and which mode it invokes, so unwiring the write fence
or pointing `Stop` at a mode that enforces nothing fails the suite (S142).

## Non-goals

- No daemon, no state outside the repository and `.git/`.
- No network access, no dependencies beyond the Python 3 standard library.
- No automatic fixing: every check refuses or reports; repair is the author's.
- No enforcement of document history (DEC-042): git is the archive.

## Open items

None open.
