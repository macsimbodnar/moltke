# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-11 by `moltke --step status`.

- Last done: S105
- In progress: none
- Next: S106
- Blocked: none
- Parked:
  - **Complete and stable at 0.8.0, awaiting new orders (DEC-041, 2026-08-09).**
    The plan is empty and that is the finished state, not a gap: 101 steps done,
    444 tests green, `--validate`, `--audit list` and `--audit check` all exit 0.
    Do not start work here without an instruction.
  - the audit loop was stopped by decision rather than by DEC-035's severity rule
    (DEC-041). The seven `2026-08-09_adversarial` findings stay `planned`, not
    `closed`: every one has a completed step and red-first tests, and what is
    missing is the independent re-measurement a re-run would give. That is the
    honest state and is left visible on purpose. Restarting is one command,
    `bin/moltke.py --audit new adversarial` plus a fresh reviewer spawn.
  - the installed plugin runs from the plugin cache, not from this checkout, so
    editing `bin/moltke.py` here changes nothing hooks execute until
    `claude plugin install moltke@moltke` runs again. 0.8.0 is committed here and
    the installed cache is 0.7.0 until that runs (S059, DEC-041).
  - DEC-020: the repository root is also the plugin root, so `adocs/`, `tests/`,
    `AGENTS.md`, and `CLAUDE.md` ship inside every install. Escape hatch is a
    `plugin/` subdirectory move.
  - GitHub configuration — visibility, remotes, branches, protection, pushes — is
    Max's own; the agent commits and never pushes (DEC-014).
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was
    agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - DEC-035 sets when the audit loop ends: a re-run with no high and no medium
    stops it. The 2026-08-08 re-run does not qualify — one high, five medium.
