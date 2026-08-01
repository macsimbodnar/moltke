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
- **`"enabled": true`** — already set up. Run
  `python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --validate` and report the result.
  Scaffolding again is safe but usually pointless; only do it to restore a
  deleted file.

## 2. Ask once

Ask whether to set up the workflow here. State plainly what it does:

- writes `AGENTS.md` (the ruleset), `CLAUDE.md`, `.cursor/rules/moltke.mdc`,
  `.moltke.json`, and a `project/` directory of state files
- turns on blocking enforcement in this repository only: hooks refuse writes
  into completed history, and refuse to end a turn with a stale `status.md`, an
  invariant violation, or source changes with no worklog recap
- costs nothing in repositories without the marker

If the answer is no, run `--decline` (step 4) and stop.

## 3. Scaffold

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --scaffold
```

It never overwrites an existing file. Anything already present is reported as
`kept`, including `AGENTS.md`. When something was kept, tell the user which
files were left alone and ask whether to merge the template in by hand; do not
merge without being asked.

Then, in the same turn:

1. Set `surface_guard` in `.moltke.json` to `cli`, `api`, `both`, or `none`
   depending on what this project actually exposes. `none` is only valid with a
   `decisions.md` entry stating why the project has no checkable surface.
2. Fill `project/specs.md`: the prime directive, then numbered invariants. This
   is the one file the workflow cannot write for the user. Ask for the prime
   directive if it is not obvious from the repository.
3. Seed `project/plan.md` and one step file per planned step, using
   `${CLAUDE_PLUGIN_ROOT}/templates/step_template.md`.
4. Verify: `python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --validate` must exit 0.
5. Commit. The agent commits; the user pushes.

## 4. Decline

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --decline
```

Writes `{"schema": 1, "enabled": false}`. Every hook and check then exits 0
here, forever, until the file is deleted. Say in one line that it is recorded
and will not be asked again.

## Notes

- Adopting a repository that already has work in flight is a manual exercise:
  scaffold, then move existing plans into the `project/` files by hand.
- An existing `AGENTS.md` is never touched. That is deliberate: it may be
  another tool's ruleset or a house standard.
