# Plan

Build the `moltke` Claude Code plugin: a document-driven development workflow
giving an agent durable, cross-session, cross-tool memory of a project,
distributed as a git repository plus a plugin marketplace entry, enforced by
hooks in marked repositories. Spec: `adocs/specs.md`.

This repository self-hosts the workflow (DEC-012). S001 was worked by hand;
from S002 onward the workflow enforces itself.

Order lives here and nowhere else (DEC-008). Step detail lives in the step files.

1. S001  scaffold this repository against its own conventions, seed decisions DEC-001 to DEC-012
2. S002  `moltke.py` skeleton, marker parsing, `--validate` mode, broken-fixture test harness
3. S003  invariants 1 to 7, red-first, one test each
4. S004  invariants 8 to 10
5. S005  hooks wiring, all five events, verified against live docs
6. S006  `init` skill and the `templates/` tree
7. S007  `step` skill
8. S008  `adversarial_reviewer` subagent and `audit` skill
9. S009  golden test over the `moltke` CLI surface, plus the test asserting `AGENTS.md` and `templates/AGENTS.md` are identical
10. S010  plugin manifest and marketplace entry, verified statically (DEC-019 moved install checks to S012)
11. S011  README and MANUAL
12. S012  install verification: marketplace add, plugin install, hooks firing in a live session, second machine
13. S013  adocs rename
