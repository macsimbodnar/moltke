# Specs: moltke

Current state only. The narrative lives in `adocs/plan_done/` step stamps,
commit messages, and git history of this file. The 0.x enforcement product
this file used to specify is history behind the 1.0 pivot (DEC-062).

## Prime directive

Project state is always derivable from tracked files alone. An agent that
trusts nothing but the filesystem knows what to do next and why — in any
session, any tool, any machine.

## Invariants

INV-1 through INV-17 belonged to the 0.x enforcement product and retired en
bloc with it (DEC-062); numbers are never reused, and the retired
definitions are in this file's git history. The 1.x product holds three,
checked by dogfooding and review rather than by code:

- INV-18 the plugin ships no executable code: skills, one agent, templates,
  documentation — markdown only, no hooks, no dependencies.
- INV-19 `init` never overwrites an existing file; everything it skips is
  reported as kept.
- INV-20 allocated ids are never reused or renumbered: step `S<nnn>`,
  decision `DEC-<nnn>`, audit finding `YYYY-MM-DD_<type>[.N]-F<nn>`
  (`.N` marks a same-day re-run; type is `[A-Za-z0-9_-]+`). One
  exception: when two branches allocated the same step id, the not-yet-merged
  side takes the next free id — file and `plan.md` entry — before merging,
  noted in the merge commit; two files claiming one id is worse.

## What is being built

A Claude Code plugin that sets up a document-driven development workflow as
rules. Three skills and one agent:

| Piece | Does |
|---|---|
| `/moltke:init` | interviews the user over a nine-topic catalog (GIT, AGENTS, TESTS, PLAN, DOCS, REVIEW, AUDIT, DEPS, COMMITS), records each answer as one line under `## Project rules` in `AGENTS.md`, scaffolds `adocs/` and the entry-point files from templates, then elicits prime directive, invariants, and the first plan (DEC-063) |
| `/moltke:rules` | shows, adds, changes, or drops Project rules lines; every change is also a `decisions.md` entry |
| `/moltke:audit` | evidence-first audit: dated report under `adocs/audit/`, written by the reviewer before any fix; every finding ends in a step or a decision; the loop stops when a re-run has no high and no medium (DEC-035) |
| `adversarial_reviewer` | subagent, arrives cold (DEC-036), writes only its own report and new regression tests, never fixes |

The workflow the ruleset describes: one file per step moved by hand through
`plan_todo/` → `plan_current/` → `plan_done/`; `status.md` rewritten by hand
at the end of any turn that changed plan state; orientation is reading
`status.md` then `plan.md`; precedence specs > plan > status; filesystem
beats prose.

Name: `moltke`. Distribution: git repository plus a single-plugin
marketplace entry, installed per Claude config root. Updates ship only on a
`version` bump in `.claude-plugin/plugin.json`.

## Non-goals

- No enforcement: no hooks, no blocking, no checker. The rules work because
  agents follow them and violations are visible in diffs.
- No daemon, no state outside the repository.
- No code, no dependencies, no network access.
- No automatic fixing; repair is the author's.
- No enforcement of document history: git is the archive (DEC-042).

## Open items

None open.
