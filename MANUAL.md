# moltke manual

Install, set up, operate. For working on moltke itself, see
[README.md](README.md).

## What it does

moltke keeps a project's memory in tracked files, and gives agents one page
of rules for reading it cheaply and keeping it current:

- `AGENTS.md` — the ruleset, ending in `## Project rules`: what *you* decided
  agents may do here (git powers, subagents, tests, cadence), recorded by an
  interview
- `adocs/status.md` — where the project stands, one small read
- `adocs/plan.md` — what is being built, ordered open steps
- `adocs/plan_todo|current|done/` — one file per step; the directory is the
  state, moved by hand
- `adocs/specs.md` — prime directive and invariants
- `adocs/decisions.md` — why things are the way they are
- `adocs/audit/` — findings, as evidence, before any fix

Every one of those travels in your repository. Any tool that reads
`AGENTS.md` gets the workflow — Claude Code, Cursor, anything; the plugin
itself is only needed to run the three skills. Nothing blocks and nothing
polices: an agent that ignores the rules is caught by the diff, not by a
hook.

## Install

Once per Claude config root. The CLI reads `~/.claude`; other clients, the
desktop app among them, set `CLAUDE_CONFIG_DIR` to a root of their own. Each
root has its own plugin registry, and a root without moltke gets no skills
and no reviewer agent — silently. Check what a root has with
`CLAUDE_CONFIG_DIR=<root> claude plugin list`.

```
claude plugin marketplace add https://github.com/macsimbodnar/moltke.git
claude plugin install moltke@moltke
```

Updating: releases ship only on a `version` bump, so `claude plugin update
moltke@moltke` does nothing until one lands. Scope is per install — a root
holding both `user` and `project` scope installs needs the update once per
scope (`--scope project` from the project directory).

## Set up a repository

```
/moltke:init
```

It interviews you — nine questions, each with a default, accept-all-defaults
as the fast path:

| Topic | You decide |
|---|---|
| GIT | commit freely / on request / also push / read-only |
| AGENTS | subagents freely / reviews only / ask first |
| TESTS | green suite gates completion, red-first / green gates / advisory / none |
| PLAN | active steps per agent: one / N / unlimited |
| DOCS | which documents are checked at completion |
| REVIEW | fast check after each step, or not |
| AUDIT | full audits on demand, or proposed on risk |
| DEPS | dependencies need asking, or not |
| COMMITS | commit per step, or on request |

The answers become one line each under `## Project rules` in `AGENTS.md`.
Then it scaffolds `AGENTS.md`, `CLAUDE.md`, a Cursor pointer, and `adocs/` —
never overwriting anything that exists — and walks you through the first
plan: prime directive, invariants, ordered steps. Declining writes nothing;
ask again whenever.

## Daily use

You mostly do nothing: agents orient from `status.md` and `plan.md` (two
small files), work the first open step, move its file through the plan
directories, and rewrite `status.md` before ending a turn that changed plan
state. Things you might do yourself:

- reorder priorities: edit the Open list in `adocs/plan.md` — order lives
  there and nowhere else
- change what agents may do: `/moltke:rules` — every change is also recorded
  as a decision
- read `adocs/status.md` when you want to know where things stand; the
  `Parked:` list at its bottom is the shared scratchpad for things worth
  remembering that are not yet steps
- ask for an audit: `/moltke:audit` — an adversarial reviewer on a clean
  context writes a dated report under `adocs/audit/`, and every finding
  becomes a step or a recorded decision before anything is fixed

## Teams

Everything is tracked files, so branches and merges work normally. Two
habits keep merges clean: after merging, rewrite `status.md` from the plan
directories (the directories win); and if two branches allocated the same
step id, the not-yet-merged side takes the next free id — file and `plan.md`
entry — before merging, noted in the merge commit. That is the one renumber
the never-reuse rule sanctions, because two files claiming one id is worse.

## Migrating from 0.x

The 0.x enforcement product is gone; the workflow is the same shape. In an
existing 0.x repository:

- your `adocs/` keeps working unchanged — same directories, same files;
  `testing.md` is no longer part of the layout (keep it if you use it,
  nothing reads it)
- `.moltke.json` is no longer read by anything — delete it or leave it
- hooks no longer exist, so nothing blocks turns or writes any more, and the
  `--step`/`--watch`/`--validate` commands are gone: step files move by hand
  per `AGENTS.md`
- refresh `AGENTS.md` by hand: take the v1 template's base sections, keep
  your own `## Project rules` (or run the `/moltke:init` interview in a
  scratch checkout and copy the result)

## Known limits

- Nothing enforces the rules. moltke v1 trades policing for simplicity; if
  your agents will not follow a one-page ruleset, no markdown will save you.
- One plugin install per Claude config root, and updates are per scope —
  see Install.
- An install ships this repository whole — moltke's own `adocs/` plan and
  audit history included, which is most of the megabyte-plus an install
  weighs — cached once per config root and per version. The repository root
  is the plugin root by choice (DEC-020); a `plugin/` subdirectory move is
  the parked escape hatch if the weight starts to matter.
