# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-08 by `moltke --step status`.

- Last done: S078
- In progress: none
- Next: S059
- Blocked: none
- Parked:
  - `2026-08-06_adversarial-F02`, the reviewer write fence, is the one finding of
    that run still `planned`. S016 changed the match and the suite covers it, but
    closing it needs a live plugin subagent spawn, which no audit can produce from
    inside itself. That clause belongs to S059.
  - the installed plugin runs from the plugin cache at the version in
    `plugin.json`, not from this checkout. 0.5.0 and 0.6.0 are both committed and
    neither was ever installed, so every fix from S045 onward is inert in live
    sessions until `claude plugin install moltke@moltke` runs. Editing
    `bin/moltke.py` here changes nothing that hooks execute. S059 verifies it.
  - DEC-020: the repository root is also the plugin root, so `adocs/`, `tests/`,
    `AGENTS.md`, and `CLAUDE.md` ship inside every install. Escape hatch is a
    `plugin/` subdirectory move.
  - GitHub configuration — visibility, remotes, branches, protection, pushes — is
    Max's own; the agent commits and never pushes (DEC-014).
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was
    agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - DEC-035 sets when the audit loop ends: a re-run with no high and no medium
    stops it. The 2026-08-08 re-run does not qualify — one high, five medium.
