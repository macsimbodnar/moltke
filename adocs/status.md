# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-11 by `moltke --step status`.

- Last done: S114
- In progress: none
- Next: S115
- Blocked: none
- Parked:
  - the audit loop is stopped by decision, not by DEC-035's severity rule
    (DEC-041). The seven `2026-08-09_adversarial` findings stay `planned`: each
    has a completed step and red-first tests; what is missing is only the
    independent re-measurement a re-run would give. Restart is one command:
    `bin/moltke.py --audit new adversarial` plus a fresh reviewer spawn.
  - the installed plugin runs from the plugin cache, not from this checkout;
    fixes land live only after a version bump plus
    `claude plugin install moltke@moltke`. Cache is 0.8.0; 0.9.0 ships S105-S110.
  - DEC-020: the repository root is also the plugin root, so `adocs/`, `tests/`,
    `AGENTS.md`, and `CLAUDE.md` ship inside every install. Escape hatch is a
    `plugin/` subdirectory move.
  - GitHub configuration — visibility, remotes, branches, protection, pushes —
    is Max's own; the agent commits and never pushes (DEC-014).
