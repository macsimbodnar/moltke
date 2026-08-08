# Audit 2026-08-08 adversarial

Scope: what was examined, at which commit.
Method: how it was examined. Audits run against the code, not against the specs.
An audit that only confirms the documentation is a documentation review.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-08_adversarial.3-F<nn>`. The example below writes that prefix as
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

Scope of this run: the whole tool at commit `60f6b0f` ("Complete S078"), working
tree clean apart from this report. Method: read `bin/moltke.py` end to end, ran
the suite (`python3 -m unittest discover -s tests`, 351 tests, OK, 117s) and
`python3 bin/moltke.py --validate` (`all checks pass`) as the baseline, then built
throwaway fixture repositories outside the repository and drove the real CLI
against them. Twenty mutations of `bin/moltke.py` were run against the suite in
scratch copies, to test whether the tests name behaviour they would still pass
without: nineteen were killed, and the one survivor is recorded at the end rather
than as a finding. Nothing in this repository was modified.

## Findings

<!-- Append findings here, most severe first. A report with no findings is a
     valid result: say so explicitly rather than leaving this empty. -->

### 2026-08-08_adversarial.3-F01  high  `--stop` blocks forever when its own state file cannot be written: the one unguarded write in `mode_stop` escapes past the counter, so the cap never advances and no problem is printed

Status: open

**Evidence.** `bin/moltke.py:1403` is the only write in `mode_stop` outside a
`try`:

```
1393        if state_path:
1394            try:
1395                state = json.loads(read_file(state_path))
...
1401            except (OSError, json.JSONDecodeError):
1402                pass
1403            state_path.write_text(
1404                json.dumps({"turn": turn, "fingerprint": fingerprint, "count": count}),
1405                encoding="utf-8")
1406        for problem in problems:
1407            print(f"moltke: {problem}", file=sys.stderr)
```

The read is guarded, the write is not. An `OSError` there escapes to `main`'s
backstop at `bin/moltke.py:2408-2416`, which returns `EXIT_BLOCK` for `--stop` —
before the problems are printed at 1406 and before the cap is consulted at 1408.

Fixture: a marked repository with a git history, one uncommitted source change
and no recap, so `--stop` has exactly one problem to report. With `.git`
writable, five runs:

```
$ for i in 1 2 3 4 5; do python3 bin/moltke.py --stop </dev/null >/dev/null 2>&1; echo -n "$? "; done
2 2 2 0 0
```

With `chmod 500 .git`, eight runs:

```
$ chmod 500 .git
$ for i in 1 2 3 4 5 6 7 8; do python3 bin/moltke.py --stop </dev/null >/dev/null 2>&1; echo -n "$? "; done
2 2 2 2 2 2 2 2
```

and the whole of what it says, on every one of them:

```
$ python3 bin/moltke.py --stop </dev/null
moltke: could not read the repository ([Errno 13] Permission denied: '/.../st1/.git/moltke_stop_state.json'). Fix the path named above, then run bin/moltke.py --validate.
EXIT=2
```

The real problem — the unrecapped source change — is never printed. The message
calls a failed *write* a failed read (the defect `.2-F10` named for `--audit`,
here in the backstop), and the remedy it names disagrees with itself:

```
$ chmod 500 .git; python3 bin/moltke.py --validate
moltke: all checks pass
EXIT=0
```

No test covers this: `grep -rn "moltke_stop_state" tests/` returns nothing, and
the four `chmod` fixtures in the suite are on the worklog, the audit directory,
and a parent step file. `TestStopNeverWedges` (tests/test_s005_hooks.py:781)
covers unreadable *reads* only.

**Impact.** Exactly the `2026-08-08_adversarial.2-F01` failure S067 closed,
reached through the write instead of the reads: `Stop` blocks the turn, forever,
with no actionable message, which DEC-006 and INV-12 make the one thing `--stop`
may never do. The session cannot be ended from inside Claude Code; the user has
to kill it or make `.git` writable, and nothing printed says so. Triggers are any
`OSError` on `<git-dir>/moltke_stop_state.json`: a read-only or foreign-owned
`.git` (reproduced above), and a full disk or quota (`ENOSPC`, not reproduced
here — I could not create that condition, but it reaches the same line).
`record_log_failure`, `take_log_failure` and the state `unlink` all guard their
writes; this one line does not.

**Suggested resolution.** Wrap the state write like every other write in the
file, and on failure carry on to the printing and the cap with the failure added
as one more problem — the pattern `porcelain_problems` and the `status.md` block
already use in the same function. A regression test in `TestStopNeverWedges` with
the git directory read-only, asserting `[2, 2, 2, 0, 0]` and that the original
problem is still printed on each. Separately, the backstop at 2414 should not say
"could not read" for a write.

### 2026-08-08_adversarial.3-F02  high  a marked root below the git top level silently switches INV-8 off, makes INV-7 permanently false, and makes `--audit check` blame its own report

Status: open

**Evidence.** Every git call is `git -C <marked root>`, but `git status
--porcelain` and `git log --name-status` print paths relative to the *repository*
top level, and `git show <sha>:<path>` resolves the path from the top level too.
Nothing checks that the marked root and the git top level are the same directory.
`find_root` (`bin/moltke.py:33-39`) walks up from the cwd looking for `.moltke.json`
and stops there, whatever git thinks.

Fixture: a git repository with a marked project inside it, everything committed
and otherwise identical to the fixture that gives `all checks pass` at the root.

```
$ mkdir -p mono/packages/foo && cd mono && git init -q .
   # workflow_repo() fixture written into packages/foo, then committed
$ cd packages/foo && python3 bin/moltke.py --validate
VIOLATION: INV-7: packages/foo/adocs/plan_done/S001_base.md landed in plan_done/ at commit d2de7dde and is gone; completed history is never removed. Restore it in a new commit: git show d2de7dde:packages/foo/adocs/plan_done/S001_base.md > packages/foo/adocs/plan_done/S001_base.md
1 violation(s). Fix the items above, then rerun bin/moltke.py --validate.
EXIT=1
```

The file is present. `landed` (`bin/moltke.py:400-404`) holds
`packages/foo/adocs/plan_done/S001_base.md`, and `root / entry`
(`bin/moltke.py:410`) is then `packages/foo/packages/foo/...`, which is not a
file. The printed remedy is a path relative to the top level, so running it from
the marked root writes to a directory that does not exist: the violation has no
way to green.

INV-8 goes the other way and says nothing at all. Removing a committed line from
`decisions.md` — the tampering INV-8 exists for — in the same two repositories:

```
   # marked root below the git top level
$ python3 bin/moltke.py --validate
VIOLATION: INV-7: packages/foo/adocs/plan_done/S001_base.md landed ... and is gone; ...
1 violation(s).

   # identical tamper, marked root == git top level
$ python3 bin/moltke.py --validate | grep INV-8
VIOLATION: INV-8: adocs/decisions.md no longer contains, in order, the lines it had at commit ebbd9a5e; ...
VIOLATION: INV-8: adocs/decisions.md no longer starts with what HEAD holds, so something above the end changed; ...
```

Both halves of INV-8 abstain: `git show HEAD:adocs/decisions.md`
(`bin/moltke.py:489`) exits non-zero because the path is not at the top level, and
`git_blobs` asks for `<sha>:adocs/decisions.md`, which `cat-file` reports as
missing, so `required` stays `None` (`bin/moltke.py:472-480`).

`--audit check` reports the report it just created as contamination, because
`saved["report"]` is `relative_to(root)` while `worktree_state` keys are top-level
relative:

```
$ python3 bin/moltke.py --audit new adversarial >/dev/null; python3 bin/moltke.py --audit check
unexpected, not attributable to writing the report:
  packages/foo/adocs/audit/2026-08-08_adversarial.md: ??
The reviewer holds Bash and is not fenced from mutating the repository (DEC-022). ...
AUDIT-CHECK EXIT=1
```

And both `Stop` gates misjudge the same paths, by the same rule: `RECAP_EXEMPT`
is matched with `startswith` (`bin/moltke.py:1265`, `1315-1317`), so
`packages/foo/adocs/worklog.md` is "source" and every turn demands a recap —

```
$ python3 bin/moltke.py --stop </dev/null
moltke: INV-7: packages/foo/adocs/plan_done/S001_base.md landed in plan_done/ ... and is gone; ...
moltke: source changed but adocs/worklog.md has no recap heading after the last logged prompt; ...
```

— while the stamp gate tests `entry.startswith(f"{DOCS}/plan_done/")`
(`bin/moltke.py:1331`), which no path there can satisfy, so a completed step
arriving in `plan_done/` is never asked for its README and MANUAL stamp. I read
that last one off the code rather than reproducing it, because the tree already
blocks for the two reasons above.

**Impact.** Any repository where `.moltke.json` is not at the git top level. That
is not the `--scaffold` path — `scaffold_root` places the marker at the top level
— but it is reachable without doing anything unusual: a marked project vendored
into a monorepo or added as a subtree; a project directory that was never
`git init`ed sitting under an ancestor that is a git repository (a `$HOME` under
version control is enough); a marker written by hand in a subproject. The result
is the worst combination the prime directive can produce: an invariant that is
silently off (INV-8, the one guarding the decision log that everything cites by
id), an invariant that is permanently and falsely on with an unrunnable remedy
(INV-7), a `Stop` that blocks every turn until the waiver, and the audit
reconciliation that DEC-022 traded the write fence away for reporting its own
output as unexplained. Documentation states the no-git case ("the check
abstains") and says nothing about this one.

**Suggested resolution.** Decide the relationship once, at startup: compare
`find_root()` against `git rev-parse --show-toplevel`. Either refuse loudly with
a message naming both paths (consistent with "each refuses rather than repairs"),
or carry the prefix and translate in the three places that consume git paths
(`porcelain_paths` consumers, `history_blocks`/`git_blobs` specs, and the
`relative_to(root)` in `audit_new`). Whichever is chosen, a fixture repository
with the marker one directory below the top level belongs in the suite: today no
test has a marked root that is not also the git root.

### 2026-08-08_adversarial.3-F03  medium  `--step block` on a parent that is already paused takes a green repository to an INV-1 violation and silently overwrites the pause

Status: open

**Evidence.** `step_block` (`bin/moltke.py:1664-1685`) requires only that the
parent is in `plan_current/` (`1666`). It never asks whether the parent is
already paused, and `set_field(parent_path, "paused_by", ...)` at `1681`
overwrites whatever was there.

```
$ python3 bin/moltke.py --validate
moltke: all checks pass
$ python3 bin/moltke.py --step block S003 first_child
moltke: S004 created in plan_current/ blocking S003, which is now paused.
$ python3 bin/moltke.py --validate
moltke: all checks pass
$ python3 bin/moltke.py --step block S003 second_child
moltke: S005 created in plan_current/ blocking S003, which is now paused.
EXIT=0
$ python3 bin/moltke.py --validate
VIOLATION: INV-1: plan_current/ holds 2 non-paused steps (S004, S005), limit 1; pause or complete until 1 remain
1 violation(s). Fix the items above, then rerun bin/moltke.py --validate.
EXIT=1
$ grep -H paused_by adocs/plan_current/*.md
adocs/plan_current/S003_active.md:paused_by: S005  # 2026-08-08
adocs/plan_current/S004_first_child.md:paused_by:
adocs/plan_current/S005_second_child.md:paused_by:
```

S004's pause of S003 is gone from the file; only S004's own `blocks: S003` still
records it. `tests/test_s007_step.py:110-139` has three `TestBlock` cases and
none of them blocks the same parent twice: `test_refuses_when_parent_is_not_active`
uses a parent in `plan_todo/`, and `test_refuses_past_the_stack_limit` chains
S003 → S004 → S005, which is the legal shape.

**Impact.** `adocs/specs.md:641` states of `--step`: "no transition may leave
INV-1..INV-7 violated", and the `step` skill's acceptance in the same file is
"every transition leaves invariants 1 to 7 satisfied". This transition leaves
INV-1 violated on the happy path, with exit 0 and a success message, from a
repository that was green. The trigger is an ordinary slip: with a paused stack,
naming the original parent instead of the active child. Afterwards every `--stop`
blocks until the waiver, `--post-write` reports on every edit, and `--step start`
refuses; the pause record that was overwritten cannot be restored by any CLI
operation.

**Suggested resolution.** Refuse when the named parent already carries a
`paused_by`, naming the child that holds the pause and suggesting `--step block
<that child> <name>` — the stack discipline AGENTS.md §4 describes. Red-first
test: block twice on the same parent, assert exit 1, assert `--validate` still
exit 0, and assert the first child's pause is intact.

### 2026-08-08_adversarial.3-F04  medium  `--step new` and `--step block` write the step file before the plan entry, so a refusal leaves an unlisted step and an INV-3 violation

Status: open

**Evidence.** `step_new` writes the file at `bin/moltke.py:1635` and lists it at
`1636`; `step_block` writes the child at `1679`, lists it at `1680`, and pauses the
parent at `1681`. `append_to_plan` (`1598-1605`) writes `plan.md`, which is the
one of the three that can fail. `mode_step` turns that into a refusal
(`bin/moltke.py:2255-2262`) after the file is already on disk.

```
$ python3 bin/moltke.py --validate
moltke: all checks pass
$ chmod 444 adocs/plan.md
$ python3 bin/moltke.py --step new orphan
moltke: --step new could not touch the plan tree ([Errno 13] Permission denied: '.../adocs/plan.md'). The workflow directories under adocs/ are what --step moves files between; restore the missing one, or run bin/moltke.py --scaffold, which creates what is absent and overwrites nothing
EXIT=1
$ chmod 644 adocs/plan.md; python3 bin/moltke.py --validate
VIOLATION: INV-3: adocs/plan_todo/S004_orphan.md is not listed in plan.md; add S004 to the ordered list, ...
1 violation(s).
```

`--step block` is worse, because the child lands in `plan_current/` and the parent
is never paused:

```
$ chmod 444 adocs/plan.md
$ python3 bin/moltke.py --step block S003 childx
moltke: --step block could not touch the plan tree ([Errno 13] Permission denied: '.../adocs/plan.md'). ...
EXIT=1
$ chmod 644 adocs/plan.md; python3 bin/moltke.py --validate
VIOLATION: INV-1: plan_current/ holds 2 non-paused steps (S003, S004), limit 1; pause or complete until 1 remain
VIOLATION: INV-3: adocs/plan_current/S004_childx.md is not listed in plan.md; add S004 to the ordered list, ...
2 violation(s).
```

The refusal text is also wrong about the cause: it says a workflow directory is
missing and offers `--scaffold`, which creates nothing here and clears nothing.

**Impact.** The same defect as `2026-08-08_adversarial-F03`, which S062 fixed for
`--step done` only: a transition that refuses and half-applies, taking the
repository from `all checks pass` to a violation while reporting that it declined.
`tests/test_s007_step.py:497` (`TestARefusedCompletionChangesNothing`) asserts the
property for `done` and nothing asserts it for `new` or `block`. Recovery needs a
hand edit — deleting the orphan file, or adding the id to `plan.md` — which is
what `--step` exists to avoid, and the id is burned either way since
`next_step_id` reads `plan.md` as well as the directories.

**Suggested resolution.** The S062 ordering, applied here: make the fallible
write first, or pre-flight `plan.md` for writability (`os.access`, as `step_done`
now does for the step file and the parent) and refuse before `write_step`. On a
failure after the file exists, unlink it and say nothing was changed. Tests
mirroring `TestARefusedCompletionChangesNothing` for both operations.

### 2026-08-08_adversarial.3-F05  medium  INV-7's remedy for a rename inside `plan_done/` is a no-op, and following both printed remedies leaves the tree worse than it started

Status: open

**Evidence.** S071 removed the shell redirection from this message
(`.2-F05`). What is printed now is safe but does not clear the violation:

```
$ git mv adocs/plan_done/S001_base.md adocs/plan_done/S001_renamed.md
$ python3 bin/moltke.py --validate
VIOLATION: INV-7: adocs/plan_done/S001_renamed.md changed under plan_done/ (renamed from adocs/plan_done/S001_base.md); history is immutable: restore it with git checkout -- adocs/plan_done/S001_renamed.md
VIOLATION: INV-7: adocs/plan_done/S001_base.md landed in plan_done/ at commit ebbd9a5e and is gone; completed history is never removed. Restore it in a new commit: git show ebbd9a5e:adocs/plan_done/S001_base.md > adocs/plan_done/S001_base.md

$ git checkout -- adocs/plan_done/S001_renamed.md     # exactly what it said
$ python3 bin/moltke.py --validate | head -2
VIOLATION: INV-7: adocs/plan_done/S001_renamed.md changed under plan_done/ (renamed from adocs/plan_done/S001_base.md); ...
VIOLATION: INV-7: adocs/plan_done/S001_base.md landed in plan_done/ at commit ebbd9a5e and is gone; ...
$ git status --short
R  adocs/plan_done/S001_base.md -> adocs/plan_done/S001_renamed.md
```

`git checkout -- <new path>` restores the new path from the index, which already
holds the rename: nothing changes. Following the second message as well makes it
worse:

```
$ git show ebbd9a5e:adocs/plan_done/S001_base.md > adocs/plan_done/S001_base.md
$ python3 bin/moltke.py --validate
VIOLATION: INV-6: duplicate step id S001 in plan_done and plan_done; ids are allocated once, rename one file
VIOLATION: INV-7: adocs/plan_done/S001_renamed.md changed under plan_done/ (renamed from adocs/plan_done/S001_base.md); history is immutable: restore it with git checkout -- adocs/plan_done/S001_renamed.md
2 violation(s).
```

Two violations, one of them new, and the same unrunnable remedy still printed.
The command that actually clears it — `git mv adocs/plan_done/S001_renamed.md
adocs/plan_done/S001_base.md` — is never named.
`tests/test_s003_invariants.py TestInv7NamesTheRenamedFile` asserts the message
names one file and does not redirect over it; nothing asserts that following it
reaches green.

**Impact.** INV-12: "every blocking exit carries a message stating exactly what
to do to unblock". `--validate` exits 1 and `--stop` blocks on this state, and the
instruction printed does not move it — the terminal-state problem S034 fixed for
the committed case, reappearing for a rename. A user who follows both messages in
order ends up with a duplicate step id.

**Suggested resolution.** When `porcelain_paths` yields two paths, print the
inverse of the rename (`git mv <new> <old>`) as the remedy, and suppress the
second "landed and is gone" violation for the same step while the rename is
staged, since it is one event and one fix. Test: perform the rename, run the
printed command verbatim, assert `--validate` exits 0.

### 2026-08-08_adversarial.3-F06  medium  `testing.md` is the one scanner input still read raw, so a fenced example row satisfies INV-5 and the `--step done` gate

Status: open

**Evidence.** `inv_5_done_evidence` reads the ledger with `read_file`
(`bin/moltke.py:292`) and `step_done` does the same at `bin/moltke.py:1754`;
every other scanner goes through `read_stripped`. A row inside a code fence —
guidance by the rule `adocs/specs.md` states as universal — therefore counts as
evidence:

```
$ tail -6 adocs/testing.md
How to write a row, for reference:

```
| S003 | example criterion | tests/test_example.py | pass |
```

$ grep -n S003 adocs/testing.md
10:| S003 | example criterion | tests/test_example.py | pass |     # the only one

$ python3 bin/moltke.py --step done S003 --stamp "README and MANUAL checked"
moltke: no "test_command" in .moltke.json, so nothing here ran the suite. ...
moltke: S003 completed and moved to plan_done/. Commit it; the move is the last action of the step.
EXIT=0
$ python3 bin/moltke.py --validate
moltke: all checks pass
```

**Impact.** `adocs/specs.md` (2026-08-01, S008): "**template guidance is never
data.** Every scanner reads its input through `strip_guidance`", strengthened by
S019 to "That makes the sentence below true rather than aspirational; it is the
fifth time this defect appeared." It is not true of the acceptance ledger, which
is the file INV-5 exists to read. A repository whose `testing.md` documents its
own row format — a normal thing to do, and the shipped template's header explains
the format in prose one line above the empty table — can complete steps against
example rows, and `--validate` will agree. The shipped template happens not to
carry a fenced example, so this does not fire out of the box; it fires as soon as
someone adds one.

**Suggested resolution.** Read `testing.md` through `read_stripped` in both
places, and add `testing.md` to `STRIPPED_FILES` so INV-13's parity guards it too
— the S063 rule that the scan list is derived from the readers. Test: a fenced row
does not discharge INV-5 and `--step done` refuses; the same row unfenced does.

### 2026-08-08_adversarial.3-F07  low  `--roadmap` exits 2 on an unreadable path, where the specs table and both exit-code tables say it exits 0

Status: open

**Evidence.** `adocs/specs.md:637` for `--roadmap`: "Exit 0 always".
`README.md:76` assigns exit `2` to `mode_pre_write`, `mode_stop`,
`mode_post_write`; `MANUAL.md` says `2` is "a blocked action, with what to do
about it". `mode_roadmap` is dispatched inside the `try` at `bin/moltke.py:2389`
and the backstop at `2416` returns `EXIT_BLOCK` for every mode except
`--log-prompt` and `--session-start`:

```
$ chmod 000 adocs/plan.md
$ python3 bin/moltke.py --roadmap
moltke: could not read the repository ([Errno 13] Permission denied: '.../adocs/plan.md'). Fix the path named above, then run bin/moltke.py --validate.
EXIT=2
```

The same tree gives `--validate` exit 1 with two named violations, so the
information exists; only this mode's exit code is undocumented.

**Impact.** Small but real, because AGENTS.md §9 and `templates/AGENTS.md` tell
every agent to end a completed unit of work by running `bin/moltke.py --roadmap`.
A wrapper that treats 2 as "blocked" gets a block from a mode documented as
never blocking. This is `.2-F10` (`--audit` exiting 2 through the backstop) with
`--roadmap` in place of `--audit`: S076 fixed the one mode the finding named.

**Suggested resolution.** Either give `--roadmap` its own refusal, or add it to
the exit-0 list at `bin/moltke.py:2416` and keep the specs claim, or narrow the
specs and both tables to say what it does. The surface test already requires the
mode to appear in the specs table, so whichever way it goes the two must be
edited together.

### 2026-08-08_adversarial.3-F08  low  a hook payload whose nested types differ from the expected ones still ends in a traceback, and in `--pre-write` that fails the reviewer fence open

Status: open

**Evidence.** MANUAL.md: "Since 0.6.0 no mode ends in a Python traceback."
`hook_input` (`bin/moltke.py:791-799`) validates only that the top level is a
dict; the three consumers assume the nested types.

```
$ echo '{"tool_input": "adocs/plan_done/S001_base.md"}' | python3 bin/moltke.py --pre-write
  File "bin/moltke.py", line 1077, in mode_pre_write
    path = path_arg or payload.get("tool_input", {}).get("file_path", "")
AttributeError: 'str' object has no attribute 'get'

$ echo '{"agent_type": ["moltke:adversarial_reviewer"], "tool_input": {"file_path": "bin/moltke.py"}}' | python3 bin/moltke.py --pre-write
  File "bin/moltke.py", line 1099, in mode_pre_write
    agent = (payload.get("agent_type") or "").split(":")[-1]
AttributeError: 'list' object has no attribute 'split'

$ echo '{"prompt": 12345}' | python3 bin/moltke.py --log-prompt
  File "bin/moltke.py", line 1048, in mode_log_prompt
    quoted = "\n".join(f"> {line}" for line in prompt.splitlines())
AttributeError: 'int' object has no attribute 'splitlines'
```

**Impact.** A `PreToolUse` hook that dies with exit 1 is non-blocking, so the
write it was judging proceeds: the reviewer fence and the `plan_done/` refusal
both fail open, silently, in the direction S016 called out as the wrong one. For
`--log-prompt` the prompt is lost rather than logged, which is the F14 class.
What I could not confirm: that Claude Code ever sends these shapes. I observed
the tracebacks by feeding the payloads directly, not from a live session, and
the documented payload has `tool_input` as an object. This is a robustness and
documentation-accuracy finding, not a reproduced live failure.

**Suggested resolution.** Coerce in `hook_input`, or type-check at each of the
three reads and treat a wrong type as absent (which is already the fail-open
default for a missing key). A test feeding each mode a payload with wrong nested
types and asserting no `Traceback` in stderr — the shape
`test_a_payload_that_cannot_be_parsed_behaves_like_an_empty_one`
(tests/test_s005_hooks.py:757) already has for the top level.

## Verdicts on prior findings

Re-measured from each finding's own reproduction, in fixture repositories built
for this run. The twelve findings of `2026-08-08_adversarial.2.md` all still read
`Status: open` in that file although S067..S078 landed; by AGENTS.md §10 they
should read `planned` until a re-run clears them, and this run is that re-run.

- **`2026-08-08_adversarial.2-F01`** (`--stop` blocks forever on an unreadable
  path) — **no longer reproduces as measured.** A broken symlink named like a step
  file in `plan_todo/` gives `2 2 2 0 0` over five stops. A different route to the
  same wedge is F01 above, so the property is not yet whole.
- **`2026-08-08_adversarial.2-F02`** (`--session-start` prints no JSON) — **no
  longer reproduces.** A directory where a step file belongs gives the full
  envelope on stdout with the read failure inside `additionalContext`, exit 0.
- **`2026-08-08_adversarial.2-F03`** (the stamp gate judges any path under
  `plan_done/`) — **no longer reproduces.** `touch adocs/plan_done/.gitkeep` in a
  repository with history leaves `--stop` at exit 0.
- **`2026-08-08_adversarial.2-F04`** (`--step done` leaves state the CLI cannot
  clear) — **not re-measured directly.** The pre-flight at `bin/moltke.py:1783-1787`
  and the stale-pause branch at `1736-1744` are present, and mutating the
  pre-flight away kills `TestNoDeadEndCompletion`; I did not rebuild the race.
- **`2026-08-08_adversarial.2-F05`** (INV-7's rename remedy truncates the file) —
  **the reported form no longer reproduces**: the message names one file and no
  arrow, `git checkout -- adocs/plan_done/S001_renamed.md`. It is still not a
  remedy that works, which is F05 above.
- **`2026-08-08_adversarial.2-F06`** (the structural guard cannot fire) — **not
  re-measured directly.** `tests/test_s033_fences.py` names the three lines allowed
  to call `strip_guidance` and a second test records `read_stripped` targets;
  reverting `hides_content` to a constant kills three tests across two files, so
  the guard is live in at least that direction.
- **`2026-08-08_adversarial.2-F07`** (dropping `-uall` from `--stop` leaves the
  suite green) — **no longer reproduces.** With `-uall` removed from
  `bin/moltke.py:1381`, the suite fails:
  `FAIL: test_a_step_inside_a_wholly_untracked_plan_done_still_reaches_the_gate`.
- **`2026-08-08_adversarial.2-F08`** (`tests/test_s033_fences.py` runs nine tests
  short) — **no longer reproduces.** Run directly it reports `Ran 42 tests`, and
  the fourteen files run directly sum to 351, the same as `discover`.
- **`2026-08-08_adversarial.2-F09`** (INV-14 blames a fence for a commented
  heading) — **no longer reproduces.** A finding heading inside an HTML comment,
  in a report with no fence markers, gives `--validate` exit 0.
- **`2026-08-08_adversarial.2-F10`** (`--audit` exits 2 through the backstop, and
  a write is called a read) — **no longer reproduces for `--audit`**: with
  `adocs/` at mode 500, `--audit new adversarial` gives exit 1 on stderr and says
  "could not write to adocs/audit". The same defect survives in the `main`
  backstop for `--roadmap` (F07) and in the `--stop` path (F01).
- **`2026-08-08_adversarial.2-F11`** (`AM` reported as contamination) — **no
  longer reproduces.** A new test staged and then edited lists under "expected,
  this run's report and new tests: tests/test_new_regression.py: AM", exit 0.
- **`2026-08-08_adversarial.2-F12`** (INV-16 tests both sides for emptiness) —
  **no longer reproduces.** A directive stated in prose and repeated inside a fence
  in the same section gives `VIOLATION: INV-16 ...`, exit 1.

Not re-measured, and unchanged in status: `2026-08-07_adversarial.2-F06` (no Stop
cap without git, `accepted` under DEC-031) and `2026-08-06_adversarial-F02` (the
reviewer fence, `planned`), which turns on the version in the plugin cache rather
than on anything in this repository.

## What was checked and found sound

Recorded so the absence of a finding is not read as an absence of looking.

- Twenty mutations of `bin/moltke.py` were run against the full suite in scratch
  copies. Nineteen were killed, most by a test that names the behaviour directly:
  `_arrives_here` narrowed to `A`, `hides_content` made blind, `hidden_findings`
  reading comments, the `--step done` pre-flight, INV-13 counting raw markers, the
  stamp gate's `STEP_FILE_RE` filter, the `Stop` turn key's breadcrumb, the
  rename split in `porcelain_paths`, the roadmap's all-done bucket rule, strict
  decoding, `_git_run`'s missing-binary tolerance, the reviewer's new-file rule,
  INV-10's exact stem match, INV-16, `-uall`, `RECAP_EXEMPT` as a bare prefix,
  `--pre-write`'s path resolution, the audit type pattern, and the foreign
  worklog-line check.
- The one survivor: dropping `and entry not in landed` at `bin/moltke.py:403`,
  which decides whether INV-7 compares a `plan_done/` file against the first or
  the last commit that added it. No test names that choice. It only differs for a
  file added, deleted and re-added under `plan_done/`, which is itself a violation,
  so it is recorded here rather than as a finding.
- The fresh-adoption path is clean: `--scaffold` into an empty git repository,
  then `--validate` (`all checks pass`), `--session-start` (planning nudge naming
  both unfilled files), `--stop` (exit 0, abstaining before the first commit),
  then a full `--step new` / `--step start` / `--step done` cycle with the
  testing-row refusal firing first — all as documented.
- `--audit new` twice on one day produces `.md` then `.2.md` and never overwrites;
  finding ids are scoped to the report stem in both directions.
- INV-11 holds for `--roadmap` in an unmarked directory (exit 0, no output), and
  for every mode in a declined one.
