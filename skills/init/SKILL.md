---
name: init
description: Set up the moltke document-driven workflow in this repository, or record that it declines. Use when the user asks to initialise, set up, or adopt the workflow, and when a repository has no .moltke.json marker yet.
---

# Set up the workflow

Ask once. Scaffold or record the decline. Never ask again.

## 1. Read the marker

Check `.moltke.json` at the repository root.

- **Missing** — continue to step 2.
- **`"enabled": false`** — the user already declined. Say so in one line and stop.
  Do not ask again, do not scaffold.
- **`"enabled": true`** — already set up, which on a fresh clone is the normal
  case: the repository's state travels in git and only the plugin install is
  per-machine. Verify rather than scaffold, in this order:

  1. `python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --validate` — report the result
     verbatim. A violation here is the first thing to fix, before any work.
  2. `python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --session-start` — read back the
     `plan_current/` stack and the derived next step, so the user sees where the
     project is rather than being told it is set up.
  3. `python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --scaffold` — safe here: it
     creates only what is missing and overwrites nothing. Its `kept` lines say,
     file by file, whether `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/moltke.mdc`
     still match the installed plugin's templates. Report any drift as drift:
     it means the files were written by an older plugin, or edited on purpose,
     and both are legitimate.

  Offer a refresh of a drifted file as a question, naming what would change, and
  apply it only on an explicit yes — the ruleset may hold house rules that an
  overwrite would erase. Never touch `adocs/` or `.moltke.json` this way: those
  are the project's own state, not the plugin's.

## 2. Ask once

Ask whether to set up the workflow here. State plainly what it does:

- writes `AGENTS.md` (the ruleset), `CLAUDE.md`, `.cursor/rules/moltke.mdc`,
  `.moltke.json`, and a `adocs/` directory of state files
- turns on blocking enforcement in this repository only: hooks refuse writes
  into completed history, and refuse to end a turn with a stale `status.md`, an
  invariant violation, or source changes with no worklog recap
- costs nothing in repositories without the marker

If the answer is no, run `--decline` (step 5) and stop.

## 3. Scaffold

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --scaffold
```

It never overwrites an existing file. Anything already present is reported as
`kept`, including `AGENTS.md`. When something was kept, tell the user which
files were left alone and ask whether to merge the template in by hand; do not
merge without being asked.

Then set the marker's two remaining keys, in the same turn:

- `surface_guard`: `cli`, `api`, `both`, or `none`, depending on what this
  project actually exposes. `none` is only valid with a `decisions.md` entry
  stating why the project has no checkable surface.
- `test_command`: the project's real suite command, so `--step done` enforces a
  green suite instead of trusting one. Ask for it. Omit the key if there is no
  suite yet, and say plainly that completion is then unenforced.

## 4. Planning phase

The scaffold leaves `adocs/specs.md` and `adocs/plan.md` holding comments. They
are the two things the workflow cannot write for the user, and until they are
filled every check reports green on a repository that has adopted the workflow
and not yet used it. `--session-start` says so on every session until both are
filled. Do this now, in the same turn as the scaffold, unless the user asks to
stop.

**1. Elicit the prime directive.** One sentence: the single property this
project must never violate. Propose one from what the repository already does
and let the user correct it — a wrong proposal is easier to fix than a blank
page. Write it into the `## Prime directive` section of `adocs/specs.md`,
replacing the comment.

**2. Elicit the invariants.** Numbered `INV-1`, `INV-2`, ..., each stated as a
testable property, not an aspiration. Three to seven is a normal first set. Each
one earns a test and a `testing.md` row later; an invariant nothing can check is
a wish, so say so and reword it. Replace the placeholder list.

**3. Propose an ordered first plan.** Discuss it before writing anything: what
is being built, in what order, and why that order. Correctness and the things
everything else rests on come first. Then write the description paragraph at the
top of `adocs/plan.md`.

**4. Create the steps with the tool, one per planned step.**

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --step new <short_name> --goal "one line"
```

It allocates the next free id, writes the step file, and lists it in `plan.md`
in one move. Do not copy the step template by hand: hand-written step files drift
from the format the checks read, ids get reused, and `plan.md` and the
directories fall out of step, which is INV-3. Fill in `accepts`, `touches`, and
`excludes` in each file afterwards — `accepts` is the one that matters, because
it is what `--step done` is judged against. Reorder by editing the list in
`plan.md`; ids never move.

**5. Record what was decided.** Every choice made during this session that a
future reader would otherwise re-derive goes into `adocs/decisions.md` as a
`DEC-<nnn>` entry, with its rejected options and the reason each was rejected.
The scope, the order of the first plan, and the `surface_guard` and
`test_command` values are the usual ones. Decisions belong to the user: propose,
and record that the analysis was yours.

**6. Regenerate and verify.**

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --step status
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --validate
```

`--validate` must exit 0.

**7. Commit.** A planning session ends in a commit exactly like a coding session
(AGENTS.md §4). Do not hold the plan open uncommitted for review; commit it,
then present it. The agent commits; the user pushes.

Starting work is a separate turn: `--step start <id>` on the first step.

## 5. Decline

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --decline
```

Writes `{"schema": 1, "enabled": false}`. Every hook and check then exits 0
here, forever, until the file is deleted. Say in one line that it is recorded
and will not be asked again.

## Notes

- Adopting a repository that already has work in flight is a manual exercise:
  scaffold, then move existing plans into the `adocs/` files by hand. The
  planning phase above assumes a project whose plan is still to be written.
- An existing `AGENTS.md` is never touched. That is deliberate: it may be
  another tool's ruleset or a house standard.
