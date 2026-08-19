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
hooks/hooks.json                 four hook events, all shelling out to bin/moltke.py
skills/init|step|audit/SKILL.md  the three skills, invoked as /moltke:<name>
agents/adversarial_reviewer.md   auditor: reads anything, writes adocs/audit/ and new tests/
templates/                       what `--scaffold` copies into a target repository
tests/                           the suite; tests/surface.py declares the guarded surface
AGENTS.md                        the live ruleset; templates/AGENTS.md is its shipped copy
adocs/                         moltke's own workflow state (it uses itself)
```

`adocs/` is not part of the plugin's behaviour. It is this repository's own
plan, decisions, and testing ledger, because moltke is the first
project to use moltke. Read `adocs/specs.md` before changing anything.

## Build

There is nothing to build. `bin/moltke.py` is Python 3 standard library only,
with no dependencies, because it runs on every prompt and startup cost matters.
The suite is run on the macOS system Python 3.9 and on 3.14, and passes on both;
nothing in between is exercised, and no lower bound has been tested.

## Test

Full suite:

```
python3 -m unittest discover -s tests
```

476 tests, 3 of which skip on a case-sensitive filesystem. A test whose
precondition is genuinely absent skips with a message saying what would activate
it, rather than passing silently.

Check this repository against its own rules, which is also what other tools
(Codex, Cursor) can run since hooks only exist in Claude Code:

```
python3 bin/moltke.py --validate
```

The audit gate, after a reviewer run: the first reconciles what the run changed
against the baseline `--audit new` recorded, the second refuses while an open
finding has neither a plan step nor a decision.

```
python3 bin/moltke.py --audit check
```

```
python3 bin/moltke.py --audit list
```

Exit codes and streams, traced to the code that produces them:

| Exit | Meaning | Stream | Produced by |
|---|---|---|---|
| `0` | clean, or a hook with nothing to say | stdout, when there is output | every mode's success path |
| `1` | **findings**: invariants, audit bookkeeping, reconciliation | stdout | `run_validate`, `audit_list`, `audit_check` |
| `1` | **refusals**: a command that will not proceed, and why | stderr | `refuse`, which is the return path for every `--step` and `--audit new` refusal, the `test_command` gate, and an unknown operation |
| `2` | a blocked action, with what to do about it | stderr | `mode_pre_write`, `mode_stop`, `mode_post_write` |

Exit `1` therefore does not tell you which stream to read: findings go to stdout,
refusals to stderr. If you script this, capture both. Two further details worth
knowing when parsing: `--post-write` returns `2` but is non-blocking by contract,
since the tool it follows has already run, and stderr can carry a warning on an
exit `0` path — `--audit new` outside a git repository says so there while still
succeeding.

After deliberately changing the CLI surface, and only after describing the
change in `adocs/specs.md` and `MANUAL.md` in the same commit:

```
python3 tests/test_s009_surface.py --refresh
```

The golden test fails on any added, renamed, or removed flag, `--step` / `--audit`
operation, skill, hook event, or recognised `.moltke.json` key, and on any rewiring
of a hook: it carries one `(event, tool matcher, mode flag)` triple per declared
hook command, not just the event names. A second check
requires each one to appear in the specs table and in MANUAL, so refreshing the
golden alone never makes the suite green. The declarations it reads live in
`tests/surface.py`.

No environment variables. `bin/moltke.py` reads none; behaviour is controlled
by `.moltke.json` in the repository being checked.

## Working on it

This repository enforces the rules it ships. Read `AGENTS.md` first; it is the
whole contract. The short version:

- Work moves through `adocs/plan_todo` → `plan_current` → `plan_done`, driven
  by `python3 bin/moltke.py --step ...`, never by moving files by hand.
- Red first. Write the test, watch it fail, record what it printed, then
  implement. A test never observed failing is not evidence.
- `testing.md` rows are voluntary documentation; the `test_command` gate is
  what enforces the green suite.
- Decisions go in `adocs/decisions.md` before or alongside the change, with
  their rejected options.
- The agent commits; the user pushes.
- Your checkout is not what the hooks run. Installing from a local path copies
  the tree into the plugin cache of one Claude config root, so an edit to
  `bin/moltke.py` reaches the live hooks only after `claude plugin update
  moltke@moltke` in that root — and a machine with more than one root needs the
  install repeated per root (DEC-057, MANUAL's Install section). Run
  `--validate` and the suite against the checkout; that is what they read.

Every commit is expected green: full suite plus `--validate`.

## Known issues

In [MANUAL.md](MANUAL.md#known-issues), so users and developers read the same
list.
