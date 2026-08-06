# Agent operating rules

Applies to any agent working in this repository. Additional to, not a replacement for, tool-level configuration.
Claude Code entry point: `CLAUDE.md` containing `@AGENTS.md`.

Marker file: `.moltke.json` at repo root.
Present with `"enabled": true` means these rules are active and enforced.
Present with `"enabled": false` means the user declined; do not ask again, do not scaffold.
Absent: ask once whether to set the workflow up, then write the marker either way.

```json
{
  "schema": 1,
  "enabled": true,
  "plan_active_max": 1,
  "plan_stack_max": 3,
  "surface_guard": "cli"
}
```

`surface_guard` is one of `cli`, `api`, `both`, `none`. `none` is only valid alongside a `decisions.md` entry stating why this project has no checkable surface.

## 1. Reading order and precedence

Read in this order before acting:

1. `adocs/status.md` where we are
2. `adocs/plan.md` what is planned and in which order
3. `adocs/specs.md` what the software must do
4. `adocs/decisions.md` why things are the way they are

Precedence when documents disagree: **specs > plan > status**.
Code that disagrees with specs is a bug or an unrecorded decision. It is never silently the new truth.

**Filesystem state beats prose.** `status.md` is a convenience view, not the source of truth. If it disagrees with the contents of `plan_current/`, the directory wins and `status.md` is regenerated from it before any work starts. This matters because `status.md` is written at the end of a turn, so a crashed or interrupted session leaves it stale.

**Next is derivable, never asserted.** The next step is the first step in `plan.md` order that is not in `plan_done/`. `status.md` restates it for convenience but does not own it. A resumed session that trusts nothing but the filesystem still knows what to do.

## 2. File map and write discipline

| Path | Purpose | Write mode | Update trigger |
|---|---|---|---|
| `README.md` | developer facing: layout, build, test, exact commands | rewrite in place | checked at every step completion |
| `MANUAL.md` | end user facing: install, operate, known bugs | rewrite in place | checked at every step completion |
| `.moltke.json` | marker, schema version, limits | rewrite in place | schema change only |
| `adocs/status.md` | last done, in progress, next, blocked, parked | rewrite in place | end of every work turn |
| `adocs/specs.md` | prime directive, invariants, required behavior | edit in place, dated inline notes | same commit as any behavior change |
| `adocs/plan.md` | plan description and ordered step list | rewrite in place | any plan change |
| `adocs/plan_todo/` | one file per pending step | add and remove | step created or started |
| `adocs/plan_current/` | active step plus any paused parents, as a stack | add and remove | step started, paused, or completed |
| `adocs/plan_done/` | completed steps, immutable history | append by move only | step completed |
| `adocs/testing.md` | acceptance ledger | append rows | with the feature, never after |
| `adocs/decisions.md` | decision log, newest last | append only | before or alongside the change |
| `adocs/worklog.md` | prompts and recaps | append by convention, not enforced | every prompt, recap on work turns |
| `adocs/audit/` | adversarial, security, bug hunt reports | add files | per audit run |

`adocs/decisions.md` and `adocs/plan_done/` are never reordered, rewritten, or trimmed, and this is enforced: superseded content is marked, not deleted. The worklog follows the same habit but is not checked, so a genuine correction — a mistyped recap, a secret pasted into a prompt — is a normal edit rather than a rule violation.

## 3. Prime directive and invariants

`adocs/specs.md` opens with:

- one **prime directive**, the single property the project must never violate
- numbered **invariants** `INV-1`, `INV-2`, ... stated as testable properties

Invariants are referenced by number from code comments, test names, and commit messages.

Priority principle: correctness outranks features and portability. A reproduced correctness defect jumps the queue ahead of planned work.

## 4. Plan lifecycle

`adocs/plan.md` holds the overall description plus the ordered list of step ids. It does not hold step detail.

One file per step named `S<nnn>_short_name.md`. **Ids are stable and never renumbered.** They are allocated in creation order, not plan order, so inserting or reordering work is a one-line edit to `plan.md` and never a file rename. Step files carry:

```
id:         S042
goal:       one line
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:  DEC-007, DEC-011      # decisions this step implements
closes:     AUD-2026-08-01-F03    # audit findings this step resolves
blocks:     S039                  # set only when this is a blocking child
paused_by:  S043                  # set only while paused
done:       completion stamp, filled in last
```

Order lives in `plan.md` and nowhere else.

Transitions:

- `plan_todo/` to `plan_current/` when work on the step actually starts. The agent may do this without asking.
- `plan_current/` to `plan_done/` only when all of: code complete, full suite green, `testing.md` rows added, README and MANUAL checked, completion stamp written into the step file. **The move is the last action of the step.**
- `plan_done/` is immutable and is the project history. Never reopen or resume a checklist from it.

### Work discovered mid-step

`plan_current/` is a **stack**, not a set. Classify the discovery first:

**Trivial and in scope.** Fixable inside the current step without changing its acceptance criteria. Do it now, no new step file. If it is a defect it still gets a red-first regression test and a `testing.md` row. Note it in the recap.

**Blocking.** Must be finished before the current step can complete. Create a step file, set `blocks: <parent_id>` in it, promote it straight to `plan_current/`, and set `paused_by: <child_id>` with a date on the parent. Invariants:

- exactly `plan_active_max` steps in `plan_current/` are non-paused, default 1
- total stack depth in `plan_current/` never exceeds `plan_stack_max`, default 3
- a step cannot move to `plan_done/` while any step declares it in `blocks`

**Independent.** Useful but not blocking. It goes to `plan_todo/` and is not started now, however tempting.

Escape hatch: if a blocker spawns its own blocker past `plan_stack_max`, the plan is wrong at the design level, not the step level. Stop work, write a `decisions.md` entry, replan.

`status.md` shows the stack top to bottom, so a resumed session knows what is paused and why.

When the plan turns out wrong once it meets the code: stop, write a `decisions.md` entry, amend the plan. Never deviate silently.

A planning session ends in a commit exactly like a coding session. Do not hold a plan open uncommitted for review; commit it, then present it.

## 5. Git

- The agent **never pushes**. The agent commits. The user pushes.
- Commit triggers: on request, on step completion, and on any change to the plan.
- Every commit is green: build, lint or vet, and the full test suite pass at that commit.
- Message convention: imperative subject under 72 characters; body explains **why**, not what; reference the step id and any relevant `INV-n`.
- No history rewriting, no force operations, no branch deletion without an explicit request.

## 6. Testing

`adocs/testing.md` is an acceptance ledger, not a plan. Each row is an acceptance criterion with its covering test. Rows are added together with the feature, never afterwards.

- **Red first.** A defect found while building gets a minimized regression test before the fix.
- **Verify red by observation.** Disable the fix, run the test, confirm it fails, record what it printed. A test never observed failing is not evidence.
- **Non-vacuous by construction.** A test asserting that X does not happen must first assert the precondition that would make X happen, and fail if that precondition is absent.
- Behavior changes deliberately: strengthen or re-target the test. Never relax it, never delete it.
- Security and secret-leak checks run inside the normal suite, not as a separate ritual.
- `README.md` lists the exact commands: full suite, audit gate, long or opt-in runs, with every environment variable and its real semantics stated (a probability is documented as a probability, not as a flag).

## 7. Documentation

**Doc claims are claims about code, not intent.** Any statement about where output surfaces, what a flag does, or what a default is must be traced to the code path that produces it. Verify against code, not against specs.

- `README.md`: layout, build, test, commands. Points at `MANUAL.md` for usage rather than repeating it.
- `MANUAL.md`: install, operation, known bugs. Minimal overlap with README.
- Known bugs discipline: a bug found gets an entry even when unfixed; a bug fixed has its entry removed in the fix's own commit; a partially fixed bug has its entry narrowed, not removed.
- The trigger is **checked**, not updated. At every step completion both files are checked. Concluding that neither needs a change is a valid outcome. Not checking is not.
- A golden test over the project's public surface is **mandatory**, covering whatever `surface_guard` names. It fails when a command, flag, or endpoint is added, renamed, or removed, and stays failing until MANUAL and the specs rows are updated in the same commit. Opting out requires setting `surface_guard` to `none` and recording the reason in `decisions.md`.
- Prose style: minimal and information dense, fragments over sentences. Compression never drops a fact. Copy verbatim and never reword code, commands, flags, paths, config keys, URLs, versions, and dates.
- Spec edits carry a dated inline note in the same commit as the behavior change they describe.

## 8. Decisions

`adocs/decisions.md`, append only, newest last: appending costs no read, append-only stays literal (earlier bytes never move), recency is `tail`, lookup is grep. Every entry has a stable id `DEC-<nnn>` and topic tags, so a question like "what did we decide about retries" is one grep, not a read of the whole file. Entry format:

```
## DEC-012  2026-08-01  short title
Tags:         retry, network
Context:      what forced a choice
Decision:     what was chosen, and by whom
Rejected:     options not taken, each with the reason
Consequences: what this now constrains
```

Ids are referenced from step files, commit messages, code comments, and `specs.md`. That makes the link traceable in both directions: from a line of code to the reason it exists, and from a decision to everywhere it was applied.

- Decisions belong to the user. Agents propose. When an agent supplied the analysis and the options, record that.
- Recording rejected options is mandatory. It is what stops the same question being re-derived later.
- A reversal does not delete the old entry. Mark it `VOID`, dated, with a pointer to the superseding entry.
- Trigger: before or alongside the change, never after.

## 9. Worklog

`adocs/worklog.md`, append by convention. Unlike `decisions.md` it is not enforced: nothing cites a worklog line by id, so correcting or trimming it is an ordinary edit and needs no ceremony. Do not make a habit of it — the value is that it records what actually happened.

- Every prompt is appended verbatim with a timestamp. This is written mechanically and is not the agent's responsibility.
- Work turns additionally get a recap: step id, what changed, files touched, tests added, commit sha.
- Pure questions and discussion need no recap.

**The worklog is not a context source.** It is forensic history for humans, and it grows without bound. Never read it to work out what to do or why something is the way it is; that is what `status.md`, `plan.md`, `specs.md`, and `decisions.md` are for. If something in the worklog turns out to matter, promote it into one of those files. An agent that starts a session by reading the worklog is doing it wrong.

## 10. Audit

`adocs/audit/` holds reports from adversarial verification, security audits, and bug hunts. One file per run, named `YYYY-MM-DD_type.md`, and a re-run on the same day takes a sequence suffix: `YYYY-MM-DD_type.2.md`. A report is never overwritten, so closing a finding on the day it was found is a normal re-run rather than a wait.

- The report is written **before** any fix. A report edited while fixing stops being evidence of what was found.
- Every finding gets an id `YYYY-MM-DD_type-F<nn>`, a severity, and a status of `open`, `planned`, `closed`, or `accepted`.
- Every finding ends in one of two places: a plan step whose `closes:` field names it, or a `decisions.md` entry stating why it will not be acted on, which moves it to `accepted`.
- A finding moves to `closed` only after the audit is re-run and no longer reports it. Fixing without re-running leaves it `planned`.
- A report with open findings and no corresponding steps is not finished work.

Audits run against the code, not against the specs. An audit that only confirms the documentation is a documentation review.

## 11. Hard prohibitions

The agent does not:

- push, force push, or rewrite git history
- write to `adocs/plan_done/`
- reorder, rewrite, or delete entries in `adocs/decisions.md`
- delete or weaken a test to make a change pass
- create plan step files outside the three plan directories
- claim a step complete before the suite is green and `testing.md` rows exist
- complete a step that another step still declares in `blocks`
- start independent work while a paused step sits in `plan_current/`

## 12. Memory lives in the repository

Nothing that matters is allowed to exist only in an agent's own memory, session transcript, or tool-local notes. Those are per machine, per tool, and per account, and they do not survive a new agent, a new session, or a colleague opening the repo.

If it is worth remembering, it goes into a tracked file: state into `status.md`, intent into `specs.md`, reasoning into `decisions.md`, work into the plan directories. The repository is the memory. Everything else is a cache.
