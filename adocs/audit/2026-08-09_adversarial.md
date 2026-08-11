# Audit 2026-08-09 adversarial

Scope: the whole repository at commit `beea5f9` ("Bump 0.7.0"), no boundary.
Method: read `bin/moltke.py` end to end (2749 lines), then reproduced against
throwaway fixture repositories built from `tests/fixtures.py` outside the
repository. Ten mutants were planted in a copy of the tree and the full suite
run against each. Every prior finding still marked `planned` was re-measured
from its own reproduction rather than from a step stamp. Audits run against the
code, not against the specs. An audit that only confirms the documentation is a
documentation review.

Baseline state, measured first: `python3 -m unittest discover -s tests` → `Ran
410 tests in 140.727s / OK`; `python3 bin/moltke.py --validate` → `moltke: all
checks pass`, exit 0; `python3 bin/moltke.py --audit check` → exit 0, this
report the only footprint.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name, so the ids in
this file read `2026-08-09_adversarial-F<nn>`. The example below writes that prefix as
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

Seven findings: one high, two medium, four low. By DEC-035 this run does not
stop the audit loop.

No test was added under `tests/`. Every finding below reproduces in five lines
of shell against a fixture repository, so none of them needs a test to be
demonstrable, and a red test committed here would block `--step done` — whose
`test_command` gate runs the whole suite — for the triage session that has to
plan these. The red-first test belongs to each fixing step.

## Findings

### 2026-08-09_adversarial-F01  high  `--step new` allocates a four-digit id past S999, and every scanner in the tool is blind to it

Status: closed

Closed 2026-08-11 by S097, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

`next_step_id` (`bin/moltke.py:1778`) has no upper bound and reads three-digit
ids out of `plan.md` prose as well as out of step files:

    highest = 0
    ...
    for number in re.findall(r"\bS(\d{3})\b", plan_text(root) or ""):
        highest = max(highest, int(number))
    return f"S{highest + 1:03d}"

`STEP_FILE_RE` (`bin/moltke.py:82`) is `^(S\d{3})_[A-Za-z0-9_]+\.md$` and
`PLAN_ENTRY_RE` (`bin/moltke.py:923`) is `^\s*(?:\d+\.|[-*])\s+(S\d{3})\b`.
Both require exactly three digits — `S1000_x.md` fails the first because the
character after `S100` is not `_`, and `5. S1000` fails the second because
`\b` does not match between `0` and `0`. So the id the allocator produces at
1000 is one nothing in the file can read.

A fixture repository that passes every check, whose `plan.md` mentions `S999`
in the description paragraph — which the shipped `templates/adocs/plan.md`
explicitly invites: "An id named in a sentence anywhere else in this file is
prose: it does not change the order, and it is not checked":

    $ python3 bin/moltke.py --step new later_work
    moltke: created adocs/plan_todo/S1000_later_work.md and listed S1000 in plan.md.
    Reorder plan.md if it does not belong last.
    exit=0

    $ ls adocs/plan_todo
    S002_pending.md
    S1000_later_work.md

    $ tail -1 adocs/plan.md
    4. S1000  later work

    $ python3 bin/moltke.py --validate
    moltke: all checks pass
    exit=0

    $ python3 bin/moltke.py --step start S1000
    moltke: S1000 does not exist; create it with --step new <name>
    exit=1

    $ python3 bin/moltke.py --roadmap
    S001 ▏█░▶▕ S003
         └ 1 done ┘ └ 2 left

         now  S003  active

The step is on disk, listed in `plan.md`, and invisible to `plan_steps`,
`plan_order`, `derived_next`, `--roadmap`, `--session-start`, `--step status`
and all sixteen invariants at once. INV-3 cannot report it in either direction:
the file is not a step file, and the plan entry is not a list entry. `--step
start` says it does not exist and names `--step new` as the remedy, which
allocates `S1001` and repeats the failure. `pauser_id` (`bin/moltke.py:267`)
and `inv_4_done_not_blocked` (`bin/moltke.py:341`) would read `S1000` as
`S100`, so a `paused_by: S1000` names a different step.

Two independent triggers, both real:

- Any `\bS\d{3}\b` token of `S999` anywhere in `plan.md`, prose included. That
  is the case reproduced above; it needs no 999 steps and no malformed input.
- The id space genuinely reaching 999. This repository allocated S001..S096 in
  nine days, so the ceiling is dated rather than hypothetical, and nothing —
  not `--step new`, not `--validate` — says a word when it is crossed.

Impact. `--step new` reports success while creating repository state that no
derivation can see, with `--validate` green. That is the prime directive
("project state is always derivable from tracked files alone") failing in the
one command whose job is to keep `plan.md` and the plan directories in step.
There is no CLI path back: the file has to be renamed and `plan.md` edited by
hand, the two things `--step` exists to avoid. The consequence is identical to
2026-08-08_adversarial.4-F01, which was rated high and fixed as S088 by
validating the *name*; the *id* half of the same filename was left unchecked.

Suggested resolution. Refuse in `mode_step` before anything touches the
filesystem when `next_step_id` would exceed `S999`, naming the ceiling and the
`plan.md` token that caused it, exactly as `step_name_problem` refuses a name.
Deciding whether the id space should widen to four digits is a separate
question and a `decisions.md` entry: widening it means `STEP_FILE_RE`,
`PLAN_ENTRY_RE`, `pauser_id`, `inv_4_done_not_blocked` and `next_step_id` all
change together, and every existing three-digit id keeps working. Either way,
allocating an id no scanner can read must not be a silent success.

### 2026-08-09_adversarial-F02  medium  a step paused by itself, or two steps paused by each other, passes every check and no command can clear it

Status: closed

Closed 2026-08-11 by S098, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

S090 (2026-08-08_adversarial.4-F03) made a `paused_by` naming a step in no plan
directory an INV-1 violation and added `--step unpause` to clear it. That
command is deliberately narrow (`bin/moltke.py:1904`): it refuses when the
named step exists, because DEC-040 rejected a general unpause. Nothing checks
that the named step is not the step itself, or that pauses do not form a cycle.

Fixture repository, `S003` in `plan_current/`, with `paused_by: S003` added to
its own step file — the field AGENTS.md §4 tells the agent to set by hand on
the parent:

    $ python3 bin/moltke.py --validate
    moltke: all checks pass
    exit=0

    $ python3 bin/moltke.py --step done S003 --stamp "x README MANUAL"
    moltke: S003 is paused by S003; complete S003 first, which unpauses this step
    automatically
    exit=1

    $ python3 bin/moltke.py --step unpause S003
    moltke: S003 is paused by S003, which exists. Complete S003 with --step done S003,
    which unpauses S003 on its way out; this command only clears a pause naming a step
    that is in no plan directory
    exit=1

The two commands name each other. `--step done` sends you to `--step done` on
the same id; `--step unpause` sends you to the `--step done` that just refused.

The two-step cycle is the same defect and needs no self-reference: `S003` with
`paused_by: S004` and `S004` with `paused_by: S003`, both in `plan_current/`:

    $ python3 bin/moltke.py --validate
    moltke: all checks pass
    exit=0

    $ python3 bin/moltke.py --step done S003 --stamp "x README MANUAL"
    moltke: S003 is paused by S004; complete S004 first, which unpauses this step
    automatically
    exit=1

    $ python3 bin/moltke.py --step unpause S003
    moltke: S003 is paused by S004, which exists. Complete S004 with --step done S004,
    ...
    exit=1

`--step done S004` refuses symmetrically. Both steps are paused, so
`inv_1_active_max` counts zero active steps and reports nothing; INV-2 sees a
stack of two under a limit of three.

Impact. Two steps, or one, permanently stuck in `plan_current/` with every
check green and no CLI operation that reaches them — the exact state S090 was
written to remove, entered through the one door it left open. `--roadmap` draws
`now S003 active [paused by S003]` and `--session-start` announces the same, so
a resumed session is told to work on a step that cannot be completed. Because
neither step is active, `--step start` on unrelated work still succeeds, so the
stuck pair silently accumulates alongside real work. Reachability is a hand
edit, which is exactly how F03 was reachable: AGENTS.md §4 instructs the agent
to "set `paused_by: <child_id>` with a date on the parent", and the file being
edited *is* the parent, so naming it instead of the child is a one-token slip.

Suggested resolution. Extend INV-1's pauser rule (`bin/moltke.py:285`) from
"the pauser has a step file" to "the pause resolves": a step may not pause
itself, and following `paused_by` from any step in `plan_current/` must reach a
step that is not paused. Report the cycle by naming its members, and let
`--step unpause` clear a pause it reports — that keeps DEC-040's rule (a pause
naming reachable, live work is never cleared) while removing the dead end.

### 2026-08-09_adversarial-F03  medium  a field value containing a newline is written unescaped: it corrupts `plan.md`, and a two-line `done:` stamp wedges the Stop gate

Status: closed

Closed 2026-08-11 by S099, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

S095 gave `parse_step_file` (`bin/moltke.py:108`) a rule for multi-line values:
"A flush-left `word:` starts a new field and a blank line ends the current one;
only an indented non-empty line continues it." No writer honours the other half
of that rule. `write_step` (`bin/moltke.py:1791`), `append_to_plan`
(`bin/moltke.py:1809`) and `with_field` (`bin/moltke.py:1823`) all interpolate
the value into one f-string and split on `"\n".join(...)`, so a value with a
newline lands with its continuation lines flush left — the one shape
`parse_step_file` is documented to drop.

Case one, `--step new --goal` with a newline. The second line becomes a list
entry in `plan.md`:

    $ python3 bin/moltke.py --step new fold_lines --goal "teach the parser to fold lines
    2. S999 injected by a newline"
    moltke: created adocs/plan_todo/S004_fold_lines.md and listed S004 in plan.md.
    exit=0

    $ cat adocs/plan.md
    # Plan

    1. S001 base
    2. S002 pending
    3. S003 active
    4. S004  teach the parser to fold lines
    2. S999 injected by a newline

    $ python3 bin/moltke.py --validate
    VIOLATION: INV-3: plan.md lists S999 but no step file exists in plan_todo/,
    plan_current/, or plan_done/; create it with --step new, or fix the id in plan.md
    1 violation(s).
    exit=1

The step file gets the same treatment: `goal:` on one line and
`2. S999 injected by a newline` flush left underneath, which `parse_step_file`
discards. The injected `S999` also feeds `next_step_id`, which is F01's
trigger — the two findings compose.

Case two, `--step done --stamp` with a newline, which is the silent one.
`step_done` checks the stamp string it was handed (`bin/moltke.py:2055`), so a
stamp whose README and MANUAL mention is on the second line passes; the file it
writes then reads back without it:

    $ python3 bin/moltke.py --step done S003 --stamp "2026-08-09: suite green, 410 tests.
    README and MANUAL checked, no change needed."
    moltke: S003 completed and moved to plan_done/. Commit it; the move is the last
    action of the step.
    exit=0

    $ cat adocs/plan_done/S003_active.md
    id:         S003
    goal:       active
    done:      2026-08-09: suite green, 410 tests.
    README and MANUAL checked, no change needed.

    $ python3 bin/moltke.py --validate
    moltke: all checks pass
    exit=0

    $ git add -A && python3 bin/moltke.py --stop
    moltke: adocs/plan_done/S003_active.md was completed without the README and MANUAL
    check recorded; check both files and note it in the done: stamp (checking with no
    change needed is valid).
    exit=2

The gate is right about what it can see — that is S095's own sentence, with the
writer as the cause instead of the reader. The remedy it prints cannot be
followed: the file is under `plan_done/`, so `--pre-write` refuses to edit it,
and doing it from `Bash` after the file is staged or committed turns the Stop
block into an INV-7 violation:

    $ python3 bin/moltke.py --validate
    VIOLATION: INV-7: adocs/plan_done/S003_active.md changed under plan_done/; history
    is immutable: restore it with git checkout -- adocs/plan_done/S003_active.md
    1 violation(s).
    exit=1

Following *that* remedy restores the truncated stamp and the Stop gate blocks
again. The escape is the deadlock cap waiving after three attempts, which is
the safety net doing its job over a defect, not a fix.

I did not find a stamp or goal in this repository's own `plan_done/` that spans
lines, so nothing here is currently in that state: all 96 completed steps carry
a single-line stamp. This is latent, not live.

Impact. `--step new` can put a line into `plan.md` that no user typed and that
`--validate` then reports as a violation; `--step done` can write history that
disagrees with the stamp its own gate accepted, leave `--validate` green, and
block every Stop for the rest of the turn with an instruction that cannot be
carried out. Both are the tool corrupting the two files it exists to keep
consistent, on a success path.

Suggested resolution. One rule at the writers, not the readers. Either refuse a
`--goal` or `--stamp` containing a newline in `mode_step`, before anything is
written — the same place and shape as `step_name_problem` (`bin/moltke.py:90`)
— or have `with_field` and `write_step` indent every continuation line to the
field's value column so what is written is what `parse_step_file` reads back,
and have `append_to_plan` collapse the goal to one line for the list entry.
Refusing is the smaller change and matches how the CLI already handles operands
it cannot file safely.

### 2026-08-09_adversarial-F04  low  `--step status` deletes blank lines from the Parked block and absorbs whatever follows it, which the docs call verbatim

Status: closed

Closed 2026-08-11 by S100, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

`parked_lines` (`bin/moltke.py:2115`) collects everything after `- Parked:` to
the end of the file but keeps only non-blank lines:

    for line in read_file(status_path).splitlines():
        if not collecting:
            collecting = bool(re.match(r"^\s*-\s*Parked:", line))
            continue
        if line.strip():
            kept.append(line.rstrip())

`adocs/specs.md` (S094) says `--step status` "carries everything below
`- Parked:` to the end of the file through a regeneration, verbatim and
whatever its indentation", and `skills/step/SKILL.md` repeats it: "everything
below `- Parked:` to the end of the file is carried through verbatim, whatever
its indentation."

A `status.md` whose Parked block has blank lines between entries and a section
below it:

    - Parked:
      - first note

      - second note, separated by a blank line for readability

    ## Notes for humans

      something else entirely

after one `--step status`:

    - Parked:
      - first note
      - second note, separated by a blank line for readability
    ## Notes for humans
      something else entirely

A second regeneration is idempotent, so this is a one-time loss at the first
transition after the file is written.

Impact. Human-written formatting in the one file the workflow describes as
"the human's to write" is destroyed by a command that runs at every step
transition and reports success. Blank lines are markdown structure, not
whitespace: paragraphs merge, and a heading below the Parked list loses its
separation. The loss is small and never silently drops text, which is why this
is low rather than a repeat of .4-F07 — but "verbatim" is stated twice in the
documentation and is not what the code does.

Suggested resolution. Keep every line after the heading including blank ones,
trimming only trailing blank lines so repeated regeneration cannot grow the
file. Then the documented word is the implemented one.

### 2026-08-09_adversarial-F05  low  the reviewer write fence fails open when `agent_type` is present but not a string

Status: closed

Closed 2026-08-11 by S101, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

`payload_str` (`bin/moltke.py:893`) returns `""` for anything that is not a
string, and `mode_pre_write` (`bin/moltke.py:1211`) compares that against the
agent name:

    agent = payload_str(payload, "agent_type").split(":")[-1]
    if agent == REVIEWER_AGENT and not reviewer_may_write(root, rel):

An absent `agent_type` is the main thread and is never fenced (S016), so a
malformed one is treated as the main thread too:

    $ printf '%s' '{"agent_type":"moltke:adversarial_reviewer","tool_input":{"file_path":"bin/moltke.py"}}' | python3 bin/moltke.py --pre-write
    moltke: the adversarial_reviewer may write under adocs/audit/, ...
    exit=2

    $ printf '%s' '{"agent_type":["moltke:adversarial_reviewer"],"tool_input":{"file_path":"bin/moltke.py"}}' | python3 bin/moltke.py --pre-write
    exit=0

`adocs/specs.md` records for S087 that "an `agent_type` that is a list, killed
`--pre-write` ... the reviewer fence and the `plan_done/` refusal failing open,
the direction S016 named as wrong", and closes with "Whether Claude Code sends
these shapes is not established, and the fence does not depend on it". S087
fixed the crash, and with it the `plan_done/` and step-file rules, which now
run for any payload shape. The reviewer fence itself still fails open on that
exact shape, so for the one rule the sentence names, the fence does still
depend on the field's type.

What I could not confirm: that Claude Code ever sends a non-string
`agent_type`. I have no observation of it, and the specs say the same. This is
a property of the code, not a reproduction of a live payload.

Impact. If that shape ever occurs, a reviewer subagent's `Write` and `Edit` are
unfenced repository-wide and nothing says so — the failure direction S016 chose
against, on the grounds that a wrong block is loud and a wrong pass is silent.
DEC-022 already treats the fence as a fast clear failure rather than the
guarantee, and `--audit check` still reconciles the run, which is why this is
low.

Suggested resolution. Distinguish absent from malformed: read `agent_type` with
a helper that returns a sentinel when the key exists with a non-string value,
and fence on the sentinel rather than passing it through as the main thread. A
one-line test with a list-valued `agent_type` asserting exit 2 pins it.

### 2026-08-09_adversarial-F06  low  MANUAL names two refusals the code does not produce

Status: closed

Closed 2026-08-11 by S102, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

`MANUAL.md:176` lists what exits 1 on stderr:

    every refusal — `--step` transitions, `--audit new` on an existing report, an
    unknown operation, a failing `test_command` — goes to stderr.

`--audit new` has not refused on an existing report since S020: `next_report_path`
(`bin/moltke.py:2212`) takes a sequence suffix instead, which `MANUAL.md:146`
describes correctly in the same file:

    $ python3 bin/moltke.py --audit new adversarial
    moltke: created adocs/audit/2026-08-09_adversarial.md. ...
    exit=0
    $ python3 bin/moltke.py --audit new adversarial
    moltke: created adocs/audit/2026-08-09_adversarial.2.md. ...
    exit=0

`MANUAL.md:139` and `adocs/specs.md:815` both say `--decline` "refuses to
disable an already-enabled repository". `mode_decline` (`bin/moltke.py:1741`)
prints to stdout and returns `EXIT_OK`:

    $ python3 bin/moltke.py --decline        # in a repository with enabled: true
    moltke: .../.moltke.json already exists and is not a declined marker; leaving it
    alone. Remove it first if this repository should stop using the workflow.
    exit=0

So the documented refusal is indistinguishable, by exit code and by stream,
from the success it is refusing to perform. `mode_scaffold` on a declined
repository behaves the same way (`bin/moltke.py:1668`).

Impact. AGENTS.md §7 makes a doc claim a claim about code, and both claims are
traceable to code that does something else. The `--decline` case also matters to
anyone scripting the `init` flow outside Claude Code, which MANUAL explicitly
addresses ("If you script this, capture both"): exit 0 on both branches means a
script cannot tell whether the marker was written.

Suggested resolution. Two independent choices, and the report takes neither.
Either delete "`--audit new` on an existing report" from the exit-code prose or
make `--audit new` refuse a same-day re-run, which S020 deliberately rejected —
so deleting the clause is almost certainly right. For `--decline`, either drop
the word "refuses" from both documents, or route the already-enabled branch
through `refuse` so it exits 1 on stderr like every other refusal; the second
makes the exit-code table true without weakening anything.

### 2026-08-09_adversarial-F07  low  a step file's own `id:` field is written once and never read or checked

Status: closed

Closed 2026-08-11 by S103, on the 2026-08-11_adversarial re-run at 5625acb: re-measured from this finding's own reproduction and it no longer reproduces.

Evidence.

`write_step` (`bin/moltke.py:1796`) is the only place `id` appears as a field
key. Every reader derives the id from the filename instead — `plan_steps`
(`bin/moltke.py:243`) returns `STEP_FILE_RE.match(path.name).group(1)` — so the
field inside the file is decorative and nothing compares the two.

`templates/step_template.md` ships `id:         S000`. Copying it by hand, which
is how AGENTS.md §4 documents the step format, produces a file whose first line
contradicts its name:

    $ cp templates/step_template.md adocs/plan_todo/S050_hand_written.md
    $ echo "4. S050 hand written" >> adocs/plan.md
    $ python3 bin/moltke.py --validate
    moltke: all checks pass
    exit=0
    $ head -1 adocs/plan_todo/S050_hand_written.md
    id:         S000

Impact. Low and cosmetic today: every check keys on the filename, so behaviour
is correct. It matters for the reader — `plan_done/` is the project history a
human opens — and for any second tool that trusts the field the ruleset
documents. It is also an invariant that is stated in AGENTS.md's step-file
layout and enforced nowhere, which is the class this audit is asked to look
for.

Suggested resolution. Either check it — a step file whose `id:` disagrees with
its filename is an INV-6-adjacent violation naming both — or drop the field
from `templates/step_template.md` and `write_step` so nothing carries an id
that means nothing. Checking is the smaller change and makes the documented
layout true.

## Verdicts on 2026-08-08_adversarial.4

All seven findings were `planned` at this commit, with steps S088..S094 in
`plan_done/`. Each was re-measured from its own reproduction in a fresh fixture
repository, not from the step stamps. **None still reproduces.**

- **.4-F01** (`--step new` accepts any name). `--step new fix-parser` → exit 1,
  `step name 'fix-parser' must match [A-Za-z0-9_]+ ...`, no file in
  `plan_todo/`, no `plan.md` entry, `--validate` exit 0. `--step new
  ../../../../pwned` and `--step block S003 ../../blocked` refuse identically
  and nothing appears above the marked root. No longer reproduces.
- **.4-F02** (`--step done` overwrites `plan_done/`). With `S003` in both
  `plan_current/` and `plan_done/`: exit 1, "already in plan_done/ ... would
  overwrite finished history", and the `plan_done/` file is byte-identical
  afterwards. No longer reproduces.
- **.4-F03** (phantom `paused_by`). `paused_by: S042` with no such file →
  `--validate` exit 1 naming the step, the pauser and `--step unpause`; the
  named command clears it and `--validate` returns to exit 0. No longer
  reproduces. See F02 above: the neighbouring case, a pauser that exists but
  is unreachable, is open.
- **.4-F04** (setup modes raise). `--scaffold` and `--decline` in a
  mode-0555 directory both exit 1 with a message naming the path and no
  `Traceback` on either stream. No longer reproduces.
- **.4-F05** (a `git rev-parse --show-prefix` per path). With a counting shim
  on `PATH`, one `--validate` over this repository spawns 7 git processes in
  total, of which exactly 1 is `rev-parse --show-prefix`; `--validate` measured
  at 0.60s real. No longer reproduces.
- **.4-F06** (INV-8 remedy below the git top level). In a monorepo fixture with
  the marked root at `packages/foo`, the high-water-mark violation prints
  `git show 3251dd99:packages/foo/adocs/decisions.md`, and running that command
  verbatim from the marked root exits 0 and prints the removed content. No
  longer reproduces.
- **.4-F07** (`--step status` deletes a flush-left Parked entry). A block of
  `- flush left entry` and `  - indented entry` survives a regeneration whole.
  No longer reproduces. F04 above is a narrower residue of the same code: blank
  lines inside the block are still dropped.

## Mutation testing

Ten mutants were planted in a copy of the tree at
`/private/tmp/.../scratchpad/mut/` and the full suite run against each with
`-f`. **All ten were killed**, each by a test that names the behaviour:

- `reviewer_may_write` → always True: killed by
  `test_s005_hooks.TestMalformedHookPayloads.test_the_reviewer_fence_still_matches_a_well_formed_payload`
- `hides_content` → always False: killed by
  `test_s006_scaffold.TestPlanningPhaseNudge.test_a_prime_directive_written_only_inside_guidance_does_not_count`
- `_arrives_here` → `A` only, dropping `R`/`C`: killed by
  `test_s005_hooks.TestStop.test_a_present_arrival_still_reaches_the_stamp_gate`
- `scan_secrets` → scans nothing: killed by
  `test_s022_secrets.TestDetector.test_the_scan_reports_a_planted_secret`
- `git_prefix` → always `""`: killed by
  `test_s003_invariants.TestAMarkedRootBelowTheGitTopLevel.test_a_clean_vendored_project_validates_clean`
- `recap_pending` → always False: killed by
  `test_s005_hooks.TestStop.test_a_rename_between_documentation_and_source_counts_as_source`
- `foreign_worklog_lines` → always empty: killed by
  `test_s008_audit.TestAuditReconciliation.test_a_hook_append_next_to_a_fabricated_one_is_still_unexpected`
- `_is_new_file` → always True: killed by
  `test_s008_audit.TestAuditReconciliation.test_a_modified_existing_test_is_unexpected`
- INV-10's open-finding reference check → disabled: killed by
  `test_s004_invariants.TestAuditFindings.test_open_finding_without_reference_fails`
- `to_git_path` → drops the prefix: killed by
  `test_s003_invariants.TestAMarkedRootBelowTheGitTopLevel.test_inv8_still_sees_tampering_there`

The gap the mutants expose is not in the assertions but in the fixtures: the
S095 tests hand-write the multi-line step files they parse
(`tests/test_s007_step.py:1035`), so nothing in the suite feeds a multi-line
value through `--step done` or `--step new` and reads it back. That round trip
is F03.

## Checked and found clean

Recorded so a later run knows what was already looked at, and so the findings
above are read as the residue of a search rather than as its whole.

- `strip_guidance` / `fence_markers` pairing, INV-13 parity and INV-14's
  raw-versus-stripped heading comparison: consistent, comments removed before
  markers are counted in both.
- `--audit check` classification: reverted files, deleted files, a modified
  existing test, a commit made during the run, an unreachable baseline `HEAD`,
  and a `Bash`-written recap heading in the worklog append are all reported as
  unexpected. Exit 0 on this run's own footprint.
- `--pre-write` path resolution: `tests/../bin/moltke.py` is judged as
  `bin/moltke.py`; `adocs/plan_done/*` is refused for the main thread; a new
  file under `tests/` is permitted for the reviewer and an existing one is not.
- INV-7 and INV-8 against a monorepo fixture, a rename inside `plan_done/`, a
  deletion, and a mid-file rewrite of `decisions.md`, committed and
  uncommitted.
- `--step done` half-apply paths: unwritable step file, unwritable parent,
  missing `plan_done/`, duplicate id, stale pause, suite gate failure.
- `run_checks` cost on this repository: 0.437s for all sixteen invariants,
  0.131s for `CHEAP_CHECKS`, from 1034 `parse_step_file` calls over 106 step
  files. Roughly ten full re-reads of the plan tree per run — inefficient, not
  a defect at this size, and recorded here rather than as a finding.
- `AGENTS.md` and `CLAUDE.md` are byte-identical to their shipped templates.
- Suite: 410 tests, no skips, green; `--validate` green; `--audit check` exit 0.
