# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-08 by `moltke --step status`.

- Last done: S057
- In progress: none
- Next: S028
- Blocked: none
- Parked:
  - S012 completed 2026-08-06 on two machines. Five of its six clauses passed; the reviewer write fence failed, proven by a live plugin spawn writing outside `adocs/audit/` unblocked. That is finding F02 and step S016, which must re-probe with a live spawn rather than synthetic payloads. Until S016 lands, the reviewer is confined by its prompt and not by enforcement.
  - the installed plugin runs from the plugin cache at the version in plugin.json, not from this checkout, so every fix in S014..S026 is inert in live sessions until 0.3.0 is built (S027) and reinstalled. Editing `bin/moltke.py` here changes nothing that hooks execute.
  - DEC-020: the repository root is also the plugin root, so adocs/, tests/, AGENTS.md, and CLAUDE.md ship inside every install. Escape hatch is a plugin/ subdirectory move.
  - plugin.json carries no `repository` URL yet. The repository exists at git@github.com:macsimbodnar/moltke.git; now planned as part of S026 (audit finding F13).
  - the 2026-08-06 adversarial audit is triaged: 14 findings, all `planned`, one step each in S014..S026, closed out by S027. DEC-022 (reviewer fence gives way to reconciliation), DEC-023 (optional `test_command`) and DEC-024 (worklog secrets detected, not redacted) were decided in that planning session.
  - GitHub configuration (visibility, remotes, branches, protection, pushes) is Max's own; agent commits only (DEC-014). DEC-002 is confirmed: master is pushed to origin.
  - GitHub repository rename and local directory rename to `moltke` are Max's own (DEC-014, DEC-015).
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - after a few weeks of real use: does `status.md` earn its place (specs open item)
