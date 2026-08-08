# Audit 2026-08-08 adversarial

Scope: `bin/moltke.py` at commit `f348c44`, version 0.5.0, plus `hooks/hooks.json`,
`agents/adversarial_reviewer.md`, `skills/`, `templates/`, `tests/`, and the claims
`README.md`, `MANUAL.md`, `adocs/specs.md`, and `AGENTS.md` make about them.

Method: two jobs. First, a verdict on each of the ten findings in
`adocs/audit/2026-08-07_adversarial.2.md` and on `2026-08-07_adversarial-F02`,
each decided by re-running that finding's own reproduction against the code at
`f348c44` in throwaway repositories under `/private/tmp`, never against the step
files, the stamps, or the commit messages. Second, a fresh pass over the ten steps
of new checker surface that landed since (S028, S029, S031, S049..S052, S055..S057),
including mutation testing: sixteen behaviours those steps introduced were each
deleted in a copy of the repository outside it and the full suite re-run, to see
whether the tests that name them bite.

Baseline at the start of the run:

```
$ python3 -m unittest discover -s tests
Ran 286 tests in 68.913s
OK
$ python3 bin/moltke.py --validate
moltke: all checks pass
$ git status --porcelain -uall
?? adocs/audit/2026-08-08_adversarial.md
```

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-08_adversarial-F<nn>`. The example below writes that prefix as
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

Summary: 6 new findings. 1 high, 3 medium, 2 low. Of the eleven prior findings
carried into this run, nine no longer reproduce, one (`.2-F06`) still reproduces
and is `accepted` under DEC-031, and one (`.2-F07`) has its code half unchanged
by design with its documentation half only partly corrected — that residual is
F06 below. `2026-08-07_adversarial-F02`, held `planned` for three runs, no longer
reproduces.

The batch is the strongest so far on tests: all sixteen mutations went red, with
no survivor, against one survivor in each of the last two runs. The pattern in
what is left is the same one three audits have now named — a rule tightened in
one place and its twin not. S050 widened which porcelain statuses mean "a step
arrived in `plan_done/`" without widening what the code does when the file named
by such a status is not on disk (F01). S047 moved the `Stop` waiver's clock into
the worklog without asking whether the worklog is still being written (F02). S052
turned a crash in `--step` into a refusal without moving the refusal ahead of the
writes (F03). S028 made `adocs/specs.md` a `strip_guidance` input without adding
it to INV-13's list (F04). S049 gave INV-14 two halves that read the same file
with two different decode policies (F05).

## Verdicts on the 2026-08-07 re-run findings

One line each, decided by running the tool at `f348c44`. Ids are written inline
rather than as headings, because a `###` heading carrying another report's stem
is an INV-10 violation in this file.

- **`.2-F01`** (the Stop waiver keys on a `prompt_id` nothing establishes, and
  without one turns every Stop check off) — **no longer reproduces as measured,
  with a residual recorded as F02 below.** The literal command sequence from the
  finding, eight `--stop` calls with `{}` and no prompt between them, still reads
  `2 2 2 0 0 0 0 0` — but under `stop_turn_key` (`bin/moltke.py:1001-1024`) that
  sequence is now eight *retries inside one turn*, which is the no-deadlock
  property working. Eight real turns, each `--log-prompt` then `--stop`, read
  `2 2 2 2 2 2 2 2` with `{}`, with `{"session_id":"s1"}`, and with the worklog
  deleted before the run (`--log-prompt` recreates it). The waived turn now prints
  the problems first, and the count resets on a changed problem set.
- **`.2-F02`** (a step listed in `plan.md` only in prose is invisible to the
  derived next step while `--validate` says all checks pass) — **no longer
  reproduces**. The fixture from the finding, `S002_pending.md` in `plan_todo/`
  with `plan.md` naming `S002` only in its description paragraph, now gives
  `VIOLATION: INV-3: adocs/plan_todo/S002_pending.md is not listed in plan.md; add
  S002 to the ordered list, since a mention in the description is not the plan and
  never becomes the next step`, exit 1, and `--stop` exit 2. In the reverse
  direction an id named only in prose is no longer a phantom at all: `S099` in a
  sentence above a normal list gives `moltke: all checks pass` and
  `Derived next step: S002`, with the false "S099 is the derived next step"
  sentence gone.
- **`.2-F03`** (`git add -A` turns off both Stop gates for a moved file, and the
  stamp gate has no test) — **no longer reproduces**. All three move shapes now
  report, exit 2: plain `mv` (` D` + `??`), `git mv` (`R  old -> new`), and `mv`
  then `git add -A` (`R  old -> new`) each give `stamp complaints: 1`. A
  `git mv adocs/notes/thing.py src_thing.py` gives `recap demands: 1`. The gate
  has four tests now, and deleting `_arrives_here`'s widening or `porcelain_paths`'
  split takes two and three of them red respectively.
- **`.2-F04`** (MANUAL says the two-unclosed-fence hole is pre-0.4.0; it
  reproduces) — **no longer reproduces**. The J2 fixture, both closing markers
  removed, now gives `VIOLATION: INV-14: 2026-08-01_adversarial.md states finding
  2026-08-01_adversarial-F02 but a code fence swallows it`, exit 1; `--audit list`
  prints `2026-08-01_adversarial-F02  hidden  (a code fence swallows it; INV-14)`,
  exit 1; and `--post-write` reports it on save, exit 2. The control with both
  fences closed gives the INV-10 unreferenced violation as before.
- **`.2-F05`** (S039 steers into `--step status`, which dies with a traceback with
  no `adocs/`) — **no longer reproduces**. In a marked repository holding only
  `.git`, `.moltke.json`, and `README.md`, all four of `--step status`, `new`,
  `start`, and `done` refuse with `adocs/ does not exist, so there is no plan to
  move. Run bin/moltke.py --scaffold to create it`, exit 1 on stderr, no traceback;
  `--session-start` and `--stop` both name `--scaffold` first. A partially
  scaffolded tree (`adocs/` present, `plan_current/` gone) gives the OSError
  refusal rather than a stack trace. See F03 below for what that refusal leaves
  behind.
- **`.2-F06`** (no Stop deadlock cap in a marked repository without git) —
  **still reproduces, status `accepted`.** Six `--stop` calls in a scaffolded,
  never-`git init`ed repository read `2 2 2 2 2 2`. Accepted under DEC-031 and
  disclosed in `MANUAL.md`; no action expected.
- **`.2-F07`** (INV-8 as enforced is a line subsequence, so a mid-file insertion
  commits green) — **code half unchanged by design; specs half corrected;
  MANUAL half only partly.** Inserting a forged `DEC-003` between `DEC-001` and
  `DEC-002` and committing still gives `moltke: all checks pass`, exit 0, which
  is now what `adocs/specs.md:35` and `MANUAL.md:320-327` say happens (S054,
  DEC-030). What was not corrected is the other sentence the finding named: see
  F06 below.
- **`.2-F08`** (INV-13 counts markers `strip_guidance` never sees) — **no longer
  reproduces**. The fixture with a fence marker inside an HTML comment, three
  markers by raw `grep` and two after comment removal, now gives
  `moltke: all checks pass` exit 0 and `--stop` exit 0. A genuinely unclosed fence
  outside a comment is still reported.
- **`.2-F09`** (the worklog exemption is shape-based, so a `Bash` append silences
  the recap gate and `--audit check` calls it expected) — **no longer reproduces**.
  A fabricated `## 2026-08-07 recap S001` appended during a run now gives, under
  `unexpected`: `adocs/worklog.md: appended 2 line(s), 2 of which --log-prompt
  would not have written, first '## 2026-08-07 recap S001'. A recap heading here
  discharges the Stop recap gate for this turn`, exit 1. The control, a genuine
  `--log-prompt` of a multi-line prompt that itself contains a recap heading and a
  fence, stays `expected`: `adocs/worklog.md: appended 4 line(s), all prompt log
  entries`, exit 0. What is unchanged, and correctly so, is that `--stop` still
  accepts the fabricated recap in the moment: `recap demands: 0`.
- **`.2-F10`** (the reviewer fence stops at the repository boundary while the agent
  definition states it unqualified) — **code unchanged by design; documentation
  half fixed.** `--pre-write` on `~/.claude/plugins/cache/moltke/moltke/0.2.0/bin/
  moltke.py` and on `~/.claude/settings.json` is still exit 0.
  `agents/adversarial_reviewer.md:20-25` and `skills/audit/SKILL.md:31-35` now both
  say the fence covers this repository only and that `--audit check` cannot see
  outside it.
- **`2026-08-07_adversarial-F02`** (an unbalanced code fence hides an open finding),
  held `planned` since 2026-08-07 — **no longer reproduces**. Its primary evidence
  path is the J2 case above, which INV-14 now reports. Its C4 case, the recap gate,
  was already fixed by S033 and remains so.

I did not re-verify the `2026-08-06_adversarial-F02` installed-plugin verdict: it
turns on what version is in `~/.claude/plugins/cache`, which is outside the
repository and outside this run's scope.

## Findings

### 2026-08-08_adversarial-F01  high  `--stop` exits 1 with a traceback and enforces nothing when a step file staged into `plan_done/` is not on disk, and the stamp gate's own remedy is what puts you there

Status: open

Evidence: the stamp gate (`bin/moltke.py:1135-1143`) decides on the porcelain
status alone and then reads the file:

```
        for line in porcelain:
            entry = porcelain_paths(line)[-1]
            if _arrives_here(line[:2]) and entry.startswith(f"{DOCS}/plan_done/"):
                fields = parse_step_file(root / entry)
```

`_arrives_here` (`bin/moltke.py:1086-1092`) returns True for any status whose
index half is `A`, `R`, or `C`, and `parse_step_file` (`bin/moltke.py:85-91`)
opens the path with no existence check and no `try`. `mode_stop` has no exception
handler, so the whole Stop hook dies. Three porcelain shapes reach it, each
measured with the same fixture and a control:

```
shape RD: RD adocs/plan_current/S003_active.md -> adocs/plan_done/S003_active.md
  --stop exit=1  FileNotFoundError: [Errno 2] No such file or directory: '.../adocs/plan_done/S003_active.md'
shape AD:  D adocs/plan_current/S003_active.md
           AD adocs/plan_done/S003_active.md
  --stop exit=1  FileNotFoundError: [Errno 2] No such file or directory: '.../adocs/plan_done/S003_active.md'
shape ??dir: ?? adocs/plan_done/
  --stop exit=1  IsADirectoryError: [Errno 21] Is a directory: '.../adocs/plan_done'
control R : RM adocs/plan_current/S003_active.md -> adocs/plan_done/S003_active.md
  --stop exit=2  moltke: adocs/plan_done/S003_active.md was completed without the README and MANUAL check record
```

`RD` and `AD` are new since S050: before it, `_arrives_here`'s predicate was
`status in ("??", "A ")`, which neither matches. The third shape is older —
`mode_stop` reads `git status --porcelain` without `-uall` (`bin/moltke.py:1119`)
while `worktree_state` passes it (`bin/moltke.py:1599`) with a comment explaining
exactly why — so a wholly untracked `adocs/plan_done/` collapses to one directory
entry that `startswith("adocs/plan_done/")` accepts.

The `RD` shape is reachable by following the gate's own instruction. A step
completed by hand and staged, with a stamp that does not name README and MANUAL:

```
1) complete the step by hand and stage it, stamp missing README/MANUAL
     R  adocs/plan_current/S003_active.md -> adocs/plan_done/S003_active.md
     --stop exit= 2
     'moltke: adocs/plan_done/S003_active.md was completed without the README and MANUAL check recorded; check both files and note it in the done: stamp (checking with no change needed is valid).'

2) the remedy: the file is under plan_done/, so Write/Edit is blocked there
     --pre-write exit= 2 | moltke: adocs/plan_done/S003_active.md is under plan_done/, which is immutable history.

3) so move it back with Bash `mv`, which the block leaves as the only way
     RD adocs/plan_current/S003_active.md -> adocs/plan_done/S003_active.md
     ?? adocs/plan_current/
     --stop exit= 1
     stderr tail: FileNotFoundError: [Errno 2] No such file or directory: '.../adocs/plan_done/S003_active.md'
     stdout: ''
```

The crash happens before `mode_stop` prints anything, so every problem collected
earlier in the same call is lost. In a fixture that also holds a real INV-3
violation and a stale `status.md`, the same repository one `mv` apart:

```
with the destination present: exit= 2 | moltke: lines = 6
    moltke: INV-3: plan.md lists S099 but no step file exists in plan_todo/, plan_current/, or plan_done/; ...
    moltke: INV-5: no testing.md row references S003; add the acceptance rows before completing the step
    moltke: INV-7: adocs/plan_done/S003_active.md changed under plan_done/; history is immutable: ...
    moltke: status.md is stale or missing: Last done says 'S001', the filesystem says 'S003'. ...
    moltke: status.md is stale or missing: In progress says 'S003 active', the filesystem says 'none'. ...
    moltke: adocs/plan_done/S003_active.md was completed without the README and MANUAL check recorded; ...
after moving it back:        exit= 1 | moltke: lines = 0
   stdout: ''
```

Impact: exit 1 from a `Stop` hook is a non-blocking error, so the turn ends. Every
`--stop` gate — all thirteen invariants, the four staleness fields, the recap gate,
the stamp gate — is off for that turn and stays off for as long as the index and
the worktree disagree about that path, which is until someone stages or reverts it.
Nothing tells the user what was wrong; a Python traceback is neither of the two
things `README.md:71-76` says exit 1 can be, and `adocs/specs.md:453` describes
`--stop` as exiting 2 with an actionable message. `.2-F05` recorded the same shape
for `--step` and S052 fixed it there; `mode_stop` and `mode_post_write` still have
no handler at all. The path in step 3 above is worse than incidental: the gate
blocks, its remedy requires editing a file the `--pre-write` fence forbids editing,
and the only compliant way out crashes the gate.

Suggested resolution: in the stamp gate, skip an entry that is not an existing
file — `path = root / entry; if not path.is_file(): continue` — before
`parse_step_file`, and give `mode_stop` and `mode_post_write` the `OSError`
handling `mode_step` gained in S052, turning an unreadable tree into a refusal
that names the path. Pass `-uall` in `mode_stop` too, so both gates and
`worktree_state` read one porcelain shape, or handle the collapsed directory
entry explicitly. Red-first cases: `AD`, `RD`, and `?? adocs/plan_done/`, each
asserting exit 2 or 0 and never 1. Not applied here.

### 2026-08-08_adversarial-F02  medium  the Stop deadlock waiver's clock is the worklog, so a prompt-append failure — the one moltke already detects — restores the `.2-F01` off switch

Status: open

Evidence: `stop_turn_key` (`bin/moltke.py:1014-1024`) builds the key from
`prompt_id`, `session_id`, and the count of prompt headings in
`adocs/worklog.md`:

```
    parts = [str(payload.get("prompt_id") or ""), str(payload.get("session_id") or "")]
    worklog = root / DOCS / "worklog.md"
    prompts = 0
    if worklog.is_file():
        ...
    parts.append(str(prompts))
```

S047 chose the heading count because `UserPromptSubmit` advances it exactly once
per turn. It does — unless the append fails, which is the case S014 built
`.git/moltke_log_failure.json` for (`bin/moltke.py:848-868`). `mode_log_prompt`
swallows the `OSError` and exits 0 by contract, so nothing downstream knows, and
`stop_turn_key` never consults the breadcrumb. With `prompt_id` absent — which
`.2-F01` established nothing shows the payload carries — the key is then constant
across turns and the counter is once again cumulative:

```
control (worklog writable), 8 turns, payload {'session_id':'s1'}:
   [2, 2, 2, 2, 2, 2, 2, 2]

$ chmod 444 adocs/worklog.md
$ printf '{"prompt":"x"}' | moltke.py --log-prompt
moltke --log-prompt: [Errno 13] Permission denied: '.../adocs/worklog.md'   (exit 0)
breadcrumb written: True

8 turns (--log-prompt then --stop), payload {'session_id':'s1'}:
   [2, 2, 2, 0, 0, 0, 0, 0]
stop state: {"turn": "|s1|1", "fingerprint": "2eeaf685f6a2d32d", "count": 8}

$ moltke.py --validate
VIOLATION: INV-3: plan.md lists S099 but no step file exists in plan_todo/, plan_current/, ...
exit=1
```

Eight distinct turns, the violation present throughout, enforcement off from the
fourth. `bin/moltke.py:871-894` reports the breadcrumb once at the next
`SessionStart` and then deletes it, so after one session the only signal that the
clock has stopped is gone while the condition persists.

Not confirmed: whether a live `Stop` payload carries `prompt_id` or `session_id`.
If it carries a per-turn `prompt_id`, this narrows to nothing; if it carries only
`session_id`, the waiver is an off switch for the rest of that session; if it
carries neither, `hook_input` also returns `{}` on a `JSONDecodeError` and on a
tty (`bin/moltke.py:679-687`), and the state file persists across sessions. I did
not provoke a live hook from inside an audit, and this repository has no
`.git/moltke_stop_state.json` right now, which means the last Stop was clean
rather than that any key is present.

Impact: the deadlock waiver is safe only while "the same turn" is real. When the
worklog stops being written the waiver stops being scoped, and the failure is
silent in both directions — the prompt is lost, and three turns later the Stop
hook stops enforcing anything. `MANUAL.md:388-396` states the per-turn scoping as
a property ("That count is per turn and per problem set: a new turn starts over")
without naming the condition it depends on, and `MANUAL.md:406-414` describes the
prompt-loss failure without saying it also disarms the cap.

Suggested resolution: make the clock independent of a file that can fail to be
written, or make the failure visible to it. The cheapest correct form is to fold
the breadcrumb into the key — `_log_failure_path` already records `count` and
`since`, both of which advance on a failing turn — so the key still moves when
the worklog does not. Alternatively refuse to waive at all while a log-failure
breadcrumb exists, and say so in the waiver line. Add a case asserting eight
turns read `2 2 2 2 2 2 2 2` with the worklog unwritable. Not applied here.

### 2026-08-08_adversarial-F03  medium  `--step done` writes the stamp and unpauses the parent before it refuses, so the S052 refusal path leaves `plan_current/` violating INV-1

Status: open

Evidence: `step_done` runs every gate first, then performs three mutations in
order — stamp, unpause, move (`bin/moltke.py:1509-1514`):

```
    set_field(path, "done", stamp)
    for parent_id, parent_path, parent_fields in steps["plan_current"]:
        if step_id in field_value(parent_fields, "paused_by"):
            set_field(parent_path, "paused_by", "")
            print(f"moltke: {parent_id} unpaused.")
    path.rename(root / DOCS / "plan_done" / path.name)
```

The `rename` is the only one that can fail, and S052 turned that failure into a
refusal at `bin/moltke.py:1936-1943` — but the refusal is raised after the first
two mutations have already been written to disk. In a fixture whose only fault is
a missing `adocs/plan_done/`, with `S001` paused by its blocking child `S002`:

```
$ moltke.py --validate
moltke: all checks pass  exit=0

$ moltke.py --step done S002 --stamp "README MANUAL checked, suite green"
moltke: no "test_command" in .moltke.json, so nothing here ran the suite. ...
moltke: S001 unpaused.
moltke: --step done could not touch the plan tree ([Errno 2] No such file or directory:
  '.../adocs/plan_current/S002_child.md' -> '.../adocs/plan_done/S002_child.md').
  The workflow directories under adocs/ are what --step moves files between; ...
exit=1

  plan_current: ['S001_parent.md', 'S002_child.md']
  S001 paused_by: ['paused_by:']
  S002 done:      ['done:      README MANUAL checked, suite green']

$ moltke.py --validate
VIOLATION: INV-1: plan_current/ holds 2 non-paused steps (S001, S002), limit 1;
pause or complete until 1 remain
exit=1
```

`adocs/specs.md:458` states the contract this breaks: "Each refuses rather than
repairs, naming the missing condition; no transition may leave INV-1..INV-7
violated." The transition refused *and* repaired half of itself, and the
repository went from `all checks pass` to an INV-1 violation.

The same ordering leaves a smaller trace in `step_new` and `step_block`, which
write the step file before `append_to_plan` reads `plan.md`: a failure there
leaves a step file that no list entry names, which is INV-3.

Impact: an agent that follows the refusal — restore the directory, rerun
`--step done` — ends up correct, because the second attempt renames and the parent
was going to be unpaused anyway. An agent that reads the refusal as "nothing
happened", which is what "could not touch the plan tree" says, leaves a repository
where `--validate` is red, `--stop` blocks on INV-1, and a step still in
`plan_current/` carries a `done:` stamp claiming README and MANUAL were checked
and the suite was green. Narrow, because it needs the plan tree to be broken
first, but that is exactly the state S052 exists to serve, and the marked
repository with a partially scaffolded `adocs/` is the first state a new user has.

Suggested resolution: do the move first and the field writes after, or check the
destination directory before any write — a `plan_done/` existence gate alongside
the testing-rows and stamp gates — so the refusal happens before the tree is
touched. Red-first case: `--step done` on a child blocking a paused parent with
`plan_done/` absent, asserting `--validate` still exits 0 afterwards. Not applied
here.

### 2026-08-08_adversarial-F04  medium  INV-13 does not scan `adocs/specs.md`, the `strip_guidance` input S028 added, so a fence there hides the prime directive with every check green

Status: open

Evidence: `inv_13_balanced_fences` scans a fixed list (`bin/moltke.py:539-542`):

```
    scanned = [f"{DOCS}/plan.md", f"{DOCS}/decisions.md", f"{DOCS}/worklog.md"]
    audit_dir = root / DOCS / "audit"
    if audit_dir.is_dir():
        scanned += [str(p.relative_to(root)) for p in sorted(audit_dir.glob("*.md"))]
```

S028 added a fifth `strip_guidance` consumer, `prime_directive`
(`bin/moltke.py:762-771`), which reads `adocs/specs.md` and feeds
`planning_pending` (`bin/moltke.py:774-789`). That file is in neither list, so
neither of the two guards the repository has applies to it. Two unclosed example
fences straddling the heading, control first — marker counts taken with
`grep -cE` on a line-anchored triple-backtick pattern:

```
=== control: both example fences closed ===
  fence markers in adocs/specs.md -> 4
  --validate  -> moltke: all checks pass  exit=0
  --stop      -> exit=0
  --session-start -> no planning nudge

=== the two closing markers removed ===
  fence markers in adocs/specs.md -> 2
  --validate  -> moltke: all checks pass  exit=0
  --stop      -> exit=0
  --session-start -> Planning phase pending: adocs/specs.md has no prime directive yet.
                     The init skill drives it: ... Nothing blocks on this.
  (the directive is written on disk: True)
```

An *odd* count is silent too, which is the part that separates this from INV-14's
territory — there the even count was the whole problem, here parity is never
consulted:

```
markers: 3 (odd)
--validate: moltke: all checks pass exit= 0   <- INV-13 does not scan specs.md
nudge: ['Planning phase pending: adocs/specs.md has no prime directive yet. ...']

control, the same odd count in plan.md:
VIOLATION: INV-13: adocs/plan.md has 1 code-fence markers, an odd number, so one fence
is unclosed. Every scanner reads ...  exit= 1
```

Impact: today the only consumer is the S028 nudge, so the cost is a session-start
line telling the user to write a prime directive they have already written, on
every session, with `--validate` and `--stop` both green and no file named as the
cause. That is the failure S028 was built to remove, reappearing one layer down.
The larger cost is that `adocs/specs.md` is the file `AGENTS.md` §1 puts second in
the reading order and the one that holds the invariants: any future check that
reads it through `strip_guidance` inherits an unguarded file, and the invariant
whose message claims "every scanner reads this file through strip_guidance" is
not scanning the file where the prime directive lives.

Suggested resolution: add `adocs/specs.md` to `scanned`, which is one entry and
makes the odd case loud; and consider deriving the list from the set of files
`strip_guidance` is actually pointed at, so the next consumer cannot be added
without it. The even-count case there stays undetectable for the same reason it
does in `plan.md` and `decisions.md`, which `adocs/specs.md:180-185` already
states — worth an explicit line naming `specs.md` alongside them. Not applied here.

### 2026-08-08_adversarial-F05  low  half of moltke's file readers decode strictly and half replace, so one non-UTF-8 byte turns every mode into a traceback — including INV-14's two halves, which disagree about the same file

Status: open

Evidence: `hidden_findings` reads a report with `errors="replace"`
(`bin/moltke.py:487`) and `report_findings`, the function it compares against,
reads the same file strictly (`bin/moltke.py:499`):

```
487:    raw = report.read_text(encoding="utf-8", errors="replace")
499:    text = strip_guidance(report.read_text(encoding="utf-8"))
```

The same split runs through the file: `inv_13_balanced_fences`,
`inv_15_worklog_secrets`, `recap_pending`, `stop_turn_key`, and `prime_directive`
pass `errors="replace"`; `parse_step_file`, `plan_text`, `inv_5_done_evidence`,
`inv_9_unique_dec_ids`, `finding_references`, `status_disagreements`, and
`parked_lines` do not. One byte in `adocs/plan.md`:

```
$ printf '4. S004 caf\xe9 latin-1\n' >> adocs/plan.md
--validate           exit=1  UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 ...
--post-write         exit=1  UnicodeDecodeError: ...
--stop               exit=1  UnicodeDecodeError: ...
--session-start      exit=1  UnicodeDecodeError: ...
--step status        exit=1  UnicodeDecodeError: ...
```

One byte in an audit report, which is the S049 twin:

```
--validate       exit=1  UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 83
--post-write     exit=1  UnicodeDecodeError: ...
--stop           exit=1  UnicodeDecodeError: ...
--audit list     exit=1  UnicodeDecodeError: ...
```

Impact: low, because the `Write` tool and `--log-prompt` both emit UTF-8, so this
needs a `Bash` heredoc, a pasted terminal capture, or a file written by another
tool. Real, because an audit report full of pasted command output is the most
likely place for it, and the consequence is the same as F01 — a `Stop` hook at
exit 1 with a traceback, enforcing nothing, and `--session-start` producing no
JSON at all, so the SessionStart channel that S014 depends on is silent too. It is
also the recurring shape in miniature: S049 added `hidden_findings` next to
`report_findings` and gave the new one the tolerant read without changing the old
one, so INV-14's two halves cannot both survive the same file.

Suggested resolution: one decode policy for every file moltke reads. Reading with
`errors="replace"` everywhere is the smaller change and matches what the newer
readers already do; refusing with a message naming the file and the byte offset is
the louder one and would be defensible for `plan.md` and `decisions.md`. Either
way, make it one helper rather than thirteen call sites. Red-first case: a
non-UTF-8 byte in a `plan_done/` step file and in an audit report, asserting no
mode exits 1 with a traceback. Not applied here.

### 2026-08-08_adversarial-F06  low  MANUAL says an INV-7 or INV-8 violation names the commit that did the tampering; it names the baseline commit

Status: open

Evidence: `MANUAL.md:307-308` reads "Committing tampering therefore does not hide
it: the violation names the commit that did it." `bin/moltke.py:342-350` names the
commit that *added* the `plan_done/` file, and `bin/moltke.py:410-416` names the
high-water-mark commit for `decisions.md`. In a fixture where `8d4dc8df` adds
`S001_base.md`, an unrelated commit follows, and `b1c076a5` is the commit that
rewrites both files:

```
adding commit   : 8d4dc8df
tampering commit: b1c076a5

$ moltke.py --validate
VIOLATION: INV-7: adocs/plan_done/S001_base.md no longer matches the version that landed at
commit 8d4dc8df; plan_done/ is append by move only. ...
VIOLATION: INV-8: adocs/decisions.md no longer contains, in order, the lines it had at commit
8d4dc8df; nothing it has held is removed or reordered, ...
exit=1
```

`b1c076a5` appears nowhere. The paragraph immediately below, `MANUAL.md:312-318`,
describes the mechanism correctly — "compare what the file says **now** against a
version from history — for a `plan_done/` file, the one at the commit that added
it; for `decisions.md`, the most recent version that had not already lost
something" — so the document contradicts itself within five lines.
`2026-08-07_adversarial.2-F07` named exactly this sentence; S054 corrected
`adocs/specs.md:35` and `MANUAL.md:320-327` and left it.

Impact: low and documentation-only. It matters because it is the sentence a reader
uses to decide where to look: told the violation names the tampering commit, they
`git show 8d4dc8df` expecting the bad change and find the legitimate one that
first added the file. It is also the second run in a row that this sentence has
survived being named.

Suggested resolution: reword `MANUAL.md:308` to "the violation names the commit
whose content it is comparing against, and restoring those bytes in a new commit
clears it", which is what the messages say and what the next paragraph already
explains. Not applied here.

## What was checked and found sound

Recorded so a later run knows this ground was covered, and so the findings above
are not read as a verdict on the whole of S028..S057.

- **No mutation survived.** Sixteen behaviours introduced by this batch were each
  deleted in a copy of the repository outside it and the full suite re-run.
  All sixteen went red: dropping INV-14 from `INVARIANT_CHECKS` (3 failures),
  removing hidden findings from `--audit list` (1), narrowing `_arrives_here` back
  to `("??", "A ")` (2), removing `porcelain_paths`' rename split (3), removing
  `--step`'s missing-`adocs/` refusal (4), flattening `_stale_remedy` (1), making
  `fence_markers` count raw text for INV-13 (3), making `foreign_worklog_lines`
  return nothing (2), removing the `--session-start` planning nudge (4), making
  `template_drift` always abstain (3), dropping INV-15 (13), replacing `mode_step`'s
  `OSError` handler (1), unscoping `own_finding_headings` from the report stem (6),
  taking INV-14 out of `CHEAP_CHECKS` (1), removing `plan.md`/`decisions.md`/
  `worklog.md` from INV-13's list (1), and putting the real stem back into the
  audit report template's fenced example (4). The last two runs each had one
  survivor; this one has none.
- The S050 tests are non-vacuous by construction: each move-shape test asserts
  `assertIn(" -> ", porcelain, "precondition: git recorded this as a rename")`
  before asserting the gate fired, and `test_the_stamp_gate_is_not_simply_always_on`
  is the other half.
- A fresh `--scaffold` in a repository with history produces `--validate` exit 0,
  a `--session-start` that names both unfilled files, and a `status.md` that
  `status_disagreements` reads as current. The second `--scaffold` creates nothing
  and reports every kept file as matching the installed template; editing
  `AGENTS.md` makes the third report `differs from the installed template` and
  names it in the closing drift line, without changing the file.
- `--audit check`'s worklog corroboration is right in both directions on the cases
  that matter: a multi-line prompt containing a recap heading and a fence arrives
  quoted and stays `expected`; a fabricated recap appended from `Bash` is
  `unexpected` and the note says what it does to the recap gate.
- INV-7's scoped porcelain reads a `git mv` into `plan_done/` as `A `, not `R `, so
  the pathspec does suppress rename detection and a legal completion is not
  reported as tampering.
- `README.md`'s "286 tests, no skips" is accurate at this commit, and its "No
  environment variables" claim holds: `bin/moltke.py` imports neither `os` nor
  anything that reads the environment.
- INV-14's stem scoping behaves as documented on this report: the verdict section
  above quotes ten foreign finding ids and none of them is treated as a finding of
  this file.
