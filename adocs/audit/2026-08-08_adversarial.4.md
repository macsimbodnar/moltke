# Audit 2026-08-08 adversarial

Scope: what was examined, at which commit.
Method: how it was examined. Audits run against the code, not against the specs.
An audit that only confirms the documentation is a documentation review.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-08_adversarial.4-F<nn>`. The example below writes that prefix as
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

## Scope of this run

Commit `2b8bfacfe60a3aaeba75f304a4f48414184208fd`, whole repository: `bin/`,
`hooks/`, `agents/`, `skills/`, `templates/`, `tests/`, and the tracked
documentation. `adocs/audit/` was not read as review material.

Baseline observations, all taken before any finding below:

- `python3 -m unittest discover -s tests` — `Ran 376 tests in 155.520s  OK`
- `python3 bin/moltke.py --validate` — `moltke: all checks pass`, exit 0
- `python3 bin/moltke.py --roadmap` — exit 0, 84 done, 1 left

Reproductions ran against throwaway repositories built by `tests/fixtures.py`
under the scratch directory, plus one monorepo fixture (git top level above the
marked root). Nothing in this repository was written except this report.

## Findings

### 2026-08-08_adversarial.4-F01  high  `--step new` and `--step block` accept any name, and an ordinary hyphen creates a step no check can see

Status: closed

Closed 2026-08-09 by S088, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

`bin/moltke.py:1739` builds the step path straight from the operand:

    path = root / DOCS / "plan_todo" / f"{step_id}_{name}.md"

`bin/moltke.py:1801` does the same for the blocking child. Nothing validates
`name`, while `STEP_FILE_RE` (`bin/moltke.py:82`) only recognises
`^(S\d{3})_[A-Za-z0-9_]+\.md$`, so any name outside `[A-Za-z0-9_]+` produces a
file that `plan_steps` never returns.

The ordinary case, in a fixture repository that passes every check:

    $ python3 bin/moltke.py --step new fix-parser --goal "fix the parser"
    moltke: created adocs/plan_todo/S004_fix-parser.md and listed S004 in plan.md.
    Reorder plan.md if it does not belong last.
    exit=0

    $ ls adocs/plan_todo
    S002_pending.md
    S004_fix-parser.md

    $ python3 bin/moltke.py --validate
    VIOLATION: INV-3: plan.md lists S004 but no step file exists in plan_todo/,
    plan_current/, or plan_done/; create it with --step new, or fix the id in plan.md
    1 violation(s).
    exit=1

    $ python3 bin/moltke.py --step start S004
    moltke: S004 does not exist; create it with --step new <name>
    exit=1

The violation's own remedy makes it worse: `--step new` allocates from
`next_step_id`, which reads `plan.md`, so a second run creates S005 and leaves
S004 listed forever. The file exists on disk, so `--step new fix_parser` does
not reuse the name either. There is no CLI path back; the repository is fixed
only by renaming the file or editing `plan.md` by hand — the two things
`--step` exists to avoid.

The hostile case is the same defect with a separator. `write_step` calls
`path.parent.mkdir(parents=True, exist_ok=True)` (`bin/moltke.py:1695`), so the
write lands wherever the name points:

    $ python3 bin/moltke.py --step new "../../../../../pwned"
    moltke: created adocs/plan_todo/S006_../../../../../pwned.md and listed S006 in plan.md.
    exit=0

    $ ls <scratch>/          # one directory above the marked root
    pwned.md
    t1

`--step new "../../../escaped"` wrote `adocs/escaped.md` and left a stray
directory `adocs/plan_todo/S005_..` behind. The printed path is computed
lexically with `relative_to`, so it still reads as contained — word for word the
`--audit new` defect that S040 fixed (2026-08-07_adversarial-F09) at
`bin/moltke.py:2340`, in the sibling that was never given the same rule.

`--step block` inherits it and ends worse, because it pauses the parent after
creating the child:

    $ python3 bin/moltke.py --step block S003 "../../../blocked"
    moltke: S007 created in plan_current/ blocking S003, which is now paused.
    exit=0

    $ cat adocs/plan_current/S003_active.md
    id:         S003
    goal:       active
    paused_by: S007  # 2026-08-08

    $ python3 bin/moltke.py --step done S003 --stamp "README MANUAL checked"
    moltke: S003 is paused by S007; complete S007 first, which unpauses this step automatically
    $ python3 bin/moltke.py --step done S007 --stamp "README MANUAL checked"
    moltke: S007 does not exist
    $ python3 bin/moltke.py --step start S007
    moltke: S007 does not exist; create it with --step new <name>

Impact.

Any agent or user who types a hyphenated step name — `fix-parser`,
`audit-followup` — gets a success message and a repository that fails
`--validate`, which the `Stop` hook enforces, so the turn cannot end. The
step is invisible to `derived_next`, `status.md`, `--roadmap`, and `--step
start`, and the printed remedy allocates a different id. `skills/step/SKILL.md:8`
states "Every operation runs through the checker, so no transition can leave the
plan in a state that violates the invariants"; this transition does, and reports
exit 0. With a separator in the name the same operand writes a file outside
`adocs/`, and outside the marked root entirely, from a mode whose whole job is
to keep the plan tree consistent. `--step block` additionally leaves a parent
paused by a step that exists nowhere, which no `--step` operation can clear
(see F03).

Suggested resolution.

Validate `name` against `[A-Za-z0-9_]+` in `step_new` and `step_block` before
anything touches the filesystem, refusing with the same shape `_mode_audit`
already uses for the audit type, and say in the refusal that the plan reader
only recognises that character set. A test that runs `--step new fix-parser` and
asserts `--validate` still exits 0 would have caught this.

### 2026-08-08_adversarial.4-F02  medium  `--step done` overwrites an existing `plan_done/` file, destroying immutable history, and exits 0

Status: closed

Closed 2026-08-09 by S089, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

`bin/moltke.py:1915-1918`:

    destination = root / DOCS / "plan_done" / path.name
    try:
        destination.write_text(with_field(read_file(path), "done", stamp),
                               encoding="utf-8")

Nothing checks whether `destination` already exists. A duplicate id across
`plan_current/` and `plan_done/` — the state INV-6 exists to report, and the
state 2026-08-08_adversarial.3-F05 describes reaching by following two violation
messages, or a `git checkout` of a step file deleted by a completion — is
enough. (I did not reproduce the branch-merge route to the same state; INV-6
firing is the only precondition this needs.)

    $ cat adocs/plan_done/S001_base.md
    id:         S001
    goal:       base
    done: 2026-08-01 done

    $ python3 bin/moltke.py --validate
    VIOLATION: INV-1: plan_current/ holds 2 non-paused steps (S001, S003), limit 1; ...
    VIOLATION: INV-6: duplicate step id S001 in plan_current and plan_done; ...
    exit=1

    $ python3 bin/moltke.py --step done S001 --stamp "README MANUAL checked"
    moltke: no "test_command" in .moltke.json, so nothing here ran the suite. ...
    moltke: S001 completed and moved to plan_done/. Commit it; the move is the last action of the step.
    exit=0

    $ cat adocs/plan_done/S001_base.md
    id:         S001
    goal:       base
    done:      README MANUAL checked

The completed step's recorded body and its original `done:` stamp are gone.
`locate_step` (`bin/moltke.py:1658-1665`) scans `plan_todo`, `plan_current`,
`plan_done` in that order and returns the first hit, so the `plan_current` copy
is what gets completed and the `plan_done` copy is what gets overwritten.
`step_start` has the same shape at `bin/moltke.py:1771` — `path.rename()` over
an existing destination is silent on POSIX.

Impact.

INV-7 states that a file under `plan_done/` never changes after the commit that
added it, `--pre-write` blocks agents from editing that directory
(`bin/moltke.py:1153`), and the specs CLI table says of `--step` that "no
transition may leave INV-1..INV-7 violated". The one tool that is supposed to be
the safe way to move a step performs exactly the write the fence forbids, with
no warning and exit 0. The loss is recoverable from git — INV-7 reports it on
the next `--validate` — but only if it is noticed before the same commit that
completes the step also records the clobbered file.

Suggested resolution.

Refuse in `step_done` when `destination.exists()`, naming the duplicate id and
INV-6; likewise in `step_start` when the target name is already in
`plan_current/`. Both are pre-flight checks in the sense S070 already
established for writability.

### 2026-08-08_adversarial.4-F03  medium  a `paused_by` naming a step that exists nowhere passes every invariant and cannot be cleared by any command

Status: closed

Closed 2026-08-09 by S090, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

INV-1 counts a step as non-active whenever `paused_by` is non-empty
(`bin/moltke.py:227-228`), and nothing anywhere checks that the named pauser
exists. INV-3's reverse direction covers exactly this shape for `plan.md`
(S024), and `step_done` covers it for a pauser already in `plan_done/` (S070,
`bin/moltke.py:1863-1871`), but a pauser that is in none of the three
directories is unhandled.

A fixture repository with `paused_by: S999` written into the one step in
`plan_current/`, and `status.md` regenerated to match:

    $ python3 bin/moltke.py --validate
    moltke: all checks pass
    exit=0

    $ python3 bin/moltke.py --roadmap
    S001 ▏█░▶▕ S003
         └ 1 done ┘ └ 2 left
         now  S003  active [paused by S999  # 2026-08-08]

    $ python3 bin/moltke.py --step done S003 --stamp "README MANUAL checked"
    moltke: S003 is paused by S999; complete S999 first, which unpauses this step automatically
    exit=1

`--step done S999` answers "S999 does not exist" and `--step start S999`
answers "S999 does not exist; create it with --step new <name>", so no
`--step` operation reaches the field.

Impact.

The prime directive is that project state is derivable from tracked files
alone. Here the filesystem says a step is waiting on work that does not exist,
every check says the repository is clean, and the only way forward is to edit a
step file by hand. F01 reaches this state through the CLI with no hand-editing
at all. INV-1 is also weakened generally: any step can be parked outside the
active count by a `paused_by` value that means nothing.

Suggested resolution.

Report a `paused_by` whose id has no step file in any plan directory, as INV-3
already reports a listed id with no file, and name the command that clears it.
Alternatively extend the S070 stale-pause path in `step_done` to cover a pauser
that does not exist as well as one already completed.

### 2026-08-08_adversarial.4-F04  medium  `--scaffold` and `--decline` still end in a Python traceback, which MANUAL says no mode does since 0.6.0

Status: closed

Closed 2026-08-09 by S091, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

`main` dispatches both before the backstop that catches everything else
(`bin/moltke.py:2524-2527` versus the `try:` at `bin/moltke.py:2536`), and
neither `mode_scaffold` (`bin/moltke.py:1602`) nor `mode_decline`
(`bin/moltke.py:1646`) guards its writes.

In a directory that is not writable:

    $ python3 bin/moltke.py --scaffold
    Traceback (most recent call last):
      File "bin/moltke.py", line 2568, in <module>
        sys.exit(main())
      File "bin/moltke.py", line 2525, in main
        return mode_scaffold()
      File "bin/moltke.py", line 1602, in mode_scaffold
        target.write_bytes((TEMPLATE_ROOT / template).read_bytes())
    PermissionError: [Errno 13] Permission denied: '<dir>/.moltke.json'
    exit=1

    $ python3 bin/moltke.py --decline
    Traceback (most recent call last):
      ...
      File "bin/moltke.py", line 1646, in mode_decline
        path.write_text(json.dumps({"schema": 1, "enabled": False}, indent=2) + "\n",
    PermissionError: [Errno 13] Permission denied: '<dir>/.moltke.json'
    exit=1

`MANUAL.md:178` states "Since 0.6.0 no mode ends in a Python traceback", and
`.claude-plugin/plugin.json` says `"version": "0.6.0"`. `README.md:71-76` and
`MANUAL.md:164-169` both assign exit 1 to findings on stdout or refusals on
stderr; a traceback is neither.

The partial-apply case is worse than the message. With `adocs` present as a
regular file, so the fifth entry of `SCAFFOLD_MAP` fails and the first four
have already landed:

    $ python3 bin/moltke.py --scaffold
    ... FileExistsError: [Errno 17] File exists: '<dir>/adocs'
    exit=1
    $ ls -a
    .cursor  .moltke.json  AGENTS.md  CLAUDE.md  adocs
    $ python3 bin/moltke.py --validate
    VIOLATION: INV-3: adocs/plan.md is missing; create it and list every step
    exit=1

The marker is written first in `SCAFFOLD_MAP`, so the failed scaffold leaves an
enabled repository with no plan tree: every hook is now live against a tree that
was never built.

Impact.

`--scaffold` is what the `init` skill runs, so this is the first command a new
user runs, and the failure mode is a stack trace naming pathlib internals rather
than the path and what to do. Any operator parsing exit codes per the documented
table gets a `1` with a traceback on stderr. The half-scaffolded repository then
enforces hooks it has no state for.

Suggested resolution.

Move both setup modes inside a guard of their own — they cannot use `main`'s
backstop, which runs after the marker gate — turning an `OSError` into a
refusal that names the path. Consider ordering the marker write last, or
removing what was created when the scaffold cannot complete, so a failed setup
leaves an unmarked repository rather than an enabled empty one.

### 2026-08-08_adversarial.4-F05  medium  every invariant run spawns one `git rev-parse --show-prefix` per path: 257 processes and 7 seconds per `--stop`

Status: closed

Closed 2026-08-09 by S092, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

`git_prefix` (`bin/moltke.py:1315-1330`) shells out on every call, and
`from_git_path` / `to_git_path` (`bin/moltke.py:1333-1345`) call it once per
path they translate. INV-7 translates every `plan_done/` entry twice
(`bin/moltke.py:428-431`), once to build the blob spec list and again in the
loop.

Instrumented run over this repository, wrapping `_git_run` and calling
`run_checks` directly:

    violations: 0
    git subprocess calls: 263
        257  rev-parse --show-prefix
          2  log --reverse
          2  cat-file --batch
          1  status --porcelain
          1  show HEAD:adocs/decisions.md
    run_checks wall time: 6.99s

Memoising that one constant is the whole difference:

    as shipped:        7.08s
    git_prefix cached: 0.42s

End to end, on this repository:

    $ python3 bin/moltke.py --validate    -> real 7.05, 6.98, 6.96
    $ echo '{}' | python3 bin/moltke.py --stop  -> 7.31s total

Impact.

`--stop` runs `run_checks` on every turn end, so every turn in this repository
pays about seven seconds of subprocess spawning, and the cost grows linearly
with `plan_done/` — 87 files today. `adocs/specs.md:943` states the constraint
being violated: "It runs on every prompt, so startup cost matters and
dependencies are unacceptable." Nothing is incorrect in the output; the defect
is that the S081 fix was written as a per-call query of a value that is constant
for the process.

Suggested resolution.

Compute the prefix once per root and cache it (module-level dict keyed by root,
or resolve it once in `run_checks` and pass it down). A test asserting an upper
bound on `_git_run` calls for one `run_checks` over a fixture with N completed
steps would keep it from coming back.

### 2026-08-08_adversarial.4-F06  low  INV-8's history violation prints a `git show` command that fails when the marked root is below the git top level

Status: closed

Closed 2026-08-09 by S093, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

`bin/moltke.py:476` builds the correct blob spec, `spec = to_git_path(root, rel)`,
and `bin/moltke.py:482` uses it in the deletion message. The high-water-mark
message at `bin/moltke.py:512` uses the repository-relative path instead:

    f"clears: git show {required_sha[:8]}:{rel}. A reversal is a new entry marking "

In a monorepo fixture — git top level above, marked root at `packages/foo` —
with one line removed from `decisions.md` and committed:

    $ python3 bin/moltke.py --validate
    VIOLATION: INV-8: adocs/decisions.md no longer contains, in order, the lines it
    had at commit 247fdd70; ... Put the removed content back where it was and this
    clears: git show 247fdd70:adocs/decisions.md. ...

    $ git show 247fdd70:adocs/decisions.md
    fatal: path 'packages/foo/adocs/decisions.md' exists, but not 'adocs/decisions.md'
    hint: Did you mean '247fdd70:packages/foo/adocs/decisions.md' aka '247fdd70:./adocs/decisions.md'?
    exit=128

INV-7's twin messages are correct in the same tree, which is what makes this a
missed line rather than a missed idea:

    VIOLATION: INV-7: adocs/plan_done/S001_base.md no longer matches the version that
    landed at commit 16c91917; ... git show 16c91917:packages/foo/adocs/plan_done/S001_base.md
    > adocs/plan_done/S001_base.md.

Impact.

INV-12 requires every blocking exit to carry a message stating exactly what to
do to unblock, and `--stop` repeats invariant violations verbatim. In a project
vendored into a monorepo — the case S081 exists for — a user whose
`decisions.md` lost a line is blocked and handed a command that exits 128. The
violation itself is correct; only the remedy is unusable.

Suggested resolution.

Use `spec` rather than `rel` in that message, as the deletion message two blocks
above already does, and cover it with the nested-root fixture
`tests/test_s003_invariants.py:371` already builds.

### 2026-08-08_adversarial.4-F07  low  `--step status` silently deletes Parked entries that are not indented, while the docs promise they are carried through untouched

Status: closed

Closed 2026-08-09 by S094, on the 2026-08-09_adversarial re-run at
0.7.0 (beea5f9): re-measured from this finding's own reproduction and it no
longer reproduces.

Evidence.

`parked_lines` (`bin/moltke.py:1948-1964`) keeps a line after `- Parked:` only
when it starts with two spaces or a tab, and `break`s out of the loop on the
first line that does not:

    if line.startswith(("  ", "\t")) or not line.strip():
        if line.strip():
            kept.append(line.rstrip())
    else:
        break

A `status.md` whose Parked entries are written flush left, which is what the
shipped template invites by ending at `- Parked:` with no example item:

    - Blocked: none
    - Parked:
    - revisit the cache design
    - ask Max about retries

    $ python3 bin/moltke.py --step status
    moltke: regenerated adocs/status.md from the filesystem.

    $ tail -1 adocs/status.md
    - Parked:

Both entries are gone, with no message. `skills/step/SKILL.md:69` says "The
Parked list is human memory and is carried through untouched", `MANUAL.md:142`
says `--step status` regenerates "keeping the Parked list", and
`bin/moltke.py:1949` says "Carry the human-written Parked list through a
regeneration".

Impact.

`--step status` runs at the end of every work turn, and both `--session-start`
and `--stop` steer the user into it whenever `status.md` disagrees with the
filesystem, so the deletion happens on a routine command rather than a rare one.
`adocs/specs.md:992-998` records that `status.md` earns its place specifically
because "it holds the Parked list, which nothing else does" — this is the one
piece of content in the file that is not derivable from anywhere else, so a lost
entry is lost outright unless it was committed first.

Suggested resolution.

Keep every line after `- Parked:` until the next unindented heading, or refuse
to regenerate when the Parked block is in a shape the reader does not
understand, or ship a template with an indented example item so the accepted
shape is visible. Whichever is chosen, a test that writes an unindented parked
entry and asserts it survives `--step status` is what pins it.

## What was checked and found sound

Recorded so a later run knows what was already measured, not as reassurance.

- The `Stop` deadlock cap: six consecutive stops on a persistent problem read
  `2 2 2 0 0 0`, and five more after a new prompt heading read `2 2 2 0 0`,
  which is the documented per-turn reset (S047).
- The `--pre-write` fence: `plan_done/` write blocked with exit 2, a scoped
  `moltke:adversarial_reviewer` writing `bin/moltke.py` blocked with exit 2, the
  same agent writing under `adocs/audit/` allowed.
- INV-7 in a monorepo fixture: both the working-tree half and the history half
  name the right path and print a `git show` spec that resolves.
- `--scaffold` run twice is idempotent ("nothing to do; the workflow is already
  set up here"), and a freshly scaffolded repository passes `--validate` and
  `--stop`.
- `--session-start` emitted its JSON envelope on a tree whose `plan_current` was
  a regular file rather than a directory, exit 0.
- The surface golden and its specs/MANUAL cross-check (`tests/test_s009_surface.py`)
  read argparse actions, declared skills, hook events, and `MARKER_KEYS`, and the
  marker-key test plants an invalid value per declared key, so the list cannot go
  decorative.
- Mutation coverage of the twelve most recent behaviours. Each was reverted by
  one line in a scratch copy of the tree at this commit, and the full suite was
  run against it. Every one of the twelve was caught, so none of these tests is
  vacuous:

      S082 block-already-paused        FAILED (failures=2)
      S078 INV-16 comparison           FAILED (failures=4)
      S050 rename arrival              FAILED (failures=4)
      S087 payload_str typing          FAILED (failures=10, errors=1)
      S086 roadmap exit 0              FAILED (failures=1)
      S081 git_prefix                  FAILED (failures=3, errors=1)
      S075 INV-14 comments             FAILED (failures=1)
      S070 done pre-flight             FAILED (failures=2)
      S069 stamp gate step filter      FAILED (failures=4)
      S085 testing.md stripped         FAILED (failures=1)
      S062 done writes destination     FAILED (failures=1)
      S077 audit new-file predicate    FAILED (failures=1)

  The reversions were, in order: `paused_by` never set in `step_block`;
  `inv_16_prime_directive_readable` returning early instead of comparing;
  `_arrives_here` dropping `R`/`C`; `payload_str` returning the raw value;
  `mode_roadmap` returning `EXIT_BLOCK` on `OSError`; `git_prefix` returning
  `""`; `hidden_findings` reading the report without `strip_comments`;
  `step_done` skipping the writability pre-flight; the stamp gate dropping its
  `STEP_FILE_RE` filter; INV-5 reading `testing.md` raw; `step_done` stamping in
  place before the move; `_is_new_file` reverting to the pre-S050 predicate.

## What could not be confirmed

- Whether Claude Code's `PreToolUse` matcher `"Write|Edit"` in
  `hooks/hooks.json` also matches `MultiEdit` or `NotebookEdit`. If it does not,
  the reviewer fence and the `plan_done/` refusal never run for those tools.
  This needs the live hook surface to settle and was not reproducible here.
