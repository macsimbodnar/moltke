# Audit 2026-08-08 adversarial

Scope: `bin/moltke.py` at commit `4f8377f`, version 0.6.0, plus `hooks/hooks.json`,
`agents/adversarial_reviewer.md`, `skills/`, `templates/`, `tests/`, and the claims
`README.md`, `MANUAL.md`, and `adocs/specs.md` make about them.

Method: two jobs. First, a verdict on each of the six findings in
`adocs/audit/2026-08-08_adversarial.md`, decided by re-running that finding's own
reproduction against the code at `4f8377f` in throwaway repositories under
`/private/tmp`, never against the step files, the stamps, or the commit messages.
Second, a fresh pass over the six steps that landed since (S060..S065), including
mutation testing: thirteen behaviours those steps introduced or depend on were each
deleted in a copy of the repository outside it and the full suite re-run, to see
whether the tests that name them bite.

Baseline at the start of the run:

```
$ python3 -m unittest discover -s tests
Ran 308 tests in 98.439s
OK
$ python3 bin/moltke.py --validate
moltke: all checks pass
$ git status --porcelain -uall
?? adocs/audit/2026-08-08_adversarial.2.md
```

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-08_adversarial.2-F<nn>`. The example below writes that prefix as
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

Summary: 12 new findings. 1 high, 5 medium, 6 low. All six findings of the
previous run no longer reproduce; every one of the six steps did what its stamp
claims. The pattern in what is new is the same one four audits have now named — a
rule tightened in one place and its twin not, and this run adds a second shape: a
defect moved rather than removed.

S060 replaced F01's silent exit 1 with a blocking exit 2 that no longer counts
against the deadlock cap, so the same stray file now wedges the session instead of
disarming it (F01), and takes the `SessionStart` JSON channel down with it (F02).
S060 widened which porcelain entries reach the stamp gate without widening what an
entry has to be, so `--scaffold`'s own `.gitkeep` blocks `Stop` in any repository
that already had commits (F03). S062 moved `--step done`'s point of no return to
the front and left the third mutation behind it, turning a recoverable partial
failure into an unrecoverable one (F04). S050's `porcelain_paths` still has an
un-updated twin in INV-7, whose remedy for a rename inside `plan_done/` is a shell
command that truncates a file (F05). And S063's structural guard against the whole
recurring class — "a call site pairing `strip_guidance` with `read_text` is a test
failure now" — was made inert by S064 one step later, demonstrated by adding a new
unguarded consumer with the suite green (F06).

## Verdicts on the 2026-08-08 findings

One line each, decided by running the tool at `4f8377f`. Ids are written inline
rather than as headings, because a `###` heading carrying another report's stem
is an INV-10 violation in this file.

- **`2026-08-08_adversarial-F01`** (`--stop` exits 1 with a traceback when a step
  file staged into `plan_done/` is not on disk) — **no longer reproduces.** All
  three shapes from the finding now exit 2 with a message and no traceback: `RD`
  and `AD` give `moltke: INV-7: adocs/plan_done/S003_active.md changed under
  plan_done/; history is immutable: restore it with git checkout -- ...`, and a
  wholly untracked `adocs/plan_done/` gives the recap and stamp complaints. The
  control (`R ` with the destination present) still gives the INV-5, staleness and
  stamp problems, exit 2. See F03 below for what the same `-uall` change did to a
  repository that has just been scaffolded, and F01 below for the class of failure
  that now blocks forever instead.
- **`2026-08-08_adversarial-F02`** (a prompt-append failure freezes the `Stop`
  waiver's clock and restores the `.2-F01` off switch) — **no longer reproduces.**
  Eight turns with the worklog `chmod 444`, `--log-prompt` then `--stop` each turn,
  read `[2, 2, 2, 2, 2, 2, 2, 2]` with `{"session_id":"s1"}` and with `{}`; the
  stop state carries the breadcrumb, `{"turn": "|s1|1|2026-08-08T14:14+02:00#9",
  "fingerprint": "2eeaf685f6a2d32d", "count": 1}`. The no-deadlock property still
  holds: eight retries inside one turn read `[2, 2, 2, 0, 0, 0, 0, 0]` both with a
  writable and with an unwritable worklog.
- **`2026-08-08_adversarial-F03`** (`--step done` writes the stamp and unpauses
  before it refuses) — **no longer reproduces as measured.** The finding's fixture,
  `plan_done/` absent and `S001` paused by `S002`, gives `moltke: could not write
  adocs/plan_done/S002_child.md ([Errno 2] ...); nothing was changed`, exit 1, with
  `plan_current` unchanged, no `done:` line on the child, `paused_by` intact, and
  `--validate` still exit 0. A residual with the same shape is F04 below.
- **`2026-08-08_adversarial-F04`** (INV-13 does not scan `adocs/specs.md`) — **no
  longer reproduces.** The finding's shape, two example fences straddling the
  prime-directive heading with their closers removed, now gives `VIOLATION: INV-16:
  adocs/specs.md states a prime directive that a code fence swallows ...`, exit 1,
  `--stop` exit 2, and no planning nudge; the control with both fences closed is
  exit 0 and silent. An odd count in `specs.md` is now INV-13, exit 1. A narrower
  residual is F12 below.
- **`2026-08-08_adversarial-F05`** (two decode policies, one non-UTF-8 byte turns
  every mode into a traceback) — **no longer reproduces.** A latin-1 byte appended
  to `adocs/plan.md`, to an audit report, to `adocs/decisions.md`, to a `plan_done/`
  step file and to `adocs/worklog.md` leaves `--validate`, `--post-write`, `--stop`,
  `--session-start`, `--step status` and `--audit list` all at exit 0 with no
  `UnicodeDecodeError`. The same byte in `.moltke.json` gives the marker-unreadable
  violations, not a traceback.
- **`2026-08-08_adversarial-F06`** (MANUAL says the violation names the tampering
  commit) — **no longer reproduces.** `MANUAL.md:322-326` now reads "The commit the
  violation names is the one it compares against — for a `plan_done/` file the
  commit that added it, for `decisions.md` the most recent version that had not
  already lost something — not the commit that did the damage, which moltke never
  identifies", which is what the messages do.

I did not re-verify `2026-08-07_adversarial.2-F06` (no Stop cap without git,
`accepted` under DEC-031) or the installed-plugin verdict of
`2026-08-06_adversarial-F02`: the first is accepted and unchanged, the second turns
on what version is in `~/.claude/plugins/cache`, outside this repository.

## Findings

### 2026-08-08_adversarial.2-F01  high  the S060 backstop makes `--stop` block forever on an unreadable path: the deadlock cap never advances, and every problem collected in the same call is dropped

Status: open

Evidence: `mode_stop` collects problems (`bin/moltke.py:1233`), then reads paths
that are outside `run_checks` — `status_disagreements`, `recap_pending`, the
porcelain gates — and only writes the retry counter at `bin/moltke.py:1280-1297`,
after all of them. An `OSError` from any of those reaches `main`'s backstop
(`bin/moltke.py:2178-2186`), which returns `EXIT_BLOCK` for `--stop`. Nothing was
printed, and no state file was written, so the count never reaches `STOP_CAP`.

A broken symlink named like a step file, which is what a moved-away target or a
half-applied patch leaves behind:

```
$ ln -s nowhere.md adocs/plan_todo/S050_lost.md
$ for i in 1 2 3 4 5; do moltke.py --stop <<< '{"session_id":"s1"}'; done
  --stop #1: exit=2 stderr="moltke: could not read the repository ([Errno 2] No such file or directory: '.../adocs/plan_todo/S050_lost.md'). Fix the path named above, then run bin/moltke.py --validate."
  --stop #2: exit=2   (identical)
  --stop #3: exit=2   (identical)
  --stop #4: exit=2   (identical)
  --stop #5: exit=2   (identical)
  stop state file written: False
```

The same for a directory where a step file belongs — the fixture S060's own specs
note names — and there the message is not just terse but strictly worse than what
the other modes print for the identical tree:

```
$ mkdir adocs/plan_todo/S050_thing.md
$ moltke.py --stop
exit=2, stderr = 1 line:
moltke: could not read the repository ([Errno 21] Is a directory: '.../adocs/plan_todo/S050_thing.md'). Fix the path named above, then run bin/moltke.py --validate.

$ moltke.py --post-write
exit=2, stderr = 6 lines:
moltke: INV-1 could not read the repository ([Errno 21] Is a directory: ...). A check that cannot look is not a check that passed: fix the path it names, then run bin/moltke.py --validate
moltke: INV-2 could not read ...   (INV-3, INV-4, INV-5, INV-6 likewise)

$ moltke.py --validate
exit=1, 6 violations, same text
```

`--stop` had those six in `problems` and threw them away. A third trigger is a
worklog that cannot be read (`chmod 000 adocs/worklog.md`), where `recap_pending`
raises after `run_checks` has already recorded a real INV-3 violation: eight
retries inside one turn read `[2, 2, 2, 2, 2, 2, 2, 2]` against `[2, 2, 2, 0, 0,
0, 0, 0]` for the same repository with the worklog readable. A fourth is `git`
missing from `PATH`, where `_git_lines` raises instead of returning `None`, so the
documented "no git, the check abstains" becomes `VIOLATION: INV-7 could not read
the repository ([Errno 2] No such file or directory: 'git')` and every `--stop`
blocks.

Impact: a session that cannot be ended. `MANUAL.md:406` states the opposite as a
property — "**Otherwise the Stop hook can never wedge a session, and never goes
quiet either.** If it blocks three times on the same problems inside one turn, the
fourth attempt is allowed with a warning" — with `MANUAL.md:396` naming the sole
exception, a repository without git. Neither the count nor the waiver runs on this
path. INV-12 and DEC-006 make no-deadlock a property of the tool, and the message
that blocks says "Fix the path named above" when nothing was printed above it. The
previous run's F01 was the same code path failing open (exit 1, everything off);
S060 turned it into failing shut, and the two halves the fix added — `run_checks`
catching per invariant, `main` catching everything else — disagree about what
happens to work already done: `--post-write` and `--validate` print it, `--stop`
discards it.

Suggested resolution: `mode_stop` should own its own failure rather than delegating
to the backstop — wrap the sections after `run_checks` so an `OSError` becomes one
more entry in `problems`, print, count, and let the cap apply as it does to
everything else. Red-first cases: a broken symlink and a directory named like a
step file, each asserting that five consecutive `--stop` calls in one turn read
`2 2 2 0 0` and that the INV-1..INV-6 read failures are printed. Not applied here.

### 2026-08-08_adversarial.2-F02  medium  on the same trigger `--session-start` prints no JSON at all, so the one channel that reaches the model goes silent on an exit 0

Status: open

Evidence: the backstop returns `EXIT_OK` for `--session-start`
(`bin/moltke.py:2186`) after printing to stderr (`bin/moltke.py:2184`).
`mode_session_start` builds its whole payload before the single
`print(json.dumps(...))` at `bin/moltke.py:902-905`, so an `OSError` anywhere in
`plan_steps`, `derived_next`, `status_disagreements` or `planning_pending` loses
all of it:

```
$ mkdir adocs/plan_todo/S050_thing.md
$ moltke.py --session-start <<< '{}'
exit=0
stdout: ''
stderr: moltke: could not read the repository ([Errno 21] Is a directory: '.../adocs/plan_todo/S050_thing.md'). Fix the path named above, then run bin/moltke.py --validate.

$ ln -s nowhere.md adocs/plan_todo/S050_lost.md      # separate fixture
$ moltke.py --session-start <<< '{}'
exit=0
stdout: ''
```

Impact: `adocs/specs.md:545-546` states that `--session-start` "emits
`hookSpecificOutput.additionalContext` JSON, the only channel that reaches the
model", and S014 built the prompt-failure breadcrumb on that channel precisely
because a zero-exit hook's stderr reaches nobody. Exit 0 with empty stdout is the
one combination where the message cannot be seen: the agent starts the session with
no stack, no derived next step, no staleness warning, and no planning nudge, and
nothing says why. The breadcrumb itself is not lost — `take_log_failure` is never
reached, so it survives to a later session — but a session that has this problem is
exactly the session that will not hear about it. Same trigger as F01, different
failure mode, so a fix for one does not fix the other.

Suggested resolution: give `mode_session_start` its own handler that puts the error
text into `additionalContext` and still prints the JSON envelope, rather than
returning through a backstop that cannot know what the mode's output contract is.
Red-first case: a directory named like a step file, asserting `--session-start`
stdout parses as JSON and mentions the path. Not applied here.

### 2026-08-08_adversarial.2-F03  medium  the stamp gate judges any path under `plan_done/`, so `--scaffold`'s own `.gitkeep` blocks every `Stop` in a repository that already had commits

Status: open

Evidence: the gate tests the porcelain status and the path prefix only
(`bin/moltke.py:1264-1278`); nothing requires the entry to be a step file, and
S060's `-uall` (`bin/moltke.py:1244`) is what makes individual files inside a
wholly untracked `plan_done/` visible to it. `--scaffold` writes
`adocs/plan_done/.gitkeep` (`bin/moltke.py:1396-1401`). An existing project
adopting moltke, which is the documented use of `--scaffold`:

```
$ git init && echo '# existing project' > README.md && git add -A && git commit -m 'existing history'
$ moltke.py --scaffold
moltke: scaffolded /private/tmp/moltke_audit_...
  created  .moltke.json
  ...
  created  adocs/plan_done/
$ moltke.py --stop
exit=2
moltke: source changed but adocs/worklog.md has no recap heading after the last logged prompt; ...
moltke: adocs/plan_done/.gitkeep was completed without the README and MANUAL check recorded; check both files and note it in the done: stamp (checking with no change needed is valid).
$ moltke.py --validate
moltke: all checks pass
```

Staging does not clear it — `_arrives_here` (`bin/moltke.py:1209-1215`) counts
`A ` as an arrival too — so `git add -A` leaves the same two lines; only a commit
does. Any stray file has the same effect in a working repository:

```
$ echo 'scratch notes' > adocs/plan_done/notes.txt
$ git status --porcelain -uall
?? adocs/plan_done/notes.txt
$ moltke.py --stop
exit=2
moltke: adocs/plan_done/notes.txt was completed without the README and MANUAL check recorded; ...
```

`plan_steps` filters on `STEP_FILE_RE` (`bin/moltke.py:202`), so INV-5 and INV-6
say nothing about either file: the stamp gate is the only reader of `plan_done/`
without that filter. `MANUAL.md:216` says "It sees **the step** arrive in
`plan_done/`", and `adocs/specs.md:554-555` says "a step file newly moved into
`plan_done/` must mention README and MANUAL in its `done:` stamp".

Impact: the first `Stop` of the first session after adopting moltke blocks with a
message about a file moltke wrote itself, telling the user to add a `done:` stamp
to a zero-byte placeholder. It is unactionable as written — the remedy is `git
commit`, which the message does not name — and it persists for every turn until
the commit lands, which is precisely the window in which a new user is deciding
whether the tool is worth keeping. The fresh-repository path is unaffected, because
the gate abstains before the first commit, so the suite's
`test_fresh_scaffold_is_immediately_clean` passes while the adoption path is broken.

Suggested resolution: require `STEP_FILE_RE.match(Path(entry).name)` in the gate
alongside the existing `is_file()` check, so the gate judges steps and the tree is
still reported by INV-7. Red-first case: `--scaffold` into a repository with one
commit, asserting `--stop` names no `.gitkeep`; plus a stray `notes.txt` under
`plan_done/`. Not applied here.

### 2026-08-08_adversarial.2-F04  medium  `--step done` still has one mutation after the point of no return, and the state it leaves has no way out through the CLI

Status: open

Evidence: S062 moved the write to `plan_done/` first and the unlink second, and
left the parent unpause third (`bin/moltke.py:1677-1680`), after both. The unpause
is a write to a different file and can fail on its own. Fixture: `S001` paused by
its blocking child `S002`, everything else valid, the parent's step file read-only:

```
$ chmod 444 adocs/plan_current/S001_parent.md
$ moltke.py --step done S002 --stamp "README MANUAL checked, suite green"
exit=1
moltke: --step done could not touch the plan tree ([Errno 13] Permission denied:
  '.../adocs/plan_current/S001_parent.md'). The workflow directories under adocs/ are
  what --step moves files between; restore the missing one, or run bin/moltke.py
  --scaffold, which creates what is absent and overwrites nothing

  plan_current: ['S001_parent.md']
  plan_done   : ['S002_child.md']
$ moltke.py --validate
moltke: all checks pass
```

The step completed; the refusal says the plan tree could not be touched and points
at `--scaffold`, and nothing is missing. The parent is now paused by a step in
`plan_done/`, and neither operation can clear it:

```
$ moltke.py --step done S001 --stamp "README MANUAL checked"
moltke: S001 is paused by S002; complete S002 first, which unpauses this step automatically
$ moltke.py --step done S002 --stamp "README MANUAL checked"
moltke: S002 is in plan_done, not plan_current/; only a step that is actually in progress can be completed
$ moltke.py --step start S001
moltke: S001 is already in plan_current/
$ moltke.py --step status   # status.md now records it as the steady state
- Last done: S002
- In progress: none
- Next: S001
- Blocked: S001 parent (paused by S002  # 2026-08-08)
```

The pre-S062 order, measured on the identical fixture with the old code restored in
a copy outside the repository, failed the other way: `plan_current:
['S001_parent.md', 'S002_child.md']`, `plan_done: []`, recoverable by `chmod` and a
rerun. So this state is new with S062.

Impact: a completion that half-applied and cannot be finished or undone with the
tool, only by hand-editing a step file — which is what `--step` exists to avoid,
and what `AGENTS.md` §4 forbids by convention. `adocs/specs.md:537` states "Each
refuses rather than repairs, naming the missing condition"; this one repairs half
and names a condition that is not the one that failed. No invariant catches it:
nothing checks that `paused_by` names a step that is still open, so `--validate` is
green and `--session-start` announces the paused parent every session. Narrow —
it needs a write failure on the parent — but the same three-writes-one-transition
shape has now produced a finding in two consecutive runs.

Suggested resolution: either do the unpause before the destination write (it is
idempotent and harmless if the move then fails, unlike the reverse), or make it a
non-fatal warning naming the parent and the field to clear, so a completion that
has already moved the file never reports as a refusal. An invariant that a
`paused_by` id must be a step outside `plan_done/` would make the residue visible
whatever the cause. Red-first case: the read-only-parent fixture, asserting
`--step done` reports success or a refusal that leaves `--step done`/`--step start`
able to proceed. Not applied here.

### 2026-08-08_adversarial.2-F05  medium  INV-7's remedy for a rename inside `plan_done/` is `git checkout -- old -> new`, which as a shell command truncates the renamed file

Status: open

Evidence: INV-7's HEAD half parses porcelain by slicing
(`bin/moltke.py:369-373`), `status, _, entry = line[:2], line[2], line[3:]`, and
never splits on ` -> `. `porcelain_paths` (`bin/moltke.py:1194-1206`) was added by
S050 for exactly this — "A staged rename is one line, `R  old -> new`, and both
halves matter" — and is used by both `Stop` gates and `worktree_state`, not here.

```
$ git mv adocs/plan_done/S001_base.md adocs/plan_done/S001_renamed.md
$ git status --porcelain -- adocs/plan_done
R  adocs/plan_done/S001_base.md -> adocs/plan_done/S001_renamed.md
$ moltke.py --validate
VIOLATION: INV-7: adocs/plan_done/S001_base.md -> adocs/plan_done/S001_renamed.md changed under plan_done/; history is immutable: restore it with git checkout -- adocs/plan_done/S001_base.md -> adocs/plan_done/S001_renamed.md
VIOLATION: INV-7: adocs/plan_done/S001_base.md landed in plan_done/ at commit 047056e3 and is gone; completed history is never removed. Restore it in a new commit: git show 047056e3:adocs/plan_done/S001_base.md > adocs/plan_done/S001_base.md
2 violation(s).
```

The instruction as printed, pasted into any POSIX shell, runs `git checkout --
adocs/plan_done/S001_base.md` with stdout redirected into
`adocs/plan_done/S001_renamed.md`, truncating it to zero bytes. Deleting `R` from
the status codes INV-7 tests leaves the full suite green, so nothing covers this
line at all:

```
$ (in a copy outside the repository) if any(code in status for code in ("M", "D", "C", "U")):
$ python3 -m unittest discover -s tests
Ran 308 tests in 131.302s
OK
```

Impact: the one invariant whose subject is immutable history prints a remedy that
destroys a file in it, and the file it destroys is the renamed copy — the only
remaining content of the step. The same text reaches `--stop` as a blocking
problem, so INV-12's "a message stating exactly what to do to unblock" is not just
unmet but actively harmful. Reachable by an agent or a human tidying a filename in
`plan_done/`, which the rules forbid but the filesystem allows, and by any `R`
status the scoped pathspec produces. Low likelihood, high cost, and the fix is one
call to a function that already exists.

Suggested resolution: read the entry through `porcelain_paths(line)[-1]` in INV-7
as everywhere else, and for a rename name both paths with `git mv` as the remedy
rather than `git checkout --`. Red-first case: `git mv` inside `plan_done/`,
asserting the message contains no ` -> ` and no shell metacharacter. Not applied
here.

### 2026-08-08_adversarial.2-F06  medium  S063's structural guard against the recurring defect cannot fire, because S064 removed the thing it looks for

Status: open

Evidence: `adocs/specs.md:75-77` states "Every whole-file read goes through
`read_stripped`, which is what keeps the list and the scanners from disagreeing
again; a call site pairing `strip_guidance` with `read_text` is a test failure now,
not an audit finding in two months." The test is
`tests/test_s033_fences.py:395-404`:

```
        source = (REPO / "bin" / "moltke.py").read_text(encoding="utf-8")
        offenders = [line.strip() for line in source.splitlines()
                     if "strip_guidance(" in line and "read_text(" in line]
        self.assertEqual(offenders, [], ...)
```

It matches one line containing both names. S064 then made `read_file` the only
reader and `tests/test_s033_fences.py:463-469` forbids any `.read_text(` without
`errors=`, so the mandated way to write a new scanner is
`strip_guidance(read_file(path))` — which contains no `read_text(` and passes. The
guard is now vacuous by construction. Demonstrated by adding a new consumer of a
file that is not in `stripped_files`, in exactly that style, to a copy of the
repository outside it:

```
def testing_rows(root):
    path = root / DOCS / "testing.md"
    if not path.is_file():
        return []
    return [l for l in strip_guidance(read_file(path)).splitlines() if l.startswith("|")]

$ python3 -m unittest discover -s tests
Ran 308 tests in 96.955s
OK
$ stripped_files(REPO) -> ['adocs/plan.md', 'adocs/decisions.md', 'adocs/worklog.md', 'adocs/specs.md', ...audit reports]
```

`adocs/testing.md` is now read through `strip_guidance` and is guarded by neither
INV-13 nor INV-16, which is the state S028 left `specs.md` in and F04 reported.

Impact: this is the guard for the defect class that has produced a finding in four
consecutive audits. It reads as enforcement in the specs and in the test's own
docstring — "A future scanner that pairs `strip_guidance` with `read_text` again
fails here rather than in an audit two months later" — and it enforces nothing. The
cost is not today's behaviour, which is correct: it is that the next consumer will
be added with the suite green and the specs claiming the opposite.

Suggested resolution: make the check structural rather than textual — assert that
every `strip_guidance(` call site in `bin/moltke.py` outside `read_stripped` and
`field_value` is absent, which is a property of the current source and survives any
reader name; or derive `STRIPPED_FILES` from the call sites by inspection at test
time. Either way state what it can still not see. Red-first case: the mutant above,
asserting the suite goes red. Not applied here.

### 2026-08-08_adversarial.2-F07  low  reverting S060's `-uall` in `--stop` leaves all 308 tests green, though it changes what the stamp gate can see

Status: open

Evidence: mutation. `bin/moltke.py:1244` back to `_git_lines(root, "status",
"--porcelain")` in a copy of the repository outside it:

```
$ python3 -m unittest discover -s tests
Ran 308 tests in 133.917s
OK
```

The behaviour it names is real. A completed step arriving in a `plan_done/` that
is itself wholly untracked, with a stamp that does not name README and MANUAL:

```
  plain  : ?? adocs/plan_done/
  -uall  : ?? adocs/plan_done/S001_base.md
current bin/moltke.py:  --stop exit=2
  moltke: adocs/plan_done/S001_base.md was completed without the README and MANUAL check recorded; ...
M2 mutant (plain porcelain): --stop exit=0
```

Impact: one of the four behaviours S060's specs note names is unguarded, so a
later change that reverts to plain porcelain for cost or consistency reasons —
`worktree_state` and this gate are the only `-uall` readers — would restore the
blind spot silently. The other three mutations bite: removing the `is_file()` skip
fails `test_the_problems_found_before_the_missing_file_are_still_printed`, removing
`run_checks`' handler fails `test_an_unreadable_tree_reports_instead_of_raising`,
and removing the `main` backstop fails three.

Suggested resolution: a case that puts a badly stamped step into an untracked
`plan_done/` and asserts `--stop` names it, with the precondition asserted first —
`assertIn("?? adocs/plan_done/", plain_porcelain)` — so it cannot pass vacuously.
Not applied here.

### 2026-08-08_adversarial.2-F08  low  `python3 tests/test_s033_fences.py` runs `unittest.main()` before the S063 and S064 classes are defined, so nine tests never run

Status: open

Evidence: `tests/test_s033_fences.py:334` holds `unittest.main()` under `if
__name__ == "__main__":`, and `TestEveryStrippedFileIsGuarded` (line 337) and
`TestOneDecodePolicy` (line 414) are defined after it.

```
$ python3 -m unittest discover -s tests -p 'test_s033*' -v | grep -c 'ok$'
35
$ python3 tests/test_s033_fences.py -v | grep -c 'ok$'
26
```

The nine missing are exactly S063's five and S064's four, including
`test_a_fence_hiding_the_prime_directive_does_not_pass_silently`,
`test_one_bad_byte_in_a_step_file_does_not_break_any_mode`, and both structural
source checks.

Impact: the full suite is unaffected — discovery imports the module, so
`__name__` is not `"__main__"` and every class is collected. It bites the
red-first workflow `AGENTS.md` §6 and `README.md:107-109` prescribe: watching one
file fail before the fix is the normal way to observe red, and for these two steps
the file reports `OK` while running none of their tests. Anyone adding a class at
the end of this file inherits the same silence.

Suggested resolution: move the `if __name__ == "__main__":` block to the end of the
file, and add a check that no test module defines a class after its `unittest.main()`
call. Not applied here.

### 2026-08-08_adversarial.2-F09  low  INV-14 blames a code fence for a finding heading an HTML comment hides, and the remedy it prints cannot be followed

Status: open

Evidence: `hidden_findings` (`bin/moltke.py:528-544`) compares the raw text against
the stripped text, and `strip_guidance` removes HTML comments as well as fences, so
a heading inside a comment is "hidden" too. A report with zero fence markers:

```
$ cat adocs/audit/2026-08-01_adversarial.md
# Audit

### 2026-08-01_adversarial-F01  high  a real finding

Status: accepted

<!-- draft, not ready to file yet:
### 2026-08-01_adversarial-F02  low  a draft finding

Status: open
-->
$ grep -c '^```' adocs/audit/2026-08-01_adversarial.md
0
$ moltke.py --validate
VIOLATION: INV-14: 2026-08-01_adversarial.md states finding 2026-08-01_adversarial-F02 but a code fence swallows it, so INV-10 and --audit list never see it. Two unclosed fences pair as one closed fence and the marker count stays even, which is why INV-13 is quiet: close the evidence blocks around that heading
$ moltke.py --audit list
  2026-08-01_adversarial-F02  hidden  (a code fence swallows it; INV-14)
```

Impact: the message names a cause that is not present and a remedy — close the
evidence blocks — that cannot be applied, and the same text reaches `--stop` and
`--post-write` as a blocking problem. It is also a policy question the code answers
by accident: `adocs/specs.md:728` makes commented content guidance everywhere else,
and the shipped report template's own `<!-- Append findings here -->` is a comment,
so commenting out a draft finding is a reasonable thing for a reviewer to do and
turns `--validate` red with a misleading explanation.

Suggested resolution: distinguish the two in `hidden_findings` — compare against
`strip_comments` as well as `strip_guidance` — and print "a code fence" or "an HTML
comment" accordingly, with the matching remedy. Decide explicitly whether a
commented heading is a violation at all and say so in the specs. Red-first case:
the fixture above, asserting the message names the comment. Not applied here.

### 2026-08-08_adversarial.2-F10  low  `--audit` exits 2 through the backstop, which README's exit table assigns to the three hook modes only, and a write failure is reported as "could not read the repository"

Status: open

Evidence: `README.md:71-76` maps exit `2` to "a blocked action, with what to do
about it", produced by `mode_pre_write`, `mode_stop`, `mode_post_write`, and exit
`1` refusals to "`refuse`, which is the return path for every `--step` and `--audit
new` refusal". The backstop (`bin/moltke.py:2178-2186`) returns `EXIT_BLOCK` for
every mode except `--log-prompt` and `--session-start`:

```
$ chmod 555 adocs/audit && moltke.py --audit new adversarial
exit=2
moltke: could not read the repository ([Errno 13] Permission denied: '.../adocs/audit/2026-08-08_adversarial.md'). Fix the path named above, then run bin/moltke.py --validate.

$ chmod 000 adocs/audit/2026-08-01_adversarial.md && moltke.py --audit list
exit=2
moltke: could not read the repository ([Errno 13] Permission denied: ...)
$ moltke.py --validate          # same repository, same file
exit=1
VIOLATION: INV-10 could not read the repository (...)
VIOLATION: INV-13 could not read the repository (...)
VIOLATION: INV-14 could not read the repository (...)
```

`--step` is unaffected: `mode_step` has its own handler at
`bin/moltke.py:2102-2109` and refuses with exit 1.

Impact: small and mechanical. A consumer following the documented mapping reads
the wrong stream and the wrong meaning for `--audit`; the first failure above is a
write, reported as a read, with a remedy — run `--validate` — that has nothing to
do with it. It also means the exit table is no longer traced to the code that
produces it, which `AGENTS.md` §7 requires of every doc claim.

Suggested resolution: give `mode_audit` the handler `mode_step` has, refusing with
exit 1 and a message that distinguishes a read from a write; or widen the README
table and say the backstop is the fourth producer of exit 2. Not applied here.

### 2026-08-08_adversarial.2-F11  low  `--audit check` keeps the pre-S050 narrow definition of "newly here", so a staged-then-edited new test is reported as unexpected

Status: open

Evidence: `_is_new_file` (`bin/moltke.py:1823-1824`) is `status in ("??", "A ")`,
the predicate S050 replaced in the `Stop` gates with `_arrives_here`
(`bin/moltke.py:1209-1215`), whose index half accepts `AM` and `RM` as well.

```
$ moltke.py --audit new adversarial
$ echo '# red first' > tests/test_regression.py && git add tests/test_regression.py
$ echo '# red first, refined' > tests/test_regression.py
$ git status --porcelain -uall
AM tests/test_regression.py
?? adocs/audit/2026-08-08_adversarial.md
$ moltke.py --audit check
expected, this run's report and new tests:
  adocs/audit/2026-08-08_adversarial.md: ??
unexpected, not attributable to writing the report:
  tests/test_regression.py: AM
The reviewer holds Bash and is not fenced from mutating the repository (DEC-022). Review each change above before acting on any finding: ...
exit=1

control, the same file never staged:
expected, this run's report and new tests:
  adocs/audit/2026-08-08_adversarial.md: ??
  tests/test_regression.py: ??
exit=0
```

Impact: `adocs/specs.md:566-580` and DEC-022 say new files under `tests/` are
expected, because a red-first regression test is the evidence a reviewer is
supposed to produce. Staging one during the run makes the gate report it as
contamination and exit 1. Minor on its own; it matters because S036's own reasoning
— a gate that is wrong on a normal path is one people learn to wave through — is
what `--audit check` exists to avoid, and because it is the same predicate twin
S050 was about, still unpaired one release later.

Suggested resolution: use `_arrives_here` in `classify`, so both readers of "this
path is newly here" have one definition. Red-first case: the sequence above,
asserting `expected`. Not applied here.

### 2026-08-08_adversarial.2-F12  low  INV-16 tests both sides for emptiness rather than comparing them, so a directive fenced beside other prose is invisible and unreported

Status: open

Evidence: `inv_16_prime_directive_readable` (`bin/moltke.py:683-687`) returns
clean as soon as `prime_directive(root)` is non-empty; it never compares the raw
section with the stripped one. `adocs/specs.md:81-82` describes it as "this
compares what the file states against what survives stripping, exactly as INV-14
does for a finding heading", and INV-14 does compare — heading by heading
(`bin/moltke.py:538-544`). The fixture, written with four-space indentation here so
this report does not nest a fence inside one:

    ## Prime directive

    This project has one rule.

    ```
    State is derivable from tracked files alone.
    ```

    ## Invariants

```
$ moltke.py --validate
moltke: all checks pass   exit=0
$ python3 -c 'print(moltke.prime_directive(root))'
This project has one rule.
$ moltke.py --session-start | grep -c 'Planning phase pending'
0
```

The directive proper is on disk, no check reports it, and `prime_directive` returns
the lead-in sentence instead of the rule.

Impact: nil today, because the only consumer is the planning nudge and it stays
quiet either way. It matters as a claim: `specs.md` says the comparison is
content-level and the code is a two-sided emptiness test, so a future reader of
`prime_directive` — the reason INV-16 exists — gets whatever prose sits outside the
fence. This is the same gap between a documented comparison and an implemented
predicate that F06 records for the structural guard.

Suggested resolution: either compare the stripped section against the raw section
with fences removed but their content kept, and report when the stripped one is
materially shorter; or narrow the specs sentence to what the code does, which is
"reports a directive section that is written and reads as empty". Not applied here.

## What was checked and found sound

Recorded so a later run knows this ground was covered, and so the findings above
are not read as a verdict on the whole of S060..S065.

- **Twelve of thirteen mutations went red.** Each behaviour was deleted in a copy
  of the repository outside it and the full suite re-run: the stamp gate's
  `is_file()` skip (1 failure), `run_checks`' `OSError` handler (1), `main`'s
  backstop (3), `stop_turn_key`'s breadcrumb fold (1), `step_done`'s write-first
  ordering (3), INV-16 (2), `specs.md` in `STRIPPED_FILES` (2), `read_file`'s
  `errors="replace"` (16), `planning_pending`'s deference to INV-16 (2), the stamp
  gate's abstain before the first commit (2). The survivors are `-uall` in
  `mode_stop` (F07) and INV-7's `R` status (F05), and one more guard is inert
  without needing a mutation (F06).
- The S061 fix is measured in both directions: eight real turns with an unwritable
  worklog read `2 2 2 2 2 2 2 2`, eight retries inside one turn read
  `2 2 2 0 0 0 0 0`, and the state file's `turn` key carries the breadcrumb's
  `since` and `count`.
- The S064 decode policy holds for every file I could reach: `plan.md`,
  `decisions.md`, `worklog.md`, `testing.md`, `status.md`, a `plan_done/` step
  file, an audit report, and `.moltke.json`, across six modes.
- `--step done`'s two earlier failure points behave as S062 claims: a missing
  `plan_done/` refuses with nothing written, and the copy is undone if the source
  cannot be unlinked.
- INV-16 and the planning nudge do not double-report: the fence case is INV-16
  alone, the empty case is the nudge alone, and a normal `specs.md` full of
  balanced example fences is silent.
- The stamp gate's `is_file()` skip does what F01 asked for: `RD` and `AD` are
  skipped by it and the tree is still reported by INV-7, in the same call.
- `README.md`'s "308 tests, no skips" is accurate at this commit, and the "No
  environment variables" claim still holds: `bin/moltke.py` imports neither `os`
  nor anything that reads the environment.
- INV-14's stem scoping behaves as documented on this report: the verdict section
  above quotes six foreign finding ids and none is treated as a finding of this
  file.
