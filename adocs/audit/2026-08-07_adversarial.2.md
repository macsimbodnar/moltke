# Audit 2026-08-07 adversarial (re-run 2)

Scope: `bin/moltke.py` at commit `b8b4345` plus one uncommitted change,
`.claude-plugin/plugin.json` bumped `0.3.0` → `0.4.0`; `hooks/hooks.json`,
`agents/adversarial_reviewer.md`, `skills/`, `tests/`, and the claims made about
them in `README.md`, `MANUAL.md`, `adocs/specs.md`, and `AGENTS.md`.

Method: two jobs. First, a verdict on each of the eleven findings in
`adocs/audit/2026-08-07_adversarial.md`, decided against the code at `b8b4345`
and reproduced with `bin/moltke.py` in throwaway repositories under `/private/tmp`,
never against the step files, the testing ledger, or the commit messages. Second,
a fresh adversarial pass over the fourteen steps of new checker surface that
landed since (S032..S042, S045, S046), including mutation testing: seventeen new
behaviours were each deleted in a copy of the repository outside it and the suite
re-run, to see whether the tests that name them actually bite.

Baseline at the start of the run:

```
$ python3 -m unittest discover -s tests
Ran 228 tests in 48.740s
OK
$ python3 bin/moltke.py --validate
moltke: all checks pass
```

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name:

```
### 2026-08-07_adversarial.2-F01  high  short title

Status: open

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
```

Every finding ends in one of two places: a plan step whose `closes:` field
names it, or a decision entry stating why it will not be acted on, which moves
it to `accepted`. A finding moves to `closed` only after the audit is re-run
and no longer reports it. Fixing without re-running leaves it `planned`.

Summary: 10 new findings. 2 high, 4 medium, 4 low. Of the eleven prior findings,
ten no longer reproduce and one (F02) still reproduces on its primary evidence
path. The prior `2026-08-06_adversarial-F02` is fixed in this checkout and still
live in the installed plugin, unchanged from the last run.

The batch is good work: sixteen of seventeen mutations went red, and nine of the
eleven fixes are complete rather than partial. The pattern in what is left is
that a rule was tightened in one place and its twin was not — `plan_order` was
narrowed to list entries while INV-3 still reads the whole file; INV-13 counts
markers in raw text while `strip_guidance` counts them after comment removal;
`git_dir` restored the Stop cap in a worktree and left the no-git case; the Stop
recap and stamp gates read `git status` porcelain without handling the `R` line
that `git add -A` produces.

## Verdicts on the 2026-08-07 findings

One line each, decided against the code at `b8b4345`. All eleven were reproduced
or refuted by running the tool, not by reading the step files.

- **F01** (`--audit check` cannot see a change the run commits) — **no longer
  reproduces**. In a committed fixture, patching a clean tracked file and
  committing it during the run now gives `src/main.py: M in a commit made during
  this run` under `unexpected`, exit 1; weakening an existing test and committing
  it gives `tests/test_existing.py: M in a commit made during this run`, exit 1.
  The report itself committed is classified `expected`. `bin/moltke.py:1430-1447`.
- **F02** (an unbalanced code fence hides an open finding) — **still reproduces
  on its primary evidence path; the recap-gate half no longer reproduces.** The
  J2 case from the original report, re-run verbatim, gives the same two exit
  codes it gave then. See F02 below for the transcript and for the documentation
  that now says otherwise. INV-13 does not fire, because two unclosed fences are
  an *even* number of markers. The C4 case (a stray fence in a recap plus a fenced
  paste in the next prompt) is genuinely fixed: prompt bodies arrive quoted, the
  marker is no longer line-anchored, and the odd count that remains is reported
  by INV-13 while `--stop` still blocks, exit 2.
- **F03** (one committed tampering makes INV-7 and INV-8 permanently red) — **no
  longer reproduces**. Tampering with `adocs/plan_done/S001_base.md` and removing
  a line from `adocs/decisions.md`, committed, gives two violations, exit 1;
  doing exactly what the messages say — restoring the bytes in a new commit —
  gives `moltke: all checks pass`, exit 0, and `--stop` exit 0. No history rewrite
  was needed.
- **F04** (linked worktree loses the audit baseline, the log breadcrumb, and the
  Stop cap) — **no longer reproduces**, in a linked worktree *and* in a submodule.
  In both, `.git` is a file, `--audit new` records a baseline, `--audit check`
  exits 0, and the Stop cap reads `[2, 2, 2, 0, 0]`. State lands in
  `.git/worktrees/<name>/` for the worktree and in the submodule's own git dir.
  One condition the fix does not cover is a repository with no git at all: see
  F06 below.
- **F05** (`--audit check` blames the plugin's own worklog write on the reviewer)
  — **no longer reproduces**. `--audit new`, one `--log-prompt`, then `--audit
  check` gives `adocs/worklog.md: M` under `expected`, exit 0. A rewrite of the
  same file is still `unexpected`, exit 1. See F09 below for what the exemption
  now lets past.
- **F06** (the Stop recap gate treats `.claude-plugin/` as not-source) — **no
  longer reproduces**. Measured one path at a time: `src/main.py` blocks,
  `bin/moltke.py` blocks, `.claude-plugin/plugin.json` blocks, `.claudefoo`
  blocks, `adocsfoo/x.md` blocks; `.claude/settings.json` and `adocs/specs.md`
  allow.
- **F07** (a malformed `test_command` silently turns the suite gate off) — **no
  longer reproduces**. Empty string, whitespace, a list, and a number each make
  `--step done` refuse with the marker violation, exit 1, and the step stays in
  `plan_current/`. `--step new`, `--step start`, and `--step status` refuse too.
- **F08** (`status.md` staleness detected only through `Next:`) — **no longer
  reproduces**. With `plan_current/` holding `S003` and `status.md` saying
  `In progress: none`, `Last done: S999`, `--stop` reports both fields, exit 2,
  and `--session-start` reports both.
- **F09** (`--audit new <type>` writes outside `adocs/audit/`) — **no longer
  reproduces**. `../../outside/pwned`, `UPPER.2`, `with space`, and the empty
  string are each refused before anything touches the filesystem, exit 1; no
  stray directory is created.
- **F10** (the reviewer's `tests/` allowance is escapable with a relative `..`)
  — **no longer reproduces**. `tests/../bin/newfile.py`, `tests/../bin/moltke.py`,
  `./tests/./../bin/x.py`, the same via hook stdin, and a `tests/link -> ../bin`
  symlink are all exit 2. `tests/newtest.py` is still allowed and
  `tests/test_x.py` (existing) is still blocked.
- **F11** (the `test_command` refusal writes to both streams) — **no longer
  reproduces**. A failing gate puts everything on stderr and leaves stdout empty,
  exit 1. On a passing gate the banner is stderr on an exit 0 path, which
  `adocs/specs.md:57-64` documents.

### Verdict on 2026-08-06_adversarial-F02 (reviewer write fence), status `planned`

**Fixed in this checkout; still reproducing in the installed plugin; not
settleable here for a live session.** Unchanged from the previous run, and the
reason is unchanged: nothing has been reinstalled.

```
$ python3 -c "import json;d=json.load(open('$HOME/.claude/plugins/installed_plugins.json'));print(d['plugins']['moltke@moltke'])"
[{'scope': 'user', 'installPath': '/Users/max/.claude/plugins/cache/moltke/moltke/0.2.0',
  'version': '0.2.0', 'gitCommitSha': '106477472b03ab75b67b269e505ab65d929169f7', ...}]

$ grep -n agent_type ~/.claude/plugins/cache/moltke/moltke/0.2.0/bin/moltke.py
408:    if payload.get("agent_type") == REVIEWER_AGENT and parts[:2] != (DOCS, "audit"):

$ for p in bin/moltke.py tests/brand_new_test.py adocs/audit/x.md
      printf '{"agent_type":"moltke:adversarial_reviewer","tool_input":{"file_path":"/Users/max/ws/moltke/'$p'"}}' | \
        python3 ~/.claude/plugins/cache/moltke/moltke/0.2.0/bin/moltke.py --pre-write
  bin/moltke.py                exit=0
  tests/brand_new_test.py      exit=0
  adocs/audit/x.md             exit=0

  ... the same three payloads against this checkout:
  bin/moltke.py                exit=2  moltke: the adversarial_reviewer may write under adocs/audit/ ...
  tests/brand_new_test.py      exit=0
  adocs/audit/x.md             exit=0
```

The cache directory holds only `0.2.0`, `bin/moltke.py` there differs from the
checkout, and `~/.claude/settings.json` enables `moltke@moltke` from the hosted
git marketplace, so every hook firing on this machine today runs the
bare-equality version. The fence is open live and the checkout's fix is not in
effect until 0.4.0 is published and installed. `--audit new` on this repository
was run from the checkout, not from the plugin — the baseline in
`.git/moltke_audit_baseline.json` carries the `worklog` key that only 0.4.0
writes — so the two copies are genuinely both in play.

## Findings

### 2026-08-07_adversarial.2-F01  high  the Stop deadlock waiver keys on a `prompt_id` nothing establishes exists, and without one it turns every Stop check off permanently

Status: open

Evidence: `mode_stop` (`bin/moltke.py:875-897`) counts consecutive blocks per
`hook_input().get("prompt_id", "")` and, past `STOP_CAP`, returns `EXIT_OK`
without printing the problems. `prompt_id` appears nowhere in `adocs/specs.md`,
`adocs/decisions.md`, `MANUAL.md`, or `README.md`; the only uses are
`bin/moltke.py:877,882,886` and two tests that supply it themselves
(`tests/test_s005_hooks.py:435,446`). Every other hook field in the file carries
a dated live observation in a comment — `bin/moltke.py:702` for UserPromptSubmit
exit 2, `bin/moltke.py:753-756` for `agent_type` — and this one does not, while
the comment immediately above the cap (`bin/moltke.py:889-890`) cites live docs
only for the absence of a built-in cap.

When the key is absent the counter is global, never resets while the repository
stays broken, and lives on disk. In a fixture whose only fault is one INV-3
violation:

```
$ for i in 1..8; printf "{}" | moltke.py --stop; echo $status
2 2 2 0 0 0 0 0

$ cat .git/moltke_stop_state.json
{"prompt_id": "", "count": 8}

$ printf "{}" | moltke.py --stop        # turn 9, stderr
moltke: still blocked after 3 attempts; allowing stop so the session is not deadlocked. Run bin/moltke.py --validate and fix by hand.

$ moltke.py --validate                  # the violation never went away
VIOLATION: INV-3: plan.md lists S099 but no step file exists in plan_todo/, ...
```

Control, one distinct `prompt_id` per turn, which is the intended shape:

```
$ for i in 1..8; printf '{"prompt_id":"p'$i'"}' | moltke.py --stop; echo $status
2 2 2 2 2 2 2 2
```

Two further reachable routes to the same empty key, independent of what Claude
Code sends: `hook_input` returns `{}` on any `JSONDecodeError` or `OSError`
(`bin/moltke.py:521-529`), which is deliberate fail-open, and it returns `{}`
when stdin is a tty, so `python3 bin/moltke.py --stop` run by hand writes
`"prompt_id": ""` too.

Not confirmed: whether a live `Stop` payload carries `prompt_id`. I could not
observe one — this repository's `.git/moltke_stop_state.json` does not exist
right now, which means the last Stop was clean rather than that the key is
present, and I will not provoke a live hook from inside an audit. If the key is
real and distinct per turn the finding narrows to the two fail-open routes above;
if it is not, the Stop hook silently stops enforcing anything — invariants, stale
`status.md`, the recap gate, the README/MANUAL stamp — from the fourth blocked
turn of a session onward, and stays off across sessions because the state file
persists.

Impact: `adocs/specs.md:42` states INV-12 and `adocs/specs.md:297-300` states the
cap "after 3 consecutive blocks for the same prompt". The scoping word "same
prompt" is what makes the waiver safe; without it the waiver is not a
deadlock-breaker but an off switch. Worse either way: when the cap fires the
problems are never printed, so a user who hits it is told to run `--validate` and
is given no indication of how many turns of enforcement have already been waved
through.

Suggested resolution: derive the per-turn key from a field the payload is known
to carry — `session_id` plus a monotonic counter, or the `transcript_path` size,
or a timestamp bucket — and record the live observation in `decisions.md` the way
S016 did for `agent_type`. Independently, print the problems alongside the waiver
line so the waived turn still says what was wrong, and reset the counter when the
problem set changes rather than only when it empties. Not applied here.

### 2026-08-07_adversarial.2-F02  high  a step listed in `plan.md` only in prose is invisible to the derived next step, and `--validate` says all checks pass

Status: open

Evidence: S045 narrowed `plan_order` to list entries (`PLAN_ENTRY_RE`,
`bin/moltke.py:544-557`) and left INV-3's forward check reading every id in the
whole file (`re.search(rf"\b{step_id}\b", plan)`, `bin/moltke.py:173`). The two
now disagree about what "listed in `plan.md`" means, so a step file can satisfy
the invariant and still never become the next step. Reproduced:

```
$ cat adocs/plan.md
# Plan

Description: S001 laid the base. Next we will do S002, then think about it.

## Steps

1. S001 base

$ ls adocs/plan_todo/
S002_pending.md

$ moltke.py --validate
moltke: all checks pass
exit=0

$ moltke.py --session-start
moltke: plan_current/ is empty.

$ grep Next adocs/status.md
- Next: no steps left in plan.md

$ moltke.py --stop; echo $status
exit=0
```

`S002` has a step file in `plan_todo/`, is named in `plan.md`, passes INV-3,
passes every other invariant, and does not exist as far as the tool is concerned.
`--session-start` prints no `Derived next step` line at all, and `--step status`
writes `no steps left in plan.md` into the file whose job is to say what is next.

The same divergence makes INV-3's reverse message false. With `S099` named only
in a prose line and a normal two-entry list:

```
$ moltke.py --validate
VIOLATION: INV-3: plan.md lists S099 but no step file exists in plan_todo/,
plan_current/, or plan_done/; create it with --step new, or fix the id in
plan.md — until then S099 is the derived next step and cannot be worked on

$ moltke.py --session-start
Derived next step: S002 (first in plan.md order not in plan_done/).
```

The violation asserts `S099 is the derived next step`; the derived next step is
`S002`. Before S045 that sentence was true, which is what S024 wrote it for.

This repository's own `plan.md` carries the same stale claim in prose at the
paragraph after entry 28: "the derived next step is the first id in document
order, so an id mentioned in prose above the list becomes the next step instead."
That is the pre-S045 behaviour, written into the plan as a warning, in a file
that also contains prose paragraphs between numbered entries — the exact shape
that triggers the defect in the other direction.

Impact: this violates the prime directive directly — `adocs/specs.md:20-22`,
"project state is always derivable from tracked files alone. An agent that trusts
nothing but the filesystem knows what to do next". Here the filesystem holds a
pending, planned, valid step and every derivation says there is nothing left.
Silent: exit 0 from `--validate`, `--stop`, and the hook. Reachable by any hand
edit of `plan.md` that names an id outside the numbered list, which is what
prose about ordering looks like; `--step new` is safe because it appends a list
entry.

Suggested resolution: make INV-3's forward check read `plan_order(root)` rather
than the whole text, so "listed in plan.md" means one thing; make the reverse
check read the list too, and reword its message to what it now enforces. Add a
red-first case for a step file whose id appears only in prose. Not applied here.

### 2026-08-07_adversarial.2-F03  medium  `git add -A` turns off both Stop gates for a moved file, and the README/MANUAL gate has no test at all

Status: open

Evidence: `mode_stop` reads `git status --porcelain` and classifies each line by
`line[:2]` and `line[3:]` (`bin/moltke.py:853-873`). A staged rename is one line,
`R  <old> -> <new>`: the status code is `R `, which is in neither `("??", "A ")`
for the stamp gate nor anything the recap gate recognises, and `line[3:]` is the
**old** path, which is what `RECAP_EXEMPT` is tested against. `AGENTS.md` §4 and
`bin/moltke.py:766-769` both name `git mv` as the way a completed step reaches
`plan_done/`, and every commit is preceded by `git add -A`.

The stamp gate, same fixture three ways, `done: 2026-08-07 suite green` — no
README, no MANUAL:

```
=== control: plain mv, destination untracked ===
   D adocs/plan_current/S001_thing.md
  ?? adocs/plan_done/S001_thing.md
  stamp complaints: 1     exit=2

=== git mv, the command AGENTS.md 4 and the pre-write hook both name ===
  R  adocs/plan_current/S001_thing.md -> adocs/plan_done/S001_thing.md
  stamp complaints: 0     exit=0

=== mv then git add -A, the state every commit passes through ===
  R  adocs/plan_current/S001_thing.md -> adocs/plan_done/S001_thing.md
  stamp complaints: 0     exit=0
```

The recap gate, same mechanism, opposite direction — moving a file out of
`adocs/` into source is judged by its old path and reads as exempt:

```
=== git mv adocs/notes/thing.py src_thing.py ===
  R  adocs/notes/thing.py -> src_thing.py
  recap demands: 0

=== control: the same move, unstaged ===
   D adocs/notes/thing.py
  ?? src_thing2.py
  recap demands: 1
```

And nothing in the suite notices if the stamp gate is deleted outright. Deleting
the whole block at `bin/moltke.py:865-873` in a copy of the repository outside it:

```
GREEN (survivor)  STOP_no_stamp_gate   Ran 228 tests ... OK
```

It was the only survivor of seventeen mutations. `adocs/specs.md:301-302` and
`MANUAL.md:187-188` both state the gate; no test names it.

Impact: the Stop stamp gate is the backstop for the hand-completion path that
`AGENTS.md` §4 permits, and it is off on exactly that path — `git mv` bypasses it
and so does `mv` followed by `git add -A`. `--step done` still enforces the stamp,
so the tool path is covered; a step completed by hand and staged is not, and a
completion with no README/MANUAL check recorded goes to `plan_done/`, which is
immutable, with nothing having asked. The recap half is smaller but the same bug:
a file promoted from documentation to source in one `git mv` needs no recap.
Because no test covers either, a future refactor of this block is unprotected.

Suggested resolution: split porcelain rename lines on ` -> ` and judge the
destination, in both gates, exactly as `worktree_state` already does at
`bin/moltke.py:1293-1294`; treat `R ` as a new arrival for the stamp gate. Add a
red-first test for the stamp gate in all three move shapes, and a case for a
rename out of `adocs/` in `test_which_paths_count_as_source`. Not applied here.

### 2026-08-07_adversarial.2-F04  medium  MANUAL says the two-unclosed-fence hole is pre-0.4.0; it reproduces at `b8b4345`

Status: open

Evidence: `MANUAL.md:242-247` states, in the past tense, "before 0.4.0, a report
with two unclosed evidence blocks lost the finding between them and `--audit list`
did not mention it at all." It still does. This is the J2 case from
`2026-08-07_adversarial-F02`, re-run verbatim on the current code — control
first, so the exit 0 is not the checker being broken:

```
=== control: both fences closed ===
$ moltke.py --validate
VIOLATION: INV-10: open finding 2026-08-01_adversarial-F02 in
2026-08-01_adversarial.md has no step closes: reference and no decisions.md
entry; plan it or record why it is accepted
exit=1

=== the two closing markers removed, nothing else changed ===
$ moltke.py --validate
moltke: all checks pass
exit=0

$ moltke.py --audit list
2026-08-01_adversarial.md
  2026-08-01_adversarial-F01  accepted  (no reference)
exit=0
```

The open finding is not reported as unreferenced. It is not listed. INV-13 is
silent because the marker count is even, which is the whole point — two unclosed
fences are two markers:

```
$ python3 -c "... import moltke; p=Path('adocs/audit/2026-08-01_adversarial.md') ..."
fence markers: 2 (even -> INV-13 silent)
report_findings: [('2026-08-01_adversarial-F01', 'accepted')]
stripped text: '# Audit\n\n### 2026-08-01_adversarial-F01  high  one\n\nStatus: accepted\n\nevidence two\n'
```

`adocs/specs.md:153-158` and `MANUAL.md:250-255` are honest about the ambiguity
and say the odd case is reported rather than guessed. What is wrong is the
sentence before them, which reads as a release note for a hole that is open, and
the fact that the finding it describes is still `open` in
`adocs/audit/2026-08-07_adversarial.md` while `adocs/plan_done/S033_*` claims it.

Impact: a reader of `MANUAL.md` concludes an audit report cannot silently lose a
finding, and it can — the failure mode is unchanged for any report whose evidence
blocks are unclosed in pairs, which is what happens when a reviewer pastes two
transcripts and forgets both closers. Compounding it, `--post-write` deliberately
does not run INV-13 (`adocs/specs.md:157`), so the feedback a reviewer gets
immediately after saving a report is INV-10 read through the broken pairing, and
never the imbalance warning.

Suggested resolution: this needs a decision, not a patch, because it is the
ambiguity S033 recorded. Options worth weighing: require a language tag or a
blank line after a closing marker so openers and closers are distinguishable;
warn when a fenced block swallows a `### ` heading that looks like a finding id
or a `## ` worklog heading, which is a content signal rather than a count; or
have `--audit new` and `--post-write` report the *number of findings visible*
next to the number of `-F<nn>` headings in the raw text, so a mismatch is loud
without needing to resolve the ambiguity. Meanwhile correct `MANUAL.md:245-247`
to the present tense and leave `2026-08-07_adversarial-F02` open. Not applied here.

### 2026-08-07_adversarial.2-F05  medium  S039 now steers the user into `--step status`, which dies with a traceback in a marked repository that has no `adocs/`

Status: open

Evidence: `status_disagreements` (`bin/moltke.py:590-601`) compares four rendered
fields, and a missing `status.md` yields four disagreements, so `--session-start`
and `--stop` both instruct `--step status`. `step_status` (`bin/moltke.py:1264`)
writes `adocs/status.md` without creating `adocs/`. A marked repository whose
`adocs/` does not exist is the exact condition S014 fixed for `--log-prompt`
(`bin/moltke.py:710-712`), so it is a state the code already knows is reachable:

```
$ ls -A
.git  .moltke.json  README.md

$ moltke.py --session-start
moltke: plan_current/ is empty.
status.md is stale (Last done says 'nothing', filesystem says 'nothing yet';
In progress says 'nothing', filesystem says 'none'; Next says 'nothing',
filesystem says 'no steps planned yet'; Blocked says 'nothing', filesystem
says 'none'); regenerate it with --step status before working.

$ moltke.py --step status
Traceback (most recent call last):
  ...
  File "bin/moltke.py", line 1264, in step_status
    (root / DOCS / "status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
FileNotFoundError: [Errno 2] No such file or directory: '.../adocs/status.md'
exit=1
```

The crash predates this batch; the instruction to run into it does not. The same
repository under `git show 10f8830:bin/moltke.py`, the pre-S039 code:

```
$ python3 moltke_pre_s039.py --session-start
moltke: plan_current/ is empty.
```

No staleness line, because the old check compared two extracted step ids and both
were `None`. The new check compares rendered strings, and `{}` never equals a
rendered value, so a missing file is now maximally stale.

Two sibling crashes on the same shape, both exit 1 with a stack trace rather than
a refusal: `--step done` when `adocs/plan_done/` is absent
(`path.rename`, `bin/moltke.py:1202`) and `--step start` when
`adocs/plan_current/` is absent (`bin/moltke.py:1095`). `mode_step` catches only
`IndexError` (`bin/moltke.py:1553`).

Impact: an agent that follows the hook's own instruction gets a Python traceback,
which is neither of the two things `README.md:71-76` says exit 1 can be. The
`--stop` gate then keeps blocking on the same four lines until the cap waives it
(F01), so the turn ends with the tool having asked for something impossible and
then having stopped asking. Worst on a freshly marked repository, which is the
first thing a new user has.

Suggested resolution: `mkdir(parents=True, exist_ok=True)` on the destination in
`step_status`, `step_done`, and `step_start`, matching what `--log-prompt` and
`write_step` already do; and catch `OSError` in `mode_step` and turn it into a
`refuse`. Add a case asserting `--step status` succeeds in a marked repository
with no `adocs/`. Not applied here.

### 2026-08-07_adversarial.2-F06  medium  the Stop deadlock cap still does not exist in a marked repository without git

Status: open

Evidence: `_stop_state_path` (`bin/moltke.py:800-802`) returns `None` when
`git_dir` finds no git, and `mode_stop` then never increments or reads a count,
so `count` is 1 forever and the `count > STOP_CAP` branch is unreachable
(`bin/moltke.py:875-897`). S035 fixed the worktree and submodule cases by asking
git; the case where git genuinely is not there was not part of the finding and is
unchanged. `--scaffold` works in any directory (`scaffold_root`,
`bin/moltke.py:924-934`), so a marked repository with no git is a state the tool
creates.

```
$ ls -A                       # scaffolded, never git init'ed
.moltke.json  AGENTS.md  CLAUDE.md  adocs  .cursor
$ git rev-parse --is-inside-work-tree
fatal: not a git repository (or any of the parent directories): .git

$ for i in 1..6; printf '{"prompt_id":"p1"}' | moltke.py --stop; echo $status
2 2 2 2 2 2

$ printf '{"prompt_id":"p1"}' | moltke.py --stop
moltke: INV-3: plan.md lists S099 but no step file exists in plan_todo/, ...
moltke: status.md is stale or missing: Next says 'no steps planned yet', ...
```

Contrast, same fixture with git, from the F04 verdict above: `[2, 2, 2, 0, 0]`.

Impact: `adocs/specs.md:42-43` states INV-12 with DEC-006's reason — a `Stop` hook
has no built-in cap and an unactionable message deadlocks the session — and
`bin/moltke.py:889-890` calls the cap "the no-deadlock property of DEC-006 /
INV-12". In a marked repository without git that property is absent, and every
Stop blocks. It is recoverable by hand, but the recovery is outside the session:
the agent cannot end its turn. `MANUAL.md:340-346` describes the state files as
located by asking git and does not say what happens when the answer is "there is
none".

Suggested resolution: fall back to a location that does not need git for the
Stop state alone — the counter is not history and does not need to be untracked
in the git sense, only unnoticed, so `adocs/` is wrong but a fixed path under the
system temp directory keyed by the resolved root would do — or keep the count in
memory-free form by treating "no state file writable" as "waive after the first
block", which is the safe direction for a gate whose purpose is not to deadlock.
This is a decision, not an obvious patch. Not applied here.

### 2026-08-07_adversarial.2-F07  low  INV-8 as enforced is a line subsequence, so a fabricated decision inserted mid-file commits green against an invariant that says earlier bytes never change

Status: open

Evidence: `inv_8_append_only` compares the current file against a high-water mark
with `lines_survive` (`bin/moltke.py:340-343, 378-393`), which asks only that
every required line still appear in order. Insertion is not a removal and not a
reordering, so it passes. The uncommitted window is covered by the byte-prefix
check against HEAD (`bin/moltke.py:394-408`); one commit closes it forever:

```
$ moltke.py --validate                       # baseline, two decisions
moltke: all checks pass

=== insert a whole new entry between DEC-001 and DEC-002, then commit ===
$ moltke.py --validate
moltke: all checks pass
exit=0

$ grep -n "^Decision:" adocs/decisions.md
21:Decision: d1
28:Decision: forged        <- DEC-003, inserted above DEC-002
35:Decision: d2
```

Control, in the same fixture: rewriting `Decision: d1` in place and re-appending
the original line at the end is caught, exit 1, so the removal side of the rule
does bite.

`adocs/specs.md:35` states INV-8 as "`decisions.md` grows only by appending;
earlier bytes are unchanged", and the violation message the code prints says "it
grows only at the end". Neither is what runs. `adocs/specs.md:180-181` does record
the consequence — "mid-file insertion passes, because only removal and reordering
break a subsequence" — but as a note under S046 rather than as an amendment to
INV-8's own line, so the invariant list and the note disagree and the invariant
list is what `AGENTS.md` §3 points a new agent at.

Separately, `MANUAL.md:275-283` still describes the pre-S046 rule: "Both checks
compare what the file says **now** against the version it had at a fixed point —
the commit that added a `plan_done/` file, the first commit for `decisions.md`."
S046 replaced the fixed first commit with a walked high-water mark, which is
strictly stronger and is the whole content of that step. The same paragraph says
"the violation names the commit that did it"; the messages name the commit the
content is compared against — `bin/moltke.py:325` names the adding commit,
`bin/moltke.py:388` names the mark — not the tampering commit.

Impact: low, because an inserted entry cannot change what an existing `DEC-<nnn>`
citation resolves to and INV-9 still catches a duplicate id. Real, because
`AGENTS.md` §8 depends on order — "append only, newest last ... recency is
`tail`" — and an entry inserted above later ones makes `tail` lie about what was
decided most recently, which is the one read the format is optimised for. The
documentation half matters more than the code half: a reader of `MANUAL.md`
understates what INV-8 now does and misreads which commit a violation names.

Suggested resolution: decide whether mid-file insertion is legal. If it is,
amend `adocs/specs.md:35` with a dated inline note the way F12 was handled, so
the invariant statement matches the rule; if it is not, require the mark's lines
to be a *prefix* of the current lines rather than a subsequence, which is one
word of change and still clears on repair. Either way, bring `MANUAL.md:275-283`
up to S046. Not applied here.

### 2026-08-07_adversarial.2-F08  low  INV-13 counts markers `strip_guidance` never sees, so a fence inside an HTML comment blocks `--stop` with a message that is false for that file

Status: open

Evidence: `inv_13_balanced_fences` counts `FENCE_MARKER` in the raw file
(`bin/moltke.py:496`). `strip_guidance` removes HTML comments *before* it looks
for markers (`bin/moltke.py:102-110`). A marker inside a comment is therefore
counted by the invariant and not by the thing the invariant exists to protect:

```
$ cat adocs/audit/2026-08-01_adversarial.md
# Audit

<!-- reviewers: an evidence block opens with
    (a triple-backtick marker on its own line)
and the checker pairs markers in order -->

### 2026-08-01_adversarial-F01  high  one

Status: accepted

    (a properly opened and closed evidence block)

$ grep -cE '^ {0,3}```' adocs/audit/2026-08-01_adversarial.md
3                                    <- what INV-13 counts
markers strip_guidance sees:  2      <- after comment removal
findings seen (correct):      [('2026-08-01_adversarial-F01', 'accepted')]

$ moltke.py --validate
VIOLATION: INV-13: adocs/audit/2026-08-01_adversarial.md has 3 code-fence
markers, an odd number, so one fence is unclosed. Every scanner reads this file
through strip_guidance, which pairs markers in order: close the fence, or the
content it swallows is invisible to the checks that read this file
exit=1

$ moltke.py --stop
moltke: INV-13: adocs/audit/2026-08-01_adversarial.md has 3 code-fence markers, ...
exit=2
```

Nothing is swallowed and no finding is lost; the message says otherwise and the
turn is blocked. Following it — closing the fence — adds a marker to a file whose
effective pairing was already correct.

Impact: low, and self-inflicted in the sense that it needs a marker inside a
comment. It is the shape an audit report or a decision entry discussing fences
naturally takes, which is not hypothetical here: `MANUAL.md`, `adocs/specs.md`,
and both existing audit reports all discuss fence markers in prose. The failure
direction is safe (a false block, not a false pass) but it blocks `--stop`, which
under F01 above burns three of the three attempts before the gate waives itself.

Suggested resolution: count markers in the comment-stripped text — one
`re.sub(r"<!--.*?-->", "", text, flags=re.S)` before `FENCE_MARKER.findall`, or
better, have `strip_guidance` return the marker count alongside the text so the
invariant and the stripper can never diverge again. Add a case with a marker
inside a comment. Not applied here.

### 2026-08-07_adversarial.2-F09  low  S036's worklog exemption is shape-based, so the reviewer can append to the one file the fence blocks it from, silence the recap gate, and `--audit check` calls it expected

Status: open

Evidence: `classify` in `audit_check` treats `adocs/worklog.md` as expected
whenever `worklog_only_grew` holds (`bin/moltke.py:1404-1412`), and
`worklog_only_grew` checks the shape of the change, not its author
(`bin/moltke.py:1363-1379`). The reviewer's `Write` and `Edit` to that path are
blocked, so the exemption applies to precisely the writes the fence was meant to
stop reaching it another way:

```
$ printf '{"agent_type":"moltke:adversarial_reviewer"}' | moltke.py --pre-write adocs/worklog.md
moltke: the adversarial_reviewer may write under adocs/audit/, and may create
new files under tests/, and adocs/worklog.md is neither. ...
exit=2

$ moltke.py --audit new adversarial
... then, from Bash during the run:
$ echo "print(2)  # patched during the audit" > src/main.py
$ printf '\n## 2026-08-07 recap S001\n\nnothing to see here\n' >> adocs/worklog.md

$ moltke.py --stop
recap demands: 0                       <- the fabricated recap satisfies the gate

$ moltke.py --audit check
expected, this run's report and new tests:
  adocs/audit/2026-08-07_adversarial.md: ??
  adocs/worklog.md: changed again (was M, now M)
unexpected, not attributable to writing the report:
  src/main.py: M
exit=1
```

The source patch is caught, which is the important half. The worklog append is
not mentioned as anything but expected, and it is what turned the Stop recap gate
off for the surrounding turn.

`skills/audit/SKILL.md:41-42` still describes the check as "The report and any new
files under `tests/` are expected; anything else exits 1 and is listed", which no
longer matches the code.

Impact: low. It needs a reviewer that appends to the worklog, which is outside
the role and which DEC-022 already accepts as possible rather than prevented. It
is recorded because S036 traded a false positive for a blind spot in the same
file, and because the blind spot lands on the file the recap gate reads: an
append is the one edit that both passes the exemption and changes a gate's
answer.

Suggested resolution: keep the exemption but describe the append — report
`adocs/worklog.md: appended N lines` under `expected` rather than omitting the
detail, so a reviewer's append is visible even though it is not flagged; or
compare the appended text against what `--log-prompt` would have written (it is
always a `## <stamp> prompt` heading followed by quoted lines) and treat anything
else as unexpected. Update `skills/audit/SKILL.md:41-42` either way. Not applied
here.

### 2026-08-07_adversarial.2-F10  low  the reviewer fence stops at the repository boundary, including for the installed checker's own source, while the agent definition states it unqualified

Status: open

Evidence: `mode_pre_write` returns `EXIT_OK` for any path that does not resolve
under `root` (`bin/moltke.py:745-749`), before the reviewer rule is reached.

```
$ printf '{"agent_type":"moltke:adversarial_reviewer"}' | \
    moltke.py --pre-write ~/.claude/plugins/cache/moltke/moltke/0.2.0/bin/moltke.py
exit=0
$ printf '{"agent_type":"moltke:adversarial_reviewer"}' | \
    moltke.py --pre-write ~/.claude/settings.json
exit=0
```

The first path is the file every hook on this machine executes (see the
2026-08-06-F02 verdict above), and the second is what decides whether the plugin
is enabled at all. Both are `Write`-able by the fenced agent.

`adocs/specs.md:82-86` and `MANUAL.md:215-217` record the boundary deliberately —
"moltke governs the repository it is marked in, and the fence was never the
guarantee". `agents/adversarial_reviewer.md:14` and `skills/audit/SKILL.md:26-27`
do not: both say the hook blocks `Write` and `Edit` outside the two allowed
places, without qualification, and the agent definition is the text the reviewer
actually reads.

Impact: low, and partly by design. Recorded because the two documents that shape
the reviewer's behaviour state a stronger fence than exists, and because the
specific out-of-repository targets include the checker that will judge the run
and the setting that turns it on. `--audit check` cannot see either: it reads
`git status` and `git diff` inside the repository.

Suggested resolution: one sentence in `agents/adversarial_reviewer.md` and in
`skills/audit/SKILL.md` matching what `MANUAL.md:215-217` already says — the
fence covers this repository only, and paths outside it are on you. Optionally
block a reviewer write whose resolved path is under `CLAUDE_PLUGIN_ROOT` or
`~/.claude`, which is a small, closed list. Not applied here.

## What was checked and found sound

Recorded so a later run knows this ground was covered, and so the findings above
are not read as a verdict on the whole of S032..S046.

- **The new tests are not vacuous, with one exception.** Seventeen behaviours
  were each removed in a copy of the repository outside it and the full suite
  re-run. Sixteen went red: reverting `strip_guidance` to global pairing fails
  the S033 line-anchor tests; deleting INV-13 fails two; removing INV-7's content
  comparison fails three S003 tests; reducing INV-8 to the first version, and
  removing its history half entirely, fail two and five S004 tests; putting back
  the `.git`-is-a-directory guess fails the worktree cap test and an S008 audit
  test; dropping the marker refusal from `mode_step` fails five S007 tests;
  reverting staleness to `Next:` only fails four S005 tests; restoring the bare
  `.claude` prefix fails `test_which_paths_count_as_source`; removing the
  `--pre-write` resolve fails the relative-escape tests; removing the audit type
  check fails the S040 tests; moving the suite-gate banner back to stdout fails
  `test_a_failing_test_command_gate`; reverting `plan_order` to document order
  fails `test_prose_above_the_list_does_not_become_the_next_step`; removing the
  worklog exemption fails two S008 tests; removing the recap gate fails several.
  The single survivor is the Stop README/MANUAL stamp gate, which is F03 above.
- `--audit check` catches the committed cases S032 was written for, and keeps the
  uncommitted ones: a committed source patch, a committed weakening of an
  existing test, and a report plus a new test committed together are classified
  correctly, and pre-existing dirt is still not blamed on the run.
- INV-7 and INV-8 both have a legal way back to green, and it is the one the
  message prescribes. A committed deletion out of `plan_done/` is still caught
  twice — once by the porcelain scan, once by the history comparison — and a
  `git mv` *into* `plan_done/` reads as the addition it is, because the scoped
  pathspec suppresses rename detection.
- `git_dir` was verified in three shapes, not one: a plain clone, a linked
  worktree created with `git worktree add`, and a repository consumed as a
  submodule. All three record the audit baseline, reconcile, and reach the Stop
  cap at `[2, 2, 2, 0, 0]`.
- The `--audit new` type check is enforced before any filesystem call, and the
  empty type is refused too, which the finding did not ask for.
- The reviewer fence resists the relative escapes it was built for and one it was
  not: a `tests/link -> ../bin` symlink resolves and is blocked.
- `--validate` on this repository costs about 0.33s despite INV-7 and INV-8 now
  fetching historical blobs; the batched `git cat-file` keeps it to one process
  per invariant over 41 `plan_done/` files and 5 `decisions.md` versions.
- `--audit list` on this repository sees all eleven findings of
  `2026-08-07_adversarial.md` and all fourteen of the 2026-08-06 report; the
  38-marker count in the former is even and pairs correctly.
- Marker counts are even in every shipped template and in every live `adocs/`
  file, so no INV-13 violation is latent in the scaffold.
- `README.md`'s "228 tests, no skips" is accurate at this commit.

## Post-report verification, 2026-08-07

Added after the findings above were written, by appending to this file. No
finding is altered; this records what happened when the report was first saved
to disk, and it settles a question the previous run could only argue from
`installed_plugins.json`.

**The `PostToolUse` hook reported eight of the ten findings.** The first save of
this file held F01 through F10. The hook answered:

```
moltke: INV-10: open finding 2026-08-07_adversarial.2-F01 ... has no step closes: reference ...
moltke: INV-10: open finding 2026-08-07_adversarial.2-F02 ...
  ... F03, F04, F05, F06, F07 ...
moltke: INV-10: open finding 2026-08-07_adversarial.2-F08 ... has no step closes: reference ...
```

F09 and F10 were absent. Running this checkout against the same bytes reports all
ten, and `--audit list` and `--validate` both count ten. Running the installed
plugin's copy against the same bytes reproduces the hook's answer exactly:

```
$ python3 -c "load report_findings from each copy, run it on this file"
installed 0.2.0  report_findings -> [... .2-F01 ... .2-F08]          # 8
checkout 0.4.0   report_findings -> [... .2-F01 ... .2-F10]          # 10
```

Two things follow, neither of them inferences.

First, the hooks firing in this session execute
`~/.claude/plugins/cache/moltke/moltke/0.2.0/bin/moltke.py`, not
`/Users/max/ws/moltke/bin/moltke.py`. The 2026-08-06-F02 verdict above rests on
that and can now stop hedging: the reviewer write fence in force today is the
bare-equality one, and it is open. `MANUAL.md:174-178` already states the general
rule ("Hooks keep running the installed copy, not your checkout"); this is it
happening, with a measurable difference in output.

Second, S033 is a real improvement and this is the measurement. The pre-S033
pairing loses two findings in an ordinary report — this one, written to the
format the repository ships, with command transcripts as evidence — because it
counts triple-backtick markers wherever they occur, including inside a fenced
block and inside a sentence, and every stray one shifts the pairing after it. The
current pairing, line-anchored, gets it right. What it does not get right is the
even-count case, which is F04 above and which stays open.

Nothing in this file was reworded to make the hook happy, because the hook is
running the old code and rewording would only hide the evidence. The current
checker reads all ten findings as written.
