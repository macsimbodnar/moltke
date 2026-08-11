---
name: step
description: Drive the plan step lifecycle — create a step, start it, pause it behind a blocking discovery, complete it, or regenerate status.md from the filesystem. Use whenever work starts, finishes, or gets blocked in a repository with a .moltke.json marker.
---

# Plan step lifecycle

Every operation runs through the checker, so no transition can leave the plan
in a state that violates the invariants. It refuses rather than repairs, and it
names the condition that is missing.

All commands: `python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --step ...`

## Start work

```
--step new <short_name> [--goal "one line"]     # allocate the next id, list it in plan.md
--step start <id>                               # plan_todo -> plan_current
```

Ids are allocated in creation order and never reused, even after a file is
deleted. `new` appends to the end of `plan.md`; reorder that list by hand if
the step does not belong last. Order lives in `plan.md` and nowhere else.

Starting is refused when the active slot is taken. That refusal is information:
either finish what is in progress, or the new work is really a blocker, in
which case use `block`.

## Work discovered mid-step

Classify it before touching anything.

- **Trivial and in scope** — fix it now, no new step. A defect still gets a
  red-first regression test and a `testing.md` row. Note it in the recap.
- **Blocking** — `--step block <parent_id> <short_name>`. Creates the child in
  `plan_current/` with `blocks:` set, and pauses the parent with `paused_by:`.
- **Independent** — `--step new <name>` and leave it in `plan_todo/`, however
  tempting. Do not start it while a paused step sits in `plan_current/`.

If `block` is refused for depth, do not raise the limit. A blocker spawning its
own blockers means the plan is wrong at design level: stop, write a
`decisions.md` entry, and replan.

## Finish

```
--step done <id> --stamp "<what proves this step is finished>"
```

Refused, with the specific reason, when the step is not in `plan_current/`, is
paused, is still named in another open step's `blocks:`, has no `testing.md`
row, or when the stamp does not record the README and MANUAL check.

Before running it: code complete, full suite green, `testing.md` rows added
alongside the feature, README and MANUAL checked. Concluding that neither doc
needs a change is a valid outcome; not checking is not. Completing a child
unpauses its parent automatically.

The move to `plan_done/` is the last action of the step. Commit after it.
`plan_done/` is immutable history: never reopen or resume a checklist from it.

## Fast check, after the commit

One small subagent over the step's diff — the tier-1 review of AGENTS.md §10:

- scope: `git show <sha>` of the completion commit, nothing wider
- instruction: top real problems only, no praise, one screen, no writes
- routing: trivial and in scope → fix now; real → `--step new`; nothing → say
  so in one line and move on

No report file, no finding ids. If what it surfaces looks like risk rather than
a defect — security-adjacent, surface-changing — propose a full audit and let
the user accept or postpone (a postponed proposal is one Parked line in
status.md).

## Keep status honest

```
--step status
```

Regenerates `adocs/status.md` from the filesystem: last done, in progress,
derived next, blocked. The Parked list is human memory: everything below
`- Parked:` to the end of the file is carried through verbatim, whatever its
indentation. Run it at the end of every work turn, and any time `status.md`
disagrees with `plan_current/` — the directory wins.

## Verify

`--validate` after any transition should exit 0. If it does not, the step
commands refused for a reason or something was edited by hand; fix the named
violation rather than working around it.
