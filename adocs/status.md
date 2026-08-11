# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-11 by `moltke --step status`.

- Last done: S118
- In progress: none
- Next: no steps left in plan.md
- Blocked: none
- Parked:
  - review runs on the S108 three-tier model: fast check per step, audit by
    proposal or on demand. The sixth audit (2026-08-11) closed all seven
    2026-08-09 findings on re-run evidence and its own six findings are fixed
    (S112-S117); none remain open. DEC-041's stop stands: no audit is scheduled,
    and the next one is a proposal or an ask away.
  - the installed plugin runs from the plugin cache, not from this checkout;
    fixes land live only after a version bump plus
    `claude plugin install moltke@moltke`. 0.9.0 is committed; S112-S117 wait
    for the next bump.
  - DEC-020: the repository root is also the plugin root, so `adocs/`, `tests/`,
    `AGENTS.md`, and `CLAUDE.md` ship inside every install. Escape hatch is a
    `plugin/` subdirectory move.
  - GitHub configuration — visibility, remotes, branches, protection, pushes —
    is Max's own; the agent commits and never pushes (DEC-014).
