# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-18 by `moltke --step status`.

- Last done: S130
- In progress: none
- Next: S137
- Blocked: none
- Parked:
  - 0.11.0 is installed (2026-08-13, sha 7ea76f7) and is what the live hooks run.
    0.12.0 is committed and unshipped: `claude plugin install moltke@moltke`
    before expecting `--watch` or the Monitor lint to exist in a session.
    `--version` tells you which one you are talking to.
  - the merge (DEC-052) could not be a git merge: with both branches' `plan_done/`
    trees as ancestors, INV-6 and INV-7 contradict each other and no resolution
    validates. It is a graft instead, and `watch-primitive-a304293` holds the
    pre-merge tip and its worklog. The branch's plan_done commits can never be an
    ancestor of a green master.
  - whether an arm-time watcher blocker belongs here at all, given DEC-047 retired
    exactly that shape of enforcement, is Max's call and carries a step.
  - DEC-041's audit stop stands: the next full audit is a proposal or an ask
    away; the per-step fast check is the habit in between (DEC-044).
  - DEC-020: the repository root is also the plugin root; `plugin/` subdirectory
    move is the escape hatch.
  - GitHub configuration and pushes are Max's own (DEC-014).
