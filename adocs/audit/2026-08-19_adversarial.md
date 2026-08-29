# Audit 2026-08-19 adversarial

Scope: what was examined, at which commit.
Method: how it was examined. Audits run against the code, not against the specs.
An audit that only confirms the documentation is a documentation review.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-19_adversarial-F<nn>`. The example below writes that prefix as
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

## Findings

<!-- Append findings here, most severe first. A report with no findings is a
     valid result: say so explicitly rather than leaving this empty. -->

Scope: the whole repository at commit `047184f7` — `bin/moltke.py` (3035 lines),
`hooks/hooks.json`, `skills/`, `agents/`, `templates/`, `.claude-plugin/`,
`tests/`, and `README.md` / `MANUAL.md` / `adocs/specs.md` read as claims about
code. Verdicts on the six 2026-08-18 findings included, re-measured from each
finding's own reproduction rather than from its step stamp.

Method: read every source file; ran the suite at HEAD (452 pass, 3 skip); drove
`bin/moltke.py` against throwaway git repositories, linked worktrees, and a
monorepo-style tree under a scratch directory; mutation-tested the suite by
copying the tree to scratch, breaking one thing, and re-running. Nothing in this
repository was mutated except the two files this role may write.

What this run changed, so `--audit check` reads cleanly: this report, and the new
red test file `tests/test_2026_08_19_adversarial_findings.py`. That test file was
corrected once after creation through `Bash` (a `python3` string replacement
adding one `mkdir()` to a fixture), because the write fence permits creating a
file under `tests/` and refuses editing one that exists — see F11. Two pre-existing
changes are not this run's: `adocs/status.md` was modified by the spawning session
after `--audit new` recorded the baseline, and `S138_rerun_audit.md` was already
mid-`--step start`.

The new test file is red on purpose (AGENTS.md §6, red first). Full suite with it:
457 tests, 5 failures, all five in that file, all five naming F01 or F03.

## Verdicts on the 2026-08-18 findings

Re-measured, each from that finding's own reproduction:

- F01 (`--log-prompt` reads the wrong key) — stays `accepted`. The mode no longer
  exists: `--log-prompt` is not a flag, argparse refuses it. Residue survives and
  is F08 below.
- F02 (ceiling does not bound one scan) — **fixed**. Its own reproduction
  (`(a+)+$` over 40 `a`s, `--ceiling 1s --interval 5s`) now exits 124 in 1.05s
  wall clock instead of running past 30s.
- F03 (reviewer Bash is unfenced) — stays `accepted` per DEC-053; still true of
  the code, still the chosen design.
- F04 (substring `moltke --watch` bypass) — **fixed**. Both bypasses in its
  reproduction — the trailing comment and the leading `echo` — are refused now.
  `_is_watch_primitive` is a tokenizer, and I could not find a spelling that
  passes it without running the primitive. F06 below is a different escape.
- F05 (Stop gate skips a staged rename) — stays `accepted`; the gate it targeted
  left with DEC-048, and `porcelain_paths` handles renames.
- F06 (ids stop being recognised past S999) — **fixed** for step files, plan
  entries, the `--pre-write` fence, `--roadmap` and every invariant; `S1000` is
  allocated, listed, seen, and `S10000` is refused at the ceiling. Two consumers
  were missed: `step_done` (F01 below) and the DEC/finding id scanners (F12).

Whether the four fixed ones move to `closed` is the triage's call; this run no
longer reports them.

## Findings

### 2026-08-19_adversarial-F01  high  `--step done` matches step ids by substring, so it clears a pause on work that is still open

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. Three comparisons in `step_done` ask whether an id occurs anywhere in a
field's text, while every other reader of those same two fields matches a token:

```
bin/moltke.py:2365   if other_id != step_id and step_id in field_value(other_fields, "blocks"):
bin/moltke.py:2387              if step_id in field_value(parent_fields, "paused_by")]
bin/moltke.py:2411       if step_id in field_value(parent_fields, "paused_by"):
```

Compare `pauser_id`, which exists for exactly this reason — "The field carries a
dated comment, so it is matched rather than compared" (bin/moltke.py:305) — and
`inv_4_done_not_blocked`, which reads `blocks:` with `STEP_ID_RE.findall`.

`--step block` writes the comment itself: `set_field(parent_path, "paused_by",
f"{child_id}  # {datetime.date.today().isoformat()}")` (bin/moltke.py:2276). So a
`paused_by` line that mentions a second id is the tool's own format. Reproduced in
a scratch repo with ordinary three-digit ids — S010 unrelated, S200 paused by
S201, S201 still open:

```
$ grep paused_by adocs/plan_current/S200_parent.md
paused_by:  S201  # 2026-08-19, after S010 lands
$ python3 bin/moltke.py --validate
moltke: all checks pass
$ python3 bin/moltke.py --step done S010 --stamp "unrelated work done"
moltke: S200 unpaused.
moltke: S010 completed and moved to plan_done/. ...
$ grep paused_by adocs/plan_current/S200_parent.md
paused_by:
$ ls adocs/plan_current/
S200_parent.md  S201_blocker.md
$ python3 bin/moltke.py --validate
VIOLATION: INV-1: plan_current/ holds 2 non-paused steps with author 'B' (S200, S201), limit 1 per author; ...
1 violation(s).
```

The same collision now exists on ids alone, because S136 widened them: `S100` is a
substring of `S1000`, so completing S100 clears a pause on S1000, and an unrelated
`blocks: S1000` refuses the completion of S100 with a message quoting a field that
does not say S100:

```
$ python3 bin/moltke.py --step done S100 --stamp "finished"
moltke: S300 still declares blocks: S100; complete or drop S300 first
```

Regression test: `tests/test_2026_08_19_adversarial_findings.py`,
`TestStepDoneMatchesIdsAsTokens` — three tests, all red now, one per direction.

Impact. A completion silently clears a pause that has not resolved, taking a
repository from `--validate` green to an INV-1 violation and printing
`S200 unpaused.` as though it were correct. That is the accounting hole S082 and
S098 closed from two other directions, reopened by the one command that is
supposed to be the safe way to move the plan. It also mis-refuses completions,
which is the loud half. Reachable today, with three-digit ids, whenever a
`paused_by` comment mentions another step — the field the tool itself writes with
a comment — and reachable on ids alone in any repository past S999.

Suggested resolution. Read both fields through the token matcher every other
reader uses: `pauser_id(parent_fields) == step_id` for the two `paused_by` sites,
`step_id in STEP_ID_RE.findall(field_value(other_fields, "blocks"))` for the
`blocks:` site. Not applied here.

### 2026-08-19_adversarial-F02  medium  the hook wiring is unguarded: the suite stays green with the write fence unwired and the Stop hook pointed at `--roadmap`

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `hooks/hooks.json` is what makes any of the enforcement fire, and the
golden reads only the *set* of event names (`declared_hook_events`,
tests/surface.py:32), never which mode an event invokes or which tools a matcher
selects. `test_every_declared_hook_event_has_a_command`
(tests/test_s010_plugin.py:67) asserts each event has some command;
`test_hooks_call_the_checker_through_the_plugin_root` (tests/test_s010_plugin.py:76)
asserts each command contains `${CLAUDE_PLUGIN_ROOT}` and `bin/moltke.py`. Neither
looks at the mode flag or the matcher. Only the `Monitor` matcher is pinned, by
`test_hooks_wire_the_monitor_matcher` (tests/test_s130_precommand.py:195).

Mutation-tested in a copy of the tree at
`$SCRATCH/mut` (`tar` copy, no `.git`), one mutation at a time:

```
# 1. delete the matcher that makes --pre-write fire at all
PreToolUse matchers now: ['Monitor']
Ran 452 tests in 49.333s
OK (skipped=3)

# 2. point the Stop hook at a mode that enforces nothing, and aim PostToolUse at Read
Stop command: python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --roadmap
PostToolUse matcher: Read
Ran 452 tests in 51.207s
OK (skipped=3)
```

Impact. The two things the plugin exists to do — refuse a write into `plan_done/`
or outside the reviewer's fence, and refuse to end a turn on violations — can be
disconnected without a single test failing. `--roadmap` always exits 0 by contract,
so mutation 2 leaves every `Stop` gate silently off in every marked repository,
which is the exact failure mode S060, S067 and S080 each hardened the code
against; here it comes from the wiring instead of the code. This is the S023/F10
lesson ("deleting `Stop` outright left the suite green") fixed one level too
shallow: the event name survived, the connection to the mode did not get guarded.
Every `--pre-write` and `--stop` test invokes the mode directly, so they cannot
see it.

Suggested resolution. Extend `tests/surface.py`'s declaration from event names to
(event, matcher, mode flag) triples and put them in the golden, so any rewiring
fails `test_surface_matches_the_golden` and the documentation check. Not applied
here.

### 2026-08-19_adversarial-F03  medium  `--watch` registers nothing when `.git` is not a directory, and says "no .git found" where git is present

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. The watch subsystem tests `.git` for directory-ness instead of asking
git, in both directions:

```
bin/moltke.py:1764   def _watch_record_path():
bin/moltke.py:1765       git_dir = scaffold_root() / ".git"
bin/moltke.py:1766       if not git_dir.is_dir():
bin/moltke.py:1767           return None
bin/moltke.py:1903       directory = root / ".git" / WATCH_DIR
```

`git_dir(root)` exists for precisely this (bin/moltke.py:1016, S035,
2026-08-07_adversarial-F04: "in a linked worktree and in a submodule it is a
file, and guessing lost the audit baseline ... silently"), and
`_stop_state_path` and `_audit_baseline_path` both use it. The watch subsystem
does not. Reproduced in a linked worktree:

```
$ git worktree add -q ../side -b side
$ file ../side/.git
../side/.git: ASCII text
$ cd ../side && printf 'RUN-DONE\n' > run.log
$ python3 bin/moltke.py --watch run.log 'RUN-DONE' --ceiling 5s --interval 1s
moltke --watch: no .git found, watch state is not registered; the watch itself still terminates on its own
RUN-DONE
$ find ../main/.git -name 'moltke_watch*'      # nothing, in either git dir
```

And with a marked root below the git top level, the monorepo layout S081 added
support for (marker in `packages/app/`, git root two levels up):

```
$ python3 bin/moltke.py --watch run.log 'RUN-DONE' --ceiling 5s --interval 1s
moltke --watch: no .git found, watch state is not registered; ...
$ find . -name moltke_watch        # nothing
```

Contrast, same worktree: `--stop` writes `moltke_stop_state.json` normally,
because that path goes through `git_dir`. There is even a worktree test for the
stop cap (tests/test_s005_hooks.py:413) and none for the watch.

Regression test: `tests/test_2026_08_19_adversarial_findings.py`,
`TestWatchStateInALinkedWorktree` — two tests, both red now; the second
establishes that the same worktree ends a turn clean before arming anything, so
the exit-0 stop it then observes is the missing report and not a clean tree.

Impact. Three documented promises fail in a linked worktree, a submodule, and a
monorepo package: specs' `--watch` row ("Registers under `.git/moltke_watch/` on
arm ... so watch state is derivable from the filesystem (§11)"), MANUAL line 238
("a session that died overnight can find the result the next morning: session
start reports it, and the turn refuses to end until someone acts on it"), and
AGENTS.md §12. A watcher that dies unrecorded, or an outcome nobody acted on, is
reported by nothing; `--step status` writes no Watching block; `--stop` exits 0.
Worktrees are how the project itself documents team work (MANUAL's Teams
section), and the message blames a missing `.git` that is right there, so the
operator has nothing to act on either.

Suggested resolution. Route both functions through `git_dir(root)` — the same
call `_stop_state_path` makes — and pass the marked root into
`_watch_record_path` rather than re-deriving it from the cwd. Keep the "not
registered" warning for the genuinely ungitted case. Not applied here.

### 2026-08-19_adversarial-F04  medium  `--audit check` calls a staged rename into `tests/` an expected new test, and never reports the source it removed

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `worktree_state` keys each porcelain line on its *last* path only:

```
bin/moltke.py:2530       entry = from_git_path(root, porcelain_paths(line)[-1])
```

`porcelain_paths` returns both halves of `R  old -> new` and its own docstring
says why both matter ("the destination is what exists now, the source is a path
that just stopped existing"), but the reconciliation keeps only the destination.
Combined with `_is_new_file` treating `R` as newly here (bin/moltke.py:2583,
deliberately, S077) and `classify` accepting anything new under `tests/`, a
staged rename of tracked source into `tests/` reconciles as expected. Reproduced:

```
$ python3 bin/moltke.py --audit new adversarial
$ git mv src/thing.py tests/moved_thing.py
$ git status --porcelain -uall
R  src/thing.py -> tests/moved_thing.py
?? adocs/audit/2026-08-19_adversarial.md
$ python3 bin/moltke.py --audit check ; echo exit=$?
expected, this run's report and new tests:
  adocs/audit/2026-08-19_adversarial.md: ??
  tests/moved_thing.py: R
exit=0
```

`src/thing.py` is gone from the tree and appears nowhere in the output. Control:
the same removal left unstaged (` D src/thing.py`) is classified unexpected and
exits 1, so only the staged-rename shape hides.

Impact. `--audit check` is what DEC-022 traded the reviewer write fence away for,
and the skill tells the operator to trust it ("a report produced by a run that
also patched the code is not evidence of what was there"). One `git mv` into
`tests/` — a plausible way for an agent to "move a repro into the suite" — removes
tracked source and reports clean. Narrow in shape, but the mechanism's whole job
is to have no such shape.

Suggested resolution. In `worktree_state`, record every path in the line, marking
the source of a rename as departed, and classify a departure the way an
unexpected deletion is classified today. Not applied here.

### 2026-08-19_adversarial-F05  medium  an out-of-range pid ends `--stop`, `--session-start` and `--watch` in a Python traceback

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `_pid_alive` catches `ProcessLookupError` and `OSError`;
`os.kill` raises `OverflowError` for a pid outside C `long`, and nothing catches
that:

```
bin/moltke.py:1706   def _pid_alive(pid):
bin/moltke.py:1708           os.kill(pid, 0)
bin/moltke.py:1709       except ProcessLookupError:
bin/moltke.py:1711       except OSError:  # EPERM and friends
```

`watch_report` guards the type and the sign but not the range
(`isinstance(watcher_pid, int) and watcher_pid > 0`, bin/moltke.py:1929), and
`main`'s backstop catches `OSError` only. Two entry points reproduce it. A watch
record on disk with a large `watcher_pid` — records are filesystem state and
`watch_records` is written to tolerate damage:

```
$ printf '{}' | python3 bin/moltke.py --stop
Traceback (most recent call last):
  ...
  File "bin/moltke.py", line 1451, in mode_stop
    problems.extend(line for line in watch_report(root)
  File "bin/moltke.py", line 1708, in _pid_alive
    os.kill(pid, 0)
OverflowError: Python int too large to convert to C long
stop exit=1
$ python3 bin/moltke.py --session-start        # same traceback, exit 1, no JSON at all
```

And a mistyped `--pid`, which argparse accepts as any int:

```
$ python3 bin/moltke.py --watch run.log 'RUN-DONE' --ceiling 5s --interval 0.2s --pid 99999999999999999999
moltke --watch: registered .../.git/moltke_watch/1787139970_3081027.json
OverflowError: Python int too large to convert to C long
exit=1
$ # the record left behind:
{'outcome': 'stopped', 'exit_code': None, 'pid': 99999999999999999999}
```

Related, same function, no crash: `--pid 0` and negative pids are process-group
targets, so `os.kill` succeeds and the watched process reads as alive forever —
exit 3 can never fire. `--watch ... --pid 0 --ceiling 1s` exits 124, not 3.

Impact. MANUAL line 317 states "Since 0.6.0 no mode ends in a Python traceback",
and the whole S060/S067/S080 line of work exists because a `--stop` that exits 1
"enforces nothing and says nothing". Here every gate for the turn is off, the
`Stop` retry counter never advances, and the user sees a traceback. From
`--session-start` the entire additionalContext payload is lost — the one
combination S068 identified as unrecoverable. For `--watch` the exit code is 1,
which the documented mapping reads as a refusal, while a record was in fact armed
and now blocks stops until someone deletes it, labelled as a manual stop.

Suggested resolution. Catch `OverflowError` alongside `OSError` in `_pid_alive`
and treat an unusable pid as dead; refuse `--pid` values that are not a plausible
process id (`> 0`, within range) at parse time in `mode_watch`, where every other
argument is already validated. Not applied here.

### 2026-08-19_adversarial-F06  low  `MOLTKE_UNBOUNDED_OK` also switches off the single-match-follow refusal that INV-17 says is refused always

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. The escape hatch is consulted before both branches, so it disables both:

```
bin/moltke.py:1218   if not command or "MOLTKE_UNBOUNDED_OK" in command:
bin/moltke.py:1219       return EXIT_OK
bin/moltke.py:1220   _piped, single = _tail_follow_into_grep(command)
bin/moltke.py:1221   if single:
```

```
$ mono 'tail -f run.log | grep -m1 BOOM' false | python3 bin/moltke.py --pre-command
moltke: tail -f piped into a single-match grep cannot end itself: ... Bounded or not, this form under-delivers; ...
exit=2
$ mono 'tail -f run.log | grep -m1 BOOM  # MOLTKE_UNBOUNDED_OK' true | python3 bin/moltke.py --pre-command
exit=0
```

Impact. INV-17 reads "a single-match follow (`tail -f | grep -m N`) is refused
always", with the `MOLTKE_UNBOUNDED_OK` exemption attached to the other branch
only; MANUAL line 253 repeats "refused always: it looks like a fix and hangs by
construction". DEC-051 says "bounded or not". The escape is documented for a
genuinely unbounded stream, which is not what `-m1` expresses, and the persistent
branch's own refusal message teaches the token to any agent it blocks — so the
next arm can carry it into the form that leaks a `tail` forever. Low because it
takes a deliberate token, but the invariant's word is "always" and the code's is
not.

Suggested resolution. Move the `MOLTKE_UNBOUNDED_OK` check below the
single-match branch, so the escape covers the persistent-arm rule only, and say
in the refusal that this form has no escape. Not applied here.

### 2026-08-19_adversarial-F07  low  `--decline` rewrites an already-declined marker, discarding what was in it

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. INV-11: "`--scaffold` and `--decline` ... both leave a declined
repository untouched." `mode_decline` returns early only when the marker exists
and is *not* declined (bin/moltke.py:1667); a declined marker falls through to
the write:

```
$ cat .moltke.json
{ "schema": 1, "enabled": false,
  "note": "declined 2026-01-01 by the team; see docs/why.md",
  "plan_active_max": 2 }
$ python3 bin/moltke.py --decline
moltke: wrote .../.moltke.json with enabled false. ...
$ cat .moltke.json
{ "schema": 1, "enabled": false }
```

`--scaffold` on the same repository prints "left untouched" and changes nothing,
which is the behaviour INV-11 describes for both.

Impact. Small and local: a declined repository loses whatever else its marker
carried — a note saying why, a leftover configuration a later `enabled: true`
would have restored. It is also the second-run behaviour of a mode documented as
idempotent, and the invariant says the opposite of what the code does.

Suggested resolution. Return early when `declined(root)` is already true, with
the same "left untouched" message `--scaffold` prints. Not applied here.

### 2026-08-19_adversarial-F08  low  the shipped audit skill still documents the worklog and `--log-prompt`, removed in 0.11.0

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `--log-prompt` is not a flag; argparse lists the thirteen that exist
and refuses it. The skill that drives every audit still describes it as live:

```
skills/audit/SKILL.md:81   any new files under `tests/`, and an append to `adocs/worklog.md` that matches
skills/audit/SKILL.md:82   what `--log-prompt` writes are expected; anything else exits 1 and is listed.
skills/audit/SKILL.md:83   The worklog is named in the listing either way, because an append there is the
skills/audit/SKILL.md:84   one edit that can turn off the `Stop` recap gate for the surrounding turn.
```

`audit_check` has no worklog handling at all — bin/moltke.py:2586 records the
removal explicitly ("`--audit check` no longer has a prompt log to classify") —
and `tests/test_s008_audit.py:439` asserts the opposite of the skill: a worklog
change is unexpected like any other file. Two more residues: the same file cites
the review model as "AGENTS.md §10", which is Hard prohibitions (review is §9);
and `tests/test_s005_hooks.py:397` defines `_turn_exits`, whose docstring calls it
"the shape of a real session", which calls `run_moltke(root, "--log-prompt", ...)`
and is itself called from nowhere.

Impact. AGENTS.md §7 makes a doc claim a claim about code, traced to the code
path producing it. This one is user-facing: an operator following step 3 expects
a worklog line among the expected changes and is told the recap gate can be
turned off by editing a file that no longer exists. A dead test helper invoking a
removed flag is the same removal's other half.

Suggested resolution. Delete the worklog paragraph from `skills/audit/SKILL.md`
step 3 and fix the section reference to §9; delete `_turn_exits`. Not applied
here.

### 2026-08-19_adversarial-F09  low  a multi-line `--stamp` is truncated at its first blank line by the parser that reads it back

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `with_field` renders continuations at twelve spaces
(bin/moltke.py:2127), including for a blank line, which becomes a whitespace-only
line; `parse_step_file` ends the field on any line whose `strip()` is empty
(bin/moltke.py:143) and then discards the indented lines that follow, because
they match no field:

```
>>> stamp = "first paragraph of the stamp\n\nREADME and MANUAL checked; suite green"
>>> print(repr(with_field(text, "done", stamp)))
'id:         S001\ngoal:       g\ndone:      first paragraph of the stamp\n            \n            README and MANUAL checked; suite green\n'
>>> parse_step_file(path)["done"]
'first paragraph of the stamp'
```

Impact. specs' `--step done` row promises "multi-line accepted, written as
indented continuations", and `field_value_problem` deliberately does not gate
`--stamp` so that a paragraphed stamp is possible. The bytes reach disk and
survive in git, so nothing is lost permanently; what is lost is every *reader* —
INV-5, the `Stop` arrival gate, anything quoting the stamp — which sees only the
first paragraph. That is the S095 defect ("every field was silently truncated to
its first line") narrowed to the one field documented as multi-line.

Suggested resolution. Either write blank continuation lines as twelve spaces and
teach `parse_step_file` that an all-whitespace line inside a field continues it,
or refuse a stamp containing a blank line the way `field_value_problem` refuses a
newline in a one-line field. Not applied here.

### 2026-08-19_adversarial-F10  low  INV-11's "every mode" test covers six of the thirteen modes

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `ALL_MODES` (tests/test_s002_marker.py:16) is a hand-written list of six:
`--session-start`, `--pre-write`, `--post-write`, `--stop`, `--validate`,
`--scaffold`. The parser declares thirteen mutually exclusive modes. Missing:
`--version`, `--pre-command`, `--roadmap`, `--decline`, `--step`, `--audit`,
`--watch`. So `test_every_mode_exits_0_without_marker` and
`test_every_mode_exits_0_when_disabled` would both still pass if the gate stopped
covering `--step`, `--audit`, `--roadmap` or `--pre-command`.

I checked the uncovered modes by hand and the behaviour is correct today — every
one exits 0 in an unmarked directory and under `enabled: false`, `--watch`,
`--version`, `--scaffold` and `--decline` excepted by design. So this is a
coverage defect, not a behaviour defect. Related and smaller: specs' INV-11
names only `--scaffold` and `--decline` as exempt, while the code also exempts
`--version` and `--watch`; MANUAL's version of the same paragraph names `--watch`
and not `--version`.

Impact. The invariant that makes moltke safe to install ("no marker, no
friction") is asserted over less than half of its surface, and the gap is
invisible because the test is named for all of it. A new mode is not covered
unless someone remembers to extend the tuple, which is the failure `surface.py`
was built to remove for the golden.

Suggested resolution. Derive the mode list from `build_parser()` the way
`tests/surface.py` does, with an explicit exempt set (`--version`, `--watch`,
`--scaffold`, `--decline`) that the test names, and make specs' INV-11 wording
list the same four. Not applied here.

### 2026-08-19_adversarial-F11  low  the write fence lets the reviewer overwrite an existing audit report, and blocks it from correcting its own new test

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. `reviewer_may_write` permits anything whose first two components are
`adocs/audit`, and permits a path under `tests/` only while it does not exist
(bin/moltke.py:1037). Driven with the live payload shape:

```
$ agent_type=moltke:adversarial_reviewer file_path=adocs/audit/2026-08-18_adversarial.md   -> exit 0
$ agent_type=moltke:adversarial_reviewer file_path=tests/test_new_thing.py                 -> exit 0
$ agent_type=moltke:adversarial_reviewer file_path=tests/test_s129_watch.py                -> exit 2
$ agent_type=moltke:adversarial_reviewer file_path=adocs/audit/sub/dir/anything.txt        -> exit 0
```

AGENTS.md §2 says of `adocs/audit/`: "add files, never overwrite a report", and
§9 says the report is "never overwritten". `--audit new` honours that with
`next_report_path`; the fence does not, so a `Write` at an older report's path
destroys evidence with no refusal. The second half is the mirror image: once the
reviewer creates `tests/test_x.py`, every further `Write` or `Edit` to it is
refused, so correcting a typo in one's own red test has to happen through `Bash`,
where nothing is fenced or classified. This run did exactly that, disclosed above.

Impact. Both directions push work into the unfenced channel and weaken the
fence's stated role as "a fast clear failure on the common path" (DEC-022): the
one write it should refuse is allowed, and a legitimate write it should allow is
refused. `--audit check` does flag a modified older report as unexpected, so the
overwrite is detected after the fact — but only if someone runs it before acting
on the report.

Suggested resolution. Refuse a reviewer write to an existing file under
`adocs/audit/` other than the report named by the current baseline, and permit
writes to a `tests/` file the same run created — the baseline in
`moltke_audit_baseline.json` already knows both. Not applied here.

### 2026-08-19_adversarial-F12  low  the DEC and finding id scanners are blind past three and two digits, the same width defect S136 just fixed for steps

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. Two scanners still read a fixed width, unanchored on the right in the
way S136's own comment calls "worse than blind":

```
bin/moltke.py:635   FINDING_RE = re.compile(r"^###\s+(\S*-F\d{2})\b", re.M)
bin/moltke.py:644       for dec_id in re.findall(r"^## (DEC-\d{3})\b", text, re.M):
```

`DEC-1000` matches neither `\d{3}\b` nor anything else, so INV-9 abstains on it
silently: a duplicate `DEC-1000` is not reported, and `--audit list` cannot see a
hundredth finding in one report, which also means INV-10 never checks its status
or its reference. Unlike step ids there is no allocator to refuse at a ceiling —
these ids are written by hand — so the failure is a silent skip rather than a
refusal. Latent: this repository is at DEC-057 and no report has more than
fourteen findings.

A third artefact of the same family, harmless but visible: `bin/moltke.py:1013`
is `def git_dir(root):    return lines`, a dead definition shadowed by the real
one three lines later, shipped in b0bcb3d (S120) and unnoticed since. It is what
any linter reports as a redefinition:

```
$ python3 -c "<ast walk over bin/moltke.py>"
redefinition: git_dir at line 1016, first at 1013
```

AGENTS.md §5 requires every commit to be green on "build, lint, full suite", and
there is no lint configuration in the repository, no linter in `test_command`,
and no linter installed — so "lint" is a claim nothing has ever checked. Line
1034, `REVIEWER_AGENT = REVIEWER_AGENT = "adversarial_reviewer"`, is the same
edit's other half.

Impact. Two id scanners will fail the way step ids failed, quietly, at a
threshold nobody will be watching for; and the ruleset's lint requirement is
unenforced today, which is how a shadowed function definition survives eight days
and twenty commits of review.

Suggested resolution. Widen both patterns the way `STEP_ID_DIGITS` was widened,
or make an unreadable id a reported violation rather than a skipped line; delete
the dead `git_dir` and the doubled assignment; either name a linter in the marker
so the gate runs it, or drop "lint" from AGENTS.md §5.

### 2026-08-19_adversarial-F13  low  the prescribed audit output makes the suite red, and the two tests that fail name neither audits nor INV-10

Status: closed  (re-run 2026-08-29_adversarial)

Evidence. Two tests bind `--validate` on this repository into the suite:

```
tests/test_s003_invariants.py:535   TestTheIdFieldAgreesWithTheFilename.test_this_repository_passes
tests/test_s007_step.py             TestMultilineStepFields.test_this_repository_still_validates
```

INV-10 makes every `open` finding without a `closes:` step or a decision a
violation, and the reviewer's own instructions and the shipped report template
both say to write `Status: open` ("only a later re-run can make it `closed`").
So writing this report turned both tests red:

```
$ python3 -m unittest discover -s tests | tail -3
Ran 457 tests in 50.896s
FAILED (failures=7, skipped=3)
$ python3 -m unittest discover -s tests 2>&1 | grep -E "^FAIL:" | tail -2
FAIL: test_this_repository_passes (test_s003_invariants.TestTheIdFieldAgreesWithTheFilename...)
FAIL: test_this_repository_still_validates (test_s007_step.TestMultilineStepFields...)
```

Five of the seven failures are the red regression tests this report ships, by
design. The other two are these, and their message is twelve INV-10 violations —
nothing to do with an `id:` field or with multi-line step fields.

Impact. Two consequences, both small and both real. First, diagnosability: a
session that runs the suite after an audit sees "the id field agrees with the
filename" failing and has to read twelve lines of INV-10 output to learn that the
cause is untriaged findings. Second, sequencing: AGENTS.md §5 requires every
commit to be green, and §9 requires the report to be written before any fix, so
the commit that lands a report can only be green if every finding is planned or
accepted in that same commit. That is what the skill's step 4 prescribes, so the
loop works — but the requirement is implicit, and the `test_command` gate will
refuse `--step done` for anything else in between.

Suggested resolution. Give the two self-host checks their own class named for what
they are, and either scope them to the invariants they mean or state in the
failure message that untriaged findings are an expected transient. Say in the
audit skill that the report and its steps land in one commit. Not applied here.

## Probed and held

Attacked and found sound. An absence here is a tested negative, not an omission.

- **`_is_watch_primitive`.** Tried env prefixes, `cd x &&`, `nohup ... &`,
  comments, a leading `echo`, `bash -c` nesting, `${CLAUDE_PLUGIN_ROOT}`
  expansion, and a primitive with a leaking command substitution in an argument.
  The documented forms pass, the leaks are refused, and the S134 bypass is gone.
  The one hole is F06's, which is the escape token, not the tokenizer.
- **`--pre-write` path normalisation.** `tests/../bin/x`, absolute paths,
  `adocs/plan_todo/../plan_done/x`, symlinks into `plan_done/`, and paths outside
  the repository all behave as documented; `_canonical_case` folds correctly on
  both filesystem kinds.
- **Four-digit step ids end to end.** Allocation at S1000, `plan.md` listing,
  `plan_steps`, `derived_next`, `--roadmap`, the `--pre-write` step fence, and
  the S9999 ceiling refusal all read the wider form. `S\d{3,4}\b` does not
  partially match `S10000`. F01 is the one consumer that was missed.
- **INV-7 immutability.** Uncommitted edit, staged edit with a reverted worktree,
  committed edit, deletion, and rename are each reported with a remedy that
  works; a legitimate `--step done` plus `git add -A` is not.
- **`--step done` atomicity.** An unwritable step file, an unwritable parent, a
  missing `plan_done/`, and a duplicate id in `plan_done/` are all refused before
  anything is written; the destination-then-unlink order holds.
- **Stop deadlock cap.** Fires at three identical problem sets and waives, in a
  clone and in a linked worktree, with the problems printed before the waiver.
  An unwritable state file degrades to a named message, not a wedge.
- **Malformed watch records.** Non-JSON, non-object, missing fields, and absent
  `outcome` all degrade to a report or a skip. Only the out-of-range pid crashes
  (F05).
- **`parse_duration` and the ceiling.** `0`, negatives, `1e3`, `nan`, and blank
  are refused; the interval timer bounds a runaway regex (F02 of 2026-08-18 is
  genuinely fixed) and the degraded no-timer path still exits at the ceiling.
- **`strip_guidance` / `hidden_findings`.** Unbalanced fences, a heading inside a
  comment, and the shipped template's fenced example finding are all classified
  as the code documents.
- **Golden surface teeth.** Refreshing the golden alone does not go green: the
  documentation check requires every flag, operation, skill, hook event and
  marker key to appear in specs and MANUAL. It reads hook *events* only, which is
  F02.
