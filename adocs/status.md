# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-09 by `moltke --step status`.

- Last done: S099
- In progress: none
- Next: S100
- Blocked: none
- Parked:
  - the installed plugin runs from the plugin cache, not from this checkout, so
    editing `bin/moltke.py` here changes nothing hooks execute until
    `claude plugin install moltke@moltke` runs again. As of 2026-08-09 the cache
    is 0.6.0 at `gitCommitSha` `c2e6ad3` and its `bin/moltke.py` is byte-identical
    to this tree, so what runs is what is committed — but that holds only until
    the next commit lands here (S059,
    `adocs/audit/2026-08-09_verification.md`).
  - DEC-020: the repository root is also the plugin root, so `adocs/`, `tests/`,
    `AGENTS.md`, and `CLAUDE.md` ship inside every install. Escape hatch is a
    `plugin/` subdirectory move.
  - GitHub configuration — visibility, remotes, branches, protection, pushes — is
    Max's own; the agent commits and never pushes (DEC-014).
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was
    agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - DEC-035 sets when the audit loop ends: a re-run with no high and no medium
    stops it. The 2026-08-08 re-run does not qualify — one high, five medium.
