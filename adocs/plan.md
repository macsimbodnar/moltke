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
48. S051  MANUAL stops claiming the two-unclosed-fence hole is fixed
49. S054  INV-8's enforced rule and its stated rule agree
50. S055  INV-13 counts the markers strip_guidance actually sees
51. S056  the worklog exemption does not hand the reviewer a silent channel
52. S057  the reviewer agent and audit skill state where the fence stops
53. S028  init drives a guided planning phase after scaffolding
54. S029  init handles a repo already initialized on another machine
55. S031  target repositories inherit the worklog secret check, not just moltke's own suite
56. S058  bump 0.5.0, re-run the audit, close the findings it no longer reports
57. S060  --stop enforces instead of crashing when a plan_done/ arrival is not on disk
58. S061  the Stop waiver clock does not freeze when prompt logging fails
59. S062  --step done refuses before it writes, so a failed completion leaves INV-1 satisfied
60. S063  INV-13 scans every file strip_guidance is pointed at, specs.md included
61. S064  one decode policy for every file moltke reads
62. S065  MANUAL says which commit an immutability violation names
63. S066  bump 0.6.0, re-run the audit, close the findings it no longer reports
64. S067  the Stop backstop still counts a turn and still prints what it found
65. S079  a --roadmap mode prints where the plan is, as one timeline strip
66. S068  --session-start always emits its JSON channel
67. S069  the stamp gate judges step files, not every path under plan_done/
68. S070  --step done leaves no state the CLI cannot clear
69. S071  INV-7's remedy for a rename is a command that works
70. S072  the structural guard against an unguarded scanner can fire again
71. S073  the -uall porcelain read has a test that fails without it
72. S074  tests/test_s033_fences.py runs every class when invoked directly
73. S075  INV-14 names the cause it can prove and a remedy that works
74. S076  --audit's exit codes match the documented table, and a write failure says write
75. S077  --audit check shares one definition of newly here
76. S078  INV-16 compares the two sides instead of testing both for emptiness
77. S080  a Stop state file that cannot be written does not wedge the session
78. S081  every git-derived check works when the marked root is below the git top level
79. S082  --step block refuses on an already-paused parent instead of breaking INV-1
80. S083  --step new and --step block leave nothing behind when they refuse
81. S084  INV-7's rename remedy is a command that restores the file
82. S085  testing.md is read through strip_guidance like every other scanner input
83. S086  --roadmap exits as its documentation says
84. S087  a malformed hook payload refuses instead of raising
85. S088  --step new and --step block refuse a name outside [A-Za-z0-9_]+
86. S089  --step done and --step start refuse when the destination file already exists
87. S090  a paused_by naming no step file is reported and clearable
88. S091  --scaffold and --decline refuse instead of tracebacking, and leave no half-applied marker
89. S092  git_prefix is computed once per root, not once per path
90. S093  INV-8's high-water-mark remedy prints the git blob spec, not the root-relative path
91. S094  --step status carries an unindented Parked list through, or refuses
92. S059  verify the installed release in a live session, after reinstall
93. S095  multiline step fields
94. S096  bump 0.7.0, re-run the audit, close the findings it no longer reports
95. S097  allocating a step id no scanner can read is a refusal, not a success
96. S098  a pause has to resolve: no step pauses itself, and no cycle of pauses
97. S099  a written field value cannot land in a shape the parser drops
98. S100  the Parked block is carried through as verbatim as the docs say
99. S101  a malformed agent_type is fenced, not mistaken for the main thread
100. S102  the two documented refusals match what the code does
101. S103  a step file's id: field agrees with its filename, or does not exist
102. S104  bump 0.8.0 and stop the audit loop by decision
103. S105  the tool stops enforcing document history, so the documents can shrink
104. S106  the always-read documents hold current state, not history
105. S107  the ruleset tells agents to look up, not to read everything
106. S108  review has three tiers: fast check by habit, full audit by consent
107. S109  a machine-local instructions file that the tool creates and injects
108. S110  a project-rules override section, and 0.9.0 ships the batch
