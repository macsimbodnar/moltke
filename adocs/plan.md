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
14. S014  prompt logging never fails silently
15. S015  Stop's recap gate fires in a live session
16. S016  reviewer fence matches the scoped agent_type
17. S017  --audit check reconciles what an audit changed
18. S030  INV-8 covers decisions.md only; the worklog is convention, not enforcement
19. S018  plan_done and append-only immutability survives a commit
20. S019  fenced guidance never discharges a finding
21. S020  an audit can be re-run the same day
22. S021  optional test_command gate on --step done
23. S022  worklog secret-shape check runs in the suite
24. S023  surface guard covers skills, hooks, and marker keys
25. S024  a plan.md id with no step file is a violation
26. S025  documented exit-code semantics match the code
27. S026  documentation drift pass
28. S027  bump 0.3.0, re-run the audit, close findings
Correctness defects jump the queue (§3), so the 2026-08-07 findings are ordered
by severity ahead of the remaining feature work. Step ids belong in the numbered
list below and nowhere else in this file: the derived next step is the first id
in document order, so an id mentioned in prose above the list becomes the next
step instead.

29. S045  plan order comes from the list, not from prose that happens to name an id
30. S034  a committed immutability violation has a legal way back to green
31. S046  INV-8 catches a committed rewrite of text appended after the first commit
32. S035  moltke works in a linked worktree and a submodule
33. S033  an unbalanced code fence cannot hide content from a scanner
34. S032  --audit check sees a change the run commits
35. S038  a malformed test_command refuses completion instead of disabling the gate
36. S039  status.md staleness is judged on the whole file, not one line
37. S037  the Stop recap gate stops treating .claude-plugin/ as not-source
38. S036  --audit check does not blame the plugin's own worklog writes on the reviewer
39. S041  the reviewer fence normalises paths before matching
40. S040  an audit type cannot write outside adocs/audit/
41. S042  the test_command refusal obeys the documented stream mapping
42. S044  bump 0.4.0, re-run the audit, close the 2026-08-07 findings
43. S047  the Stop deadlock waiver cannot become an off switch
44. S048  INV-3 and plan_order agree on what listed in plan.md means
45. S049  two unclosed fences cannot hide a finding
46. S050  a renamed file does not slip past either Stop gate
47. S052  --step does not traceback in a marked repository without adocs/
48. S053  the Stop deadlock cap exists in a marked repository without git
49. S051  MANUAL stops claiming the two-unclosed-fence hole is fixed
50. S054  INV-8's enforced rule and its stated rule agree
51. S055  INV-13 counts the markers strip_guidance actually sees
52. S056  the worklog exemption does not hand the reviewer a silent channel
53. S057  the reviewer agent and audit skill state where the fence stops
54. S028  init drives a guided planning phase after scaffolding
55. S029  init handles a repo already initialized on another machine
56. S031  target repositories inherit the worklog secret check, not just moltke's own suite
