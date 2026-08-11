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

116. S118  bump 0.10.0 so the audit fixes ship
117. S119  --pre-write consults PATH before reading stdin
118. S120  the worklog subsystem is removed (DEC-046)
119. S121  steps are claimed at start and limits count per author (DEC-045)
120. S122  merge semantics and the team story ship with the scaffold (DEC-045)
121. S123  AGENTS.md reissued once - team rules in, trimmed to the operative core
122. S124  INV-13, INV-14, INV-16 retired; stripping stays (DEC-047)
123. S125  the completion ceremony is slimmed (DEC-048)
124. S126  testing.md rows pruned with the plan window
125. S127  plan_steps memoized per process, and --version exists
126. S128  bump 0.11.0 and ship the batch
