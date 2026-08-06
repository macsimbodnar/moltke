id:         S012
goal:       install verification: marketplace add, plugin install, hooks firing in a live session, second machine
accepts:    `claude plugin marketplace add <repo>` and `claude plugin install moltke@moltke` succeed; `/moltke:init`, `/moltke:step`, `/moltke:audit` resolve; the five hooks fire in a live session (SessionStart prints the stack, a write into plan_done/ is blocked, Stop refuses a stale status.md); the adversarial_reviewer subagent is spawnable and its write fence holds; the same install works on a second machine; DEC-002 (public repository) confirmed before the first push
touches:    nothing in the repository; this verifies an installed artefact
excludes:   code changes — anything found here becomes its own step
decisions:  DEC-002, DEC-014, DEC-019
closes:
blocks:
paused_by:
owner:      Max. The agent changes no GitHub or Claude Code configuration (DEC-014); it supplies the commands and reads back the results.
done:      2026-08-06. Verified live on two machines against the adocs/ build: marketplace add, plugin install, all three skills resolving, and all five hook events firing (SessionStart stack, UserPromptSubmit verbatim log, PreToolUse both refusals, PostToolUse non-blocking INV-3, Stop refusing a stale status.md). The reviewer write fence was verified NOT to hold: a real plugin spawn wrote outside adocs/audit/ unblocked. Recorded as F02, fixed by S016, which re-probes with a live spawn. README and MANUAL checked: MANUAL's two fence entries narrowed to the confirmed defect and the deliberate Bash gap (DEC-022); the live-hook entry narrowed to F01 and F14.
