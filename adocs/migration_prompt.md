# Migration prompt: 0.x to 1.x

Operator note, not shipped documentation — it lives in `adocs/` so it travels
in git and can be copy-pasted on any machine (the product's own migration
notes are MANUAL's Migrating section). moltke 1.0 replaced the enforcement
product with rules (DEC-062); a 0.x repository keeps its `adocs/` history and
plan unchanged, and what migrates is the ruleset, a handful of dead files,
and the shape of `plan.md`. Two layers, in this order or the reverse — the
repository half works with or without the plugin installed.

## 1. The machine: update the plugin

Once per Claude config root that has moltke (roots are `~/.claude` for the
CLI and whatever `CLAUDE_CONFIG_DIR` points at for other clients; scope is
per install):

```
claude plugin update moltke@moltke
```

For a root that also holds a project-scope install, additionally, from the
project directory:

```
claude plugin update moltke@moltke --scope project
```

**This is the point of no return for the whole root**: hooks vanish for
every 0.x repository in it at once, migrated or not, and the
`--step`/`--validate`/`--watch` commands go with them. 0.13.0 and 1.0.0
cannot coexist in one root, so update when you are ready to migrate the
repositories that depended on enforcement.

## 2. Each repository: the agent prompt

Paste the block below to an agent working in the repository. Fill
`<MOLTKE_TEMPLATES>` first: the `templates/` directory of your moltke
checkout, or of the installed plugin cache
(`<config root>/plugins/cache/moltke/moltke/<version>/templates`).

````markdown
Migrate this repository's moltke setup from v0.x (enforcement) to v1 (rules
only). The v1 ruleset template is <MOLTKE_TEMPLATES>/AGENTS.md — read it from
there. Do not touch adocs/plan_done/, adocs/audit/, or any step currently in
adocs/plan_current/ — history and in-flight work survive migration unchanged.

1. Harvest before deleting. Read and note:
   - .moltke.json: `test_command`, `plan_active_max`, `surface_guard`
   - AGENTS.md: any custom lines in its `## Project rules` section

2. Replace AGENTS.md with the v1 template, then fill its `## Project rules`
   section with these lines (translate the harvested values where marked):
   - GIT: commit freely; never push — the user pushes.
   - AGENTS: subagents allowed freely.
   - TESTS: the suite is green before a step is marked done (<test_command>);
     a defect gets a failing test before its fix.
     (no test_command in the marker → "- TESTS: no automated suite — each
     done: stamp says what was verified by hand.")
   - PLAN: one active (non-paused) step per agent. (<plan_active_max> if not 1)
   - DOCS: README and MANUAL checked at every step completion.
     (drop MANUAL from the line if the repo has none)
   - REVIEW: fast check after each completed step.
   - AUDIT: propose a full audit on real risk (security-touching, public
     surface, long unaudited stretch); the user accepts or parks it.
   - DEPS: never add a dependency without asking; state what it buys and
     what it costs.
   - COMMITS: commit at each completed step and at any plan change.
   Append the harvested custom lines verbatim. If the harvested
   `surface_guard` was `cli`, `api`, or `both`, add: "- SURFACE: refresh the
   golden test only after specs and the docs describe the change."
   Show the finished rule list to the user and apply corrections before
   moving on.

3. Cleanup:
   - delete .moltke.json (nothing reads it in v1)
   - remove the moltke lines from .gitattributes (union merges for
     adocs/testing.md and adocs/status.md); delete the file if nothing else
     is in it
   - adocs/testing.md left the layout: ask the user keep-or-delete
   - rm -rf .git/moltke_watch .git/moltke_stop_state.json
     .git/moltke_audit_baseline.json (all three of 0.x's git-dir artifacts)
   - if .git/info/exclude lists .moltke.local.md, move that line to .gitignore
   - keep CLAUDE.md, .cursor/rules/moltke.mdc, .moltke.local.md as they are

4. Reshape adocs/plan.md to the v1 sections, content unchanged: open entries
   as a numbered list under `## Open`, the last five completed under
   `## Done recently`, prose paragraph on top stays.

5. Record and commit: append a decisions.md entry (next free DEC id, ids
   never reused) — "migrated to moltke v1: rules recorded, enforcement files
   removed", naming anything chosen differently from the table above. One
   commit for the whole migration. Never push.

6. Verify and report: AGENTS.md base sections match the template byte-for-byte
   (diff them), status.md and plan.md orient a cold reader, no .moltke.json
   remains, git status clean after the commit. Expect no hook output anywhere
   — v1 has no hooks; that is correct, not broken. Report the rule lines
   recorded and every file deleted.
````

Two calibrations are baked into the prompt, flip them per repository before
pasting if they are wrong for it: AUDIT is set to propose-on-risk (0.x's
behaviour; `on demand only` is the other option) and DEPS to ask-first. The
agent shows the full rule list before applying, so corrections have a
natural moment. Steps mid-flight in `plan_current/` are deliberately left
alone: migration changes the rules, not the plan.
