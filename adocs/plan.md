# Plan

Build the `moltke` Claude Code plugin: a document-driven development workflow
giving an agent durable, cross-session, cross-tool memory of a project,
distributed as a git repository plus a plugin marketplace entry, enforced by
hooks in marked repositories. Spec: `adocs/specs.md`.

This repository self-hosts the workflow (DEC-012). S001 was worked by hand;
from S002 onward the workflow enforces itself.

Order lives here and nowhere else (DEC-008). Step detail lives in the step files.

Correctness defects jump the queue (§3), so the 2026-08-07 findings are ordered
by severity ahead of the remaining feature work. Step ids belong in the numbered
list below and nowhere else in this file: the derived next step is the first id
in document order, so an id mentioned in prose above the list becomes the next
step instead.

105. S107  the ruleset tells agents to look up, not to read everything
106. S108  review has three tiers: fast check by habit, full audit by consent
107. S109  a machine-local instructions file that the tool creates and injects
108. S110  a project-rules override section, and 0.9.0 ships the batch
109. S111  fix the five findings of the batch's own fast check
