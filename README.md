# moltke

A Claude Code plugin that gives an agent durable memory of a project: what to
do next, why past choices were made, what has been audited. State lives in
tracked files; the rules for keeping it current live beside it. Nothing is
enforced — v1 is rules agents follow, not hooks that police them (DEC-062).

Moltke commanded armies he could not see by writing orders that survived his
absence. Same problem, smaller scale.

For installing and using it, see [MANUAL.md](MANUAL.md). This file is for
working on moltke itself.

## Layout

```
.claude-plugin/plugin.json       manifest: name, explicit version
.claude-plugin/marketplace.json  single-plugin marketplace entry
skills/init/SKILL.md             the interview: records Project rules, scaffolds, elicits the first plan
skills/rules/SKILL.md            show, add, change, drop Project rules
skills/audit/SKILL.md            evidence-first audit loop around the reviewer
agents/adversarial_reviewer.md   auditor: reads anything, writes only its own report and tests
templates/                       what init copies into a target repository
AGENTS.md                        the live ruleset; templates/AGENTS.md is its shipped copy
adocs/                           moltke's own workflow state (it uses itself)
```

The plugin is markdown only: no executable code, no hooks, no dependencies.
`adocs/` is not part of the plugin's behaviour — it is this repository's own
plan, decisions, and audit history, because moltke is the first project to
use moltke. Read `adocs/specs.md` before changing anything.

## Verify

There is no suite. A change is verified by dogfooding: follow
`skills/init/SKILL.md` by hand in a scratch repository and check that what it
produces matches what `AGENTS.md` and `MANUAL.md` claim. Keeping
`templates/AGENTS.md` and the root `AGENTS.md` base sections identical is part
of every change that touches either.

## Ship

A release is a deliberate act, in this order:

1. bump `version` in `.claude-plugin/plugin.json`
2. commit on `master` — the bump commit is the release commit (agents
   commit; Max pushes)
3. tag the release commit with an annotated `v<version>`
   (`git tag -a v<version>`), after every release-bound change has landed —
   the tag, not the manifest, names the released tree, and a pushed tag
   never moves (DEC-069)
4. push commits and tag together (`git push --follow-tags`)
5. `claude plugin update moltke@moltke` in each Claude config root (and each
   scope) that has it installed — updates compare `version` and nothing else

The 0.x enforcement product — `bin/moltke.py`, hooks, the suite — is git
history behind the 1.0 pivot (DEC-062).
