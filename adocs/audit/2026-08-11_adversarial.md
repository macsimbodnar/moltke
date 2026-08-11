# Audit 2026-08-11 adversarial

Scope: the whole repository at commit `5625acb` ("Complete S111: the batch's
own fast check, findings fixed"), no boundary. The installed plugin cache was
read for version identity only (0.9.0, gitCommitSha `5625acb`: what runs is
what is committed).
Method: read `bin/moltke.py` end to end (2888 lines) plus hooks, templates,
skills, agents, tests, and both manuals; reproduced every claim against
throwaway fixture repositories built from `tests/fixtures.py` outside this
repository. Nine mutants were planted in a copy of the tree and run against
the suite. Every 2026-08-09 finding still marked `planned` was re-measured
from its own reproduction rather than from a step stamp. Audits run against
the code, not against the specs.

Baseline state, measured first: `python3 -m unittest discover -s tests` → `Ran
445 tests in 121.882s / OK`; `python3 bin/moltke.py --validate` → `moltke: all
checks pass`, exit 0; `python3 bin/moltke.py --audit check` → exit 0, this
report the only footprint; `--audit list` exit 0; `--roadmap` exit 0.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-11_adversarial-F<nn>`. The example below writes that prefix as
`<report>`: a fenced example carrying this report's real stem cannot be told
apart from a real finding that a fence has swallowed, which is INV-14 (S049).

```
### <report>-F01  high  short title

Status: open

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
```

Every finding ends in one of two places: a plan step whose `closes:` field
names it, or a decision entry stating why it will not be acted on, which moves
it to `accepted`. A finding moves to `closed` only after the audit is re-run
and no longer reports it. Fixing without re-running leaves it `planned`.

Six findings: one medium, five low. No high. By DEC-035's severity rule alone
this run would stop the audit loop; DEC-044 leaves that to the user.

No test was added under `tests/`. Every finding below reproduces in a few
lines of shell against a fixture repository, so none needs a test to be
demonstrable, and a red test committed here would block `--step done` — whose
`test_command` gate runs the whole suite — for the triage session that has to
plan these. The red-first test belongs to each fixing step. This is the same
call the 2026-08-09 run made, for the same reason.

## Findings

### 2026-08-11_adversarial-F01  medium  in a linked worktree the `.moltke.local.md` exclusion is written where git never reads it, and the Stop gate then blocks on moltke's own file — with "commit the change" as the printed way out

Status: planned  (S112)

Evidence.

`local_file_lines` (`bin/moltke.py:995`) creates `.moltke.local.md` at the
marked root on every `--session-start` and appends the exclusion to
`git_dir(root) / "info" / "exclude"` (`bin/moltke.py:1010-1022`). `git_dir`
(`bin/moltke.py:1086`) is `git rev-parse --absolute-git-dir`, which in a
linked worktree is the per-worktree directory `.git/worktrees/<name>` — right
for the three state files it was built for (S035: "The path is per-worktree,
which is what these files want to be"), wrong for `info/exclude`, which git
reads from the common directory only.

A repository with a linked worktree (`git worktree add ../linked`), the
linked worktree scaffolded and committed clean:

    $ python3 bin/moltke.py --session-start; echo exit=$?
    exit=0

    $ cat "$(git rev-parse --absolute-git-dir)/info/exclude"
    .moltke.local.md                        # written here…

    $ git check-ignore -v .moltke.local.md; echo exit=$?
    exit=1                                  # …and git does not honour it

    $ git status --porcelain
    ?? .moltke.local.md

    $ python3 bin/moltke.py --stop; echo exit=$?
    moltke: source changed but adocs/worklog.md has no recap heading after the
    last logged prompt; append a recap (step id, what changed, files, tests,
    commit) before ending the turn, or commit the change if the turn that made
    it was already recapped.
    exit=2

The same sequence in the primary worktree: exclusion honoured, porcelain
clean, `--stop` exit 0. `git rev-parse --git-path info/exclude` resolves to
the common directory's file in both layouts (verified: in the linked worktree
it returns `<main>/.git/info/exclude`, and one line there makes
`git status` clean).

The file is not under `RECAP_EXEMPT` (`bin/moltke.py:1405`), so
`porcelain_problems` (`bin/moltke.py:1498`) counts it as changed source.
Deleting it does not help: the next `--session-start` recreates it. The S109
tests (`tests/test_s005_hooks.py:1068-1140`) all build the primary-worktree
layout, where `absolute-git-dir` and the common dir coincide, so the suite
cannot see this.

Impact. In a linked worktree — a configuration MANUAL explicitly supports
("Linked worktrees and submodules work", `MANUAL.md:492`) — every session
leaves an untracked file the Stop gate reads as unrecapped source change, so
an otherwise clean turn exits 2 until a recap is appended or the deadlock cap
waives. Worse, the message's second remedy, "commit the change", steers the
agent into committing the machine-local file, which is the one thing DEC-043
says it must never do ("must never travel in git"), and MANUAL:132-134 and
`templates/moltke_local.md` both state as fact ("keeps it out of git via
`.git/info/exclude`"). A session starting during an audit also lands
`?? .moltke.local.md` in the run's footprint, which `--audit check` reports
as unexpected. Submodules are unaffected: their absolute git dir is its own
common dir.

Suggested resolution. Ask git for the honoured path — `git rev-parse
--git-path info/exclude` — instead of composing it from `--absolute-git-dir`,
and keep the three state files on `git_dir` as they are. A regression test
that builds a linked worktree, runs `--session-start`, and asserts porcelain
is clean pins it; the existing
`test_a_substring_in_the_exclude_file_does_not_satisfy_the_check` shows the
shape.

### 2026-08-11_adversarial-F02  low  on a case-insensitive filesystem the `--pre-write` deny rules are bypassed by case-variant paths, and legitimate case-variant paths are refused with a false message

Status: planned  (S113)

Evidence.

`mode_pre_write` resolves the path (`bin/moltke.py:1214`) and compares
`rel.parts` against lowercase literals (`bin/moltke.py:1246`, `1251`).
`Path.resolve()` does not fold case, and the default macOS filesystem — the
platform this project is developed and installed on — is case-insensitive, so
one path names the fenced file while spelling past the comparison. In a
fixture repository on this machine:

    $ printf '%s' '{"tool_input":{"file_path":"adocs/plan_done/notes.md"}}' \
        | python3 bin/moltke.py --pre-write; echo exit=$?
    moltke: adocs/plan_done/notes.md is under plan_done/, which is immutable
    history. …
    exit=2

    $ printf '%s' '{"tool_input":{"file_path":"ADOCS/PLAN_DONE/notes.md"}}' \
        | python3 bin/moltke.py --pre-write; echo exit=$?
    exit=0

    $ python3 -c "from pathlib import Path; \
        Path('ADOCS/PLAN_DONE/notes.md').write_text('planted'); \
        print(sorted(p.name for p in Path('adocs/plan_done').iterdir()))"
    ['S001_base.md', 'notes.md']

The write lands in the real `adocs/plan_done/`. The reverse direction is a
false refusal: a legitimate step file addressed with different case is
blocked, with a message that is untrue on this filesystem —

    $ printf '%s' '{"tool_input":{"file_path":"Adocs/plan_todo/S099_probe.md"}}' \
        | python3 bin/moltke.py --pre-write; echo exit=$?
    moltke: S099_probe.md looks like a step file but Adocs/plan_todo/S099_probe.md
    is outside the three plan directories. …
    exit=2

Contained: a case-variant write to an existing *step-file-named* path under
`plan_done/` is still blocked (the step-file rule fires on the filename, with
the same wrong message), and the reviewer fence is allow-based, so case
variation can only make it block more, never less.

Impact. The `plan_done/` blanket refusal — a documented behaviour of
`--pre-write` in the specs table, README, and MANUAL — is spelled around by
one case change for any non-step-named path, on the OS family most installs
run on. What leaks is bounded: mutation of a tracked file is still caught
after the fact by INV-7, and a planted untracked file under `plan_done/` is
caught by the Stop stamp gate only if named like a step. DEC-030 scopes
moltke to drift rather than hostile authors, which is why this is low: the
realistic failure is an agent normalising case oddly and being wrongly
refused, or wrongly passed, with a message that misdescribes the tree either
way.

Suggested resolution. Compare case-insensitively when the filesystem does —
e.g. after `resolve()`, also resolve the existing prefix of the path and
compare the parts casefolded when `root` and its case-variant spelling
`samefile()` each other — or simply casefold `rel.parts` for the two deny
rules on darwin. A test with an upper-cased directory spelling, skipped on
case-sensitive filesystems, pins it.

### 2026-08-11_adversarial-F03  low  a pause naming a completed step strands the parent behind refusals that name each other, and the state is one the CLI itself leaves behind

Status: planned  (S114)

Evidence.

A stale pause — `paused_by` naming a step already in `plan_done/` — is a
state `--step done` deliberately leaves when the parent unpause write fails
(`bin/moltke.py:2228-2235`, printing "its pause now names a completed step,
so --step done <parent> will clear it"), and one AGENTS.md §4's hand-edited
workflow can produce directly. In that state, with S003 in `plan_current/`
paused by S004 in `plan_done/`:

    $ python3 bin/moltke.py --validate; echo exit=$?
    moltke: all checks pass
    exit=0

    $ python3 bin/moltke.py --step unpause S003; echo exit=$?
    moltke: S003 is paused by S004, which exists and is reachable. Complete S004
    with --step done S004, which unpauses S003 on its way out; …
    exit=1

    $ python3 bin/moltke.py --step done S004 --stamp "x README MANUAL"; echo exit=$?
    moltke: S004 is in plan_done, not plan_current/; only a step that is actually
    in progress can be completed
    exit=1

    $ python3 bin/moltke.py --step block S003 new_blocker; echo exit=$?
    moltke: S003 is already paused by S004; a step is blocked by one child at a
    time. Complete S004, which unpauses S003, or block S004 itself …
    exit=1

`--step unpause` refuses because `unresolvable_pauses`
(`bin/moltke.py:289-304`) treats a pauser in `plan_done/` as existing and
reachable, and both refusal messages prescribe `--step done S004`, which
refuses. `--step block` on the parent is also impossible. Meanwhile
`--step status` and `--session-start` report `Blocked: S003 … (paused by
S004)` indefinitely, with every check green.

The one CLI door out is `--step done S003` itself, which steps over the stale
pause (S070) — that is, the parent can only be *finished*, never resumed or
re-blocked, and until it is finished the repository states a pause that
resolved days ago.

Impact. Narrower than 2026-08-09_adversarial-F02 (whose phantom and ring
shapes are fixed) but the same signature: commands whose refusals name each
other, over a state the tool itself documents leaving behind. An agent
resuming the parent works under a `Blocked:` banner that is false, and INV-1
counts the step as paused, so unrelated work can be started alongside it —
the drift §4's stack rules exist to prevent.

Suggested resolution. Either let `--step done` and `--step unpause` treat a
pauser found in `plan_done/` identically — `unpause` clearing exactly the
stale pause `done` already steps over keeps DEC-040's rule, since a completed
pauser is by definition not live work — or make `--validate` report the stale
pause so the state is at least visible. The refusal texts should stop
prescribing `--step done` on a step that is already in `plan_done/`.

### 2026-08-11_adversarial-F04  low  `--step unpause` prints a false reason on every non-phantom clear

Status: planned  (S115)

Evidence.

`step_unpause`'s success message is hard-coded to the phantom case
(`bin/moltke.py:2052`):

    print(f"moltke: {step_id} unpaused; {pauser} had no step file in any plan directory.")

Clearing a self-pause — S098's own case — prints a statement that is false of
the repository, about the very file the command just rewrote:

    $ python3 bin/moltke.py --step unpause S003     # S003 paused_by: S003
    moltke: S003 unpaused; S003 had no step file in any plan directory.
    exit=0

S003's step file is in `plan_current/` — the command edited it one line
earlier. A two-step ring prints the same wrong reason ("S004 unpaused; S003
had no step file in any plan directory" while S003 sits in
`plan_current/`).

Impact. Cosmetic but load-bearing text: the success line is the record of
*why* the pause was cleared, quoted into recaps and worklogs, and for the
cycle and self-pause cases it asserts a phantom that never existed. Anyone
tracing the clear later starts from a false premise.

Suggested resolution. `unresolvable_pauses` already returns the kind; print
the matching sentence ("was paused by itself", "was in a ring with …", "had
no step file …").

### 2026-08-11_adversarial-F05  low  the tool's own `--help` omits `--step unpause` and `--audit check`

Status: planned  (S116)

Evidence.

`build_parser` (`bin/moltke.py:2831-2834`):

    modes.add_argument("--step", nargs="+", metavar="OP",
                       help="lifecycle: new <name> | start <id> | block <parent> <name> | done <id> | status")
    modes.add_argument("--audit", nargs="+", metavar="OP",
                       help="audit reports: new <type> | list")

    $ python3 bin/moltke.py --help | grep -A1 -- "--step OP"
      --step OP [OP ...]   lifecycle: new <name> | start <id> | block <parent>
                           <name> | done <id> | status
    $ python3 bin/moltke.py --help | grep -- "--audit OP"
      --audit OP [OP ...]  audit reports: new <type> | list

`STEP_OPS` includes `unpause` (since S090) and `AUDIT_OPS` includes `check`
(since S032); the golden (`tests/golden/cli_surface.txt`) lists both, and
MANUAL and the specs table document both. The golden deliberately reads
argparse actions rather than help text (`tests/surface.py:39-43`), so nothing
pins the help strings, and they have lagged the surface through two
additions.

Impact. `--help` is the one description of the surface that ships inside the
binary and needs no documentation lookup, and it currently denies two
operations exist — including `unpause`, the only repair path for the pauses
INV-1 reports, whose violation text tells the user to run a command `--help`
does not list.

Suggested resolution. Update the two help strings — or derive them from
`STEP_OPS`/`AUDIT_OPS` so they cannot drift again, which also puts them under
the golden indirectly.

### 2026-08-11_adversarial-F06  low  the decisions.md index is missing its two newest entries, and the body is not newest-last

Status: planned  (S117)

Evidence.

    $ grep -c "^- DEC-" adocs/decisions.md
    42
    $ grep -c "^## DEC-" adocs/decisions.md
    44

The index ends at `DEC-042`; `DEC-043` and `DEC-044` have body entries but no
index line. The body also orders them `…DEC-042, DEC-044, DEC-043`, against
AGENTS.md §8 ("newest last") and the file's own header ("ids stable, never
reused, newest last"). AGENTS.md §1 and §8 make the index the lookup device
("never read whole. It opens with an index; grep by id"), so an agent
following the reading protocol greps the index and concludes the two newest
decisions do not exist — DEC-043 being the decision that explains the
machine-local file every session now injects.

No invariant covers the index (INV-9 checks id uniqueness only), so
`--validate` is green; this is the workflow's own state drifting in the exact
way the tooling cannot see.

Impact. A "what did we decide about overrides" grep against the index misses
DEC-043; a reader trusting the index undercounts current constraints by two.
Small today, but the index is the mechanism that keeps decisions.md readable
at all sizes, and it silently stopped being maintained at the S106
compaction.

Suggested resolution. Add the two index lines and swap the two body entries
into id order. If the index is worth keeping, it may be worth a cheap check —
every `## DEC-<nnn>` body id has an index line — as part of INV-9; that is a
decision, not this report's call.

## Verdicts on 2026-08-09_adversarial

All seven findings were `planned` at this commit, with steps S097..S103 in
`plan_done/`. Each was re-measured from its own reproduction in a fresh
fixture repository, not from the step stamps. **None still reproduces.**

- **F01** (four-digit id past S999). With `S999` in plan.md prose, `--step
  new later_work` → exit 1 naming the ceiling, the highest id in use, and
  where it was found (`adocs/plan.md`); nothing written. No longer reproduces.
- **F02** (self-pause and pause rings pass every check, no command clears
  them). `paused_by: S003` on S003 itself → `--validate` exit 1, `INV-1: the
  pause on S003 never resolves: S003 -> S003 … Clear it with bin/moltke.py
  --step unpause S003`; the named command clears it and `--validate` returns
  to exit 0. The two-step ring is reported for both members and clears the
  same way. No longer reproduces. See F03 and F04 above: the neighbouring
  stale-pause case, and the message the clear prints, are new findings in the
  same code.
- **F03** (newline in `--goal`/`--stamp` corrupts plan.md, wedges the Stop
  gate). Both refuse at exit 1 before anything touches the filesystem, with
  the one-line rule stated; plan.md unchanged, no move happened. No longer
  reproduces.
- **F04** (`--step status` drops blank lines from Parked and absorbs what
  follows). A Parked block with internal blank lines and a heading below it
  survives one and two regenerations byte-identical. No longer reproduces.
- **F05** (reviewer fence fails open on non-string `agent_type`). A
  list-valued `agent_type` now blocks at exit 2 exactly like the well-formed
  reviewer payload; JSON `null` still reads as the main thread at exit 0. No
  longer reproduces.
- **F06** (MANUAL names refusals the code does not produce). `--decline`
  against an enabled repository now exits 1 on stderr; `MANUAL.md:164`
  documents the refusal, and `MANUAL.md:205` now states `--audit new` on an
  existing report is *not* among the refusals. No longer reproduces.
- **F07** (`id:` field written once, read never). A hand-copied
  `templates/step_template.md` under a real step name → `--validate` exit 1,
  `INV-6: … declares id: S000, and every check reads the id from the
  filename, which says S050`. No longer reproduces.

Per §10 these move to `closed` on the strength of this re-run; the status
lines in the 2026-08-09 report are the triage session's to flip, as S096 did
for the previous batch.

## Mutation testing

Nine mutants were planted in a copy of the tree at
`/private/tmp/…/scratchpad/mut/` (no `.git`, pristine source restored after
each) and run against the test file naming the behaviour. **All nine were
killed**:

- `step_id_ceiling_problem` → always None: killed, `test_s007_step` (3 failures)
- `unresolvable_pauses` → cycle detection removed, phantom kept: killed,
  `test_s003_invariants` (4 failures)
- `field_value_problem` → always None: killed, `test_s007_step` (2 failures)
- `parked_lines` → blank lines dropped again (S100 reverted): killed,
  `test_s007_step` (1 failure)
- INV-6 `id:` field check → disabled: killed, `test_s003_invariants` (1 failure)
- non-string `agent_type` → waved through again (S101 reverted): killed,
  `test_s005_hooks` (6 failures)
- `--decline` already-enabled → exit 0 again (S102 reverted): killed,
  `test_s006_scaffold` (2 failures)
- `prune_plan` → never drops: killed, `test_s007_step` (1 failure)
- exclude check → substring again (S111 reverted): killed, `test_s005_hooks`
  (1 failure)

Every behaviour added by S097–S111 that was probed is pinned by a
non-vacuous test. The gap the linked-worktree finding exposes is in the
fixtures, not the assertions: every S109 test builds the primary-worktree
layout, where the wrong exclude path and the right one are the same file
(F01).

## Checked and found clean

Recorded so a later run knows what was already looked at.

- `--audit check` classification at this commit: this report is the only
  expected footprint; the pre-existing uncommitted `adocs/worklog.md`
  modification predates the baseline and is correctly not attributed to this
  run.
- `--pre-write` in its documented spellings: `plan_done/` refused, step files
  outside the plan directories refused, reviewer fenced to `adocs/audit/`
  plus new `tests/` files, `tests/../bin/…` normalised, malformed
  `agent_type` fenced, `null` read as main thread.
- `--step done` refusal chain: duplicate id in `plan_done/`, missing testing
  row, missing/short stamp, suite-gate failure; nothing half-applied on any
  refusal probed.
- `--step unpause` against a pause on reachable live work: refused, as
  DEC-040 requires.
- The nine 0.9.0-era templates: `AGENTS.md` and `CLAUDE.md` byte-identical to
  their shipped templates; scaffolded documents carry their guidance in
  comments and fenced examples that no scanner counts.
- Golden surface: `tests/golden/cli_surface.txt` matches the parser, ops
  lists, hooks, marker keys, and skills; MANUAL and specs document every op
  including the two `--help` omits (F05).
- Hook wiring (`hooks/hooks.json`): five events, all shelling to
  `bin/moltke.py`, matching the specs table. `PreToolUse`/`PostToolUse` match
  `Write|Edit` only — `Bash` is out of scope by DEC-022; no `.ipynb` surface
  exists in the plan directories for `NotebookEdit` to matter today.
- Suite: 445 tests, no skips, green at `5625acb`; `--validate`, `--audit
  list`, `--audit check`, `--roadmap` all exit 0.

Observations, not findings: the `status.md` Parked note "Cache is 0.8.0;
0.9.0 ships S105-S110" is stale — `installed_plugins.json` shows 0.9.0
installed today at commit `5625acb` — and the note parking the seven
`planned` findings is discharged by this run's verdicts. Both lines are the
human's to clear (§2).
