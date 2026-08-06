# moltke

A Claude Code plugin that gives an agent durable memory of a project: what to
do next, why past choices were made, what has been audited, what is verified.
State lives in tracked files, and hooks refuse to let it rot.

Moltke commanded armies he could not see by writing orders that survived his
absence. Same problem, smaller scale.

For installing and using it, see [MANUAL.md](MANUAL.md). This file is for
working on moltke itself.

## Layout

```
.claude-plugin/plugin.json       manifest: name, explicit version
.claude-plugin/marketplace.json  single-plugin marketplace entry
bin/moltke.py                    every check and command, one entry point
hooks/hooks.json                 five hook events, all shelling out to bin/moltke.py
skills/init|step|audit/SKILL.md  the three skills, invoked as /moltke:<name>
agents/adversarial_reviewer.md   auditor: reads anything, writes only adocs/audit/
templates/                       what `--scaffold` copies into a target repository
tests/                           the suite; tests/golden/ holds the CLI surface
AGENTS.md                        the live ruleset; templates/AGENTS.md is its shipped copy
adocs/                         moltke's own workflow state (it uses itself)
```

`adocs/` is not part of the plugin's behaviour. It is this repository's own
plan, decisions, testing ledger, and worklog, because moltke is the first
project to use moltke. Read `adocs/specs.md` before changing anything.

## Build

There is nothing to build. `bin/moltke.py` is Python 3 standard library only,
with no dependencies, because it runs on every prompt and startup cost matters.
Developed and tested on Python 3.12.

## Test

Full suite:

```
python3 -m unittest discover -s tests
```

116 tests, no skips. A test whose precondition is genuinely absent skips with a
message saying what would activate it, rather than passing silently.

Check this repository against its own rules, which is also what other tools
(Codex, Cursor) can run since hooks only exist in Claude Code:

```
python3 bin/moltke.py --validate
```

Exit codes: `0` clean, `1` invariant violations listed on stdout, `2` a blocked
action with the reason on stderr.

After deliberately changing the CLI surface, and only after describing the
change in `adocs/specs.md` and `MANUAL.md` in the same commit:

```
python3 tests/test_s009_surface.py --refresh
```

The golden test fails on any added, renamed, or removed flag or `--step` /
`--audit` operation. A second check requires each one to appear in the specs
table and in MANUAL, so refreshing the golden alone never makes the suite
green.

No environment variables. `bin/moltke.py` reads none; behaviour is controlled
by `.moltke.json` in the repository being checked.

## Working on it

This repository enforces the rules it ships. Read `AGENTS.md` first; it is the
whole contract. The short version:

- Work moves through `adocs/plan_todo` → `plan_current` → `plan_done`, driven
  by `python3 bin/moltke.py --step ...`, never by moving files by hand.
- Red first. Write the test, watch it fail, record what it printed, then
  implement. A test never observed failing is not evidence.
- `testing.md` rows are added with the feature. `--step done` refuses without
  one.
- Decisions go in `adocs/decisions.md` before or alongside the change, with
  their rejected options.
- The agent commits; the user pushes.

Every commit is expected green: full suite plus `--validate`.

## Known issues

In [MANUAL.md](MANUAL.md#known-issues), so users and developers read the same
list.
