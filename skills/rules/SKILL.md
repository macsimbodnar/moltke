---
name: rules
description: Show, add, change, or drop the Project rules recorded in AGENTS.md - the per-repository answers from the init interview. Use when the user wants to see the rules or change what agents may do here (git powers, subagents, tests, docs, cadence).
---

# Project rules

The rules live in `AGENTS.md` under `## Project rules`: one line per rule,
stable id first. This skill edits that section and nothing else in the file.

- **Show**: read the section back verbatim. If it is missing, the workflow is
  not set up here — point at `/moltke:init` and stop.
- **Change**: rewrite the rule's line in place, keeping its id. For a catalog
  topic — GIT, AGENTS, TESTS, PLAN, DOCS, REVIEW, AUDIT, DEPS, COMMITS —
  re-ask that one question from the catalog in
  `${CLAUDE_PLUGIN_ROOT}/skills/init/SKILL.md` rather than inventing new
  phrasing; the user's own wording still wins.
- **Add**: a new line with a new id — short, uppercase, not colliding with
  the catalog ids. One rule per line; a rule that needs a paragraph is two
  rules or a specs.md entry.
- **Drop**: delete the line — non-catalog ids only. Catalog topics are
  changed, never dropped: the base ruleset reads PLAN, TESTS, DOCS, REVIEW,
  and COMMITS by id, so a dropped line leaves it referencing an undefined
  rule where the catalog has a recorded none/off option — turning a topic
  off is a Change to that option.

Every add, change, or drop also gets a `decisions.md` entry — heading,
`Tags: rules`, `Decision:` the new line (or what was dropped) and by whom,
`Why:` one line. A ruleset changed without a decision trail is one nobody
can trust the next session.

Then commit per the COMMITS rule — including when COMMITS itself is what
changed; the cadence that applies is the one just recorded.
