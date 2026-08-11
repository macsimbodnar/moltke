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

111. S113  the pre-write rules match paths the way the filesystem does
112. S114  a pause that already resolved is reported and clearable
113. S115  --step unpause says what actually happened
114. S116  --help names every operation the parser accepts
115. S117  the decisions index matches the entries, newest last
