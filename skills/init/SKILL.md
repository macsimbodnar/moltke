---
name: init
description: Set up the moltke document-driven workflow in this repository - interview the user, record the answers as Project rules, scaffold the adocs/ memory, and elicit the first plan. Use when the user asks to initialise, set up, or adopt the workflow.
---

# Set up the workflow

An interview, a scaffold, a first plan. Everything written here travels in the
repository; the plugin is only needed to run the skills. Nothing enforces the
result — the rules work because agents read them, so write them exactly.

## 1. Detect

- `adocs/` exists and `AGENTS.md` has a `## Project rules` section: already
  set up. Read `adocs/status.md` and `adocs/plan.md` back to the user (the
  Orient order), mention `/moltke:rules` for changing rules, stop.
- `AGENTS.md` exists but is not moltke's ruleset: never overwrite it. Offer
  to continue and append instead, or to stop — an existing ruleset may be
  another tool's or a house standard. If appending: run the interview as
  normal, and in step 3 append the whole ruleset — base sections and the
  recorded `## Project rules` together — to the existing file as one clearly
  marked section, instead of creating `AGENTS.md`.
- `AGENTS.md` is moltke's ruleset (it has `## Project rules`) but `adocs/`
  is missing: partial state. Skip the interview — the rules are already
  recorded — and scaffold only what is missing in step 3; the existing
  `AGENTS.md` stays untouched, and changing its rules is `/moltke:rules`'
  section rewrite, never a second ruleset.
- None of the above: continue.

If the user declines at any point: write nothing, mark nothing, and say they
can ask again any time. Nothing in v1 nags, so nothing needs a durable "no".

## 2. Interview

Ask the catalog below — one question at a time with the question UI where
available, in chat otherwise. **Offer defaults-for-everything first**:
accepting it is one answer, not nine. Show each rule line as it will be
recorded; the user's own wording wins over the canned one.

| Id | Question | Options, default first → recorded line |
|---|---|---|
| GIT | What may agents do with git? | commit freely, never push → `- GIT: commit freely; never push — the user pushes.` · commit only on request → `- GIT: commit only when asked; never push.` · commit and push → `- GIT: commit freely; push to <branch> when a step completes.` · read-only → `- GIT: read-only — no commits; the user handles git.` |
| AGENTS | May agents spawn subagents? | freely → `- AGENTS: subagents allowed freely.` · reviews and exploration only → `- AGENTS: subagents only for reviews and read-only exploration.` · per-spawn consent → `- AGENTS: no subagent without asking first.` |
| TESTS | What test discipline? | green before done, red first → `- TESTS: the suite is green before a step is marked done (<command>); a defect gets a failing test before its fix.` · green before done → `- TESTS: the suite is green before a step is marked done (<command>).` · advisory → `- TESTS: tests are encouraged, not gating.` · none → `- TESTS: no automated suite — each done: stamp says what was verified by hand.` |
| PLAN | How many steps in progress at once, per person? | one → `- PLAN: one active (non-paused) step per agent.` · N → `- PLAN: at most <N> active steps per agent.` · unlimited → `- PLAN: no limit on active steps; keep status.md honest.` |
| DOCS | Which documents are checked at every step completion? | README → `- DOCS: README checked at every step completion.` · README and MANUAL → `- DOCS: README and MANUAL checked at every step completion.` · none → `- DOCS: no documents gate completion.` |
| REVIEW | Review each step's diff after completion? | yes → `- REVIEW: fast check after each completed step.` · no → `- REVIEW: no per-step review.` |
| AUDIT | Full audits? | on demand → `- AUDIT: full audits on demand only.` · propose on risk → `- AUDIT: propose a full audit on real risk (security-touching, public surface, long unaudited stretch); the user accepts or parks it.` |
| DEPS | May agents add dependencies? | never without asking → `- DEPS: never add a dependency without asking; state what it buys and what it costs.` · freely → `- DEPS: dependencies may be added when warranted; each one is a recorded decision.` |
| COMMITS | Commit cadence? | per completed step → `- COMMITS: commit at each completed step and at any plan change.` · on request → `- COMMITS: commit only when the user asks.` |

Two answers need a follow-up: a gating TESTS choice needs the real suite
command (no suite yet — record the `none` line and say completion is then a
claim, not a check), and GIT `read-only` makes COMMITS moot — skip it and
record `- COMMITS: none — GIT is read-only.`

## 3. Scaffold — never overwrite

Create each of these from `${CLAUDE_PLUGIN_ROOT}/templates/`, skipping and
reporting anything that already exists (report it as `kept`):

- `AGENTS.md` from `templates/AGENTS.md`, with the recorded rule lines
  replacing the placeholder comment under `## Project rules`
- `CLAUDE.md` from `templates/CLAUDE.md` (one line: `@AGENTS.md`)
- `.cursor/rules/moltke.mdc` from `templates/cursor_rules`
- `adocs/specs.md`, `adocs/plan.md`, `adocs/status.md`, `adocs/decisions.md`
  from `templates/adocs/`
- empty `adocs/plan_todo/`, `adocs/plan_current/`, `adocs/plan_done/`,
  `adocs/audit/` (add `.gitkeep`)
- offer `.moltke.local.md` from `templates/moltke_local.md` for machine-local
  notes; if taken, add `.moltke.local.md` to `.gitignore`

Two of these are entry points, and a kept file is not a wired one. If an
existing `CLAUDE.md` lacks an `@AGENTS.md` reference, offer to append that
one line — append, never rewrite — and report it as `wired` rather than
`kept`; the same offer for an existing `.cursor/rules/moltke.mdc` that does
not reference the ruleset. Skipping this leaves sessions reading the old
entry point and never seeing the ruleset: nothing fails and nothing warns,
the workflow is simply not in force.

Then record the adoption as the first decision in `adocs/decisions.md`:
`DEC-001`, the chosen rules in one entry, and any option the user rejected
with a reason worth keeping.

## 4. First plan

The scaffold leaves `specs.md` and `plan.md` holding comments — the two
things this skill cannot write for the user. Do this now, in the same
conversation, unless the user asks to stop:

1. **Prime directive.** One sentence: the property this project must never
   violate. Propose one from what the repository already does and let the
   user correct it — a wrong proposal beats a blank page.
2. **Invariants.** `INV-1`, `INV-2`, ... each a testable property, not an
   aspiration; three to seven is a normal first set. An invariant nothing
   could check is a wish — say so and reword it.
3. **First plan.** Discuss order before writing: correctness and the things
   everything else rests on come first. Write the description paragraph at
   the top of `plan.md`.
4. **Step files.** Create one per planned step in `adocs/plan_todo/`, by
   hand, in the format `AGENTS.md` shows — ids from S001 in creation order —
   and list each in `plan.md`'s Open list. `accepts` is the field that
   matters: it is what completion is judged against.
5. **Decisions.** Scope, order, and anything the user chose against — into
   `decisions.md` while it is fresh.
6. **Status.** Fill `status.md`: nothing done, nothing in progress, next is
   the first Open entry.
7. **Commit**, per the COMMITS rule just recorded.

Starting work is a separate turn: move the first step to `plan_current/`,
set `author:`, begin.

## Notes

- Adopting a repository with work already in flight is a manual exercise:
  scaffold, then move the existing plan into the `adocs/` files by hand.
- The catalog above is also the reference for `/moltke:rules` when it
  re-asks a topic; keep wording changes here.
