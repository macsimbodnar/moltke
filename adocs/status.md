# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-06 by `moltke --step status`.

- Last done: S013
- In progress: S012 install verification: marketplace add, plugin install, hooks firing in a live session, second machine
- Next: S012
- Blocked: none
- Parked:
  - S012 (install verification) is Max's: the agent changes no GitHub or Claude Code configuration (DEC-014, DEC-019). Partly verified 2026-08-02 from an installed plugin: marketplace add from the git URL, install of moltke@moltke 0.1.0 at sha 0b5c96b, all three skills resolving, and SessionStart, UserPromptSubmit, PreToolUse and PostToolUse observed firing. Still open: the Stop hook's refusals, the reviewer fence under a real subagent spawn, and a second machine.
  - the installed plugin is pinned at the version in plugin.json and runs from the plugin cache, not this checkout. Max reports installing on two machines (2026-08-06); what that run exercised is not yet recorded, so the S012 stamp is still pending. Contradicting evidence in this checkout: none of the 2026-08-06 session's prompts reached `adocs/worklog.md`, which is audit finding F14 and means the live hooks here were still enforcing 0.1.0's rules against `project/`.
  - DEC-020: the repository root is also the plugin root, so adocs/, tests/, AGENTS.md, and CLAUDE.md ship inside every install. Escape hatch is a plugin/ subdirectory move.
  - plugin.json carries no `repository` URL yet. The repository exists at git@github.com:macsimbodnar/moltke.git; now planned as part of S026 (audit finding F13).
  - the 2026-08-06 adversarial audit is triaged: 14 findings, all `planned`, one step each in S014..S026, closed out by S027. DEC-022 (reviewer fence gives way to reconciliation), DEC-023 (optional `test_command`) and DEC-024 (worklog secrets detected, not redacted) were decided in that planning session.
  - GitHub configuration (visibility, remotes, branches, protection, pushes) is Max's own; agent commits only (DEC-014). DEC-002 is confirmed: master is pushed to origin.
  - GitHub repository rename and local directory rename to `moltke` are Max's own (DEC-014, DEC-015).
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - after a few weeks of real use: does `status.md` earn its place (specs open item)
