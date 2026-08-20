# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-20 by `moltke --step status`.

- Last done: S153
- In progress: none
- Next: S154
- Blocked: none
- Parked:
  - two Claude config roots on this machine, each with its own plugin registry and
    its own install (DEC-057): `~/.claude` for the CLI, `~/.claude-work` for the
    desktop app. The desktop root installs from a `directory` source pointing at
    the checkout, so its cache is a snapshot and an edit reaches the live hooks
    only after `claude plugin update moltke@moltke` in that root. Machine detail
    is in `.moltke.local.md`; the general rule is in MANUAL's Install section.
  - nothing in a session reports which install is answering, so a stale or absent
    root fails silently — S139 excluded the fix as a behaviour change (DEC-057),
    and it is unstepped.
  - master is unpushed ahead of origin/master (`b37ed95`, S134); the CLI root still
    runs the older `6ca6455`. Pushes are Max's own. The count was written as 2 and
    was 30 by 2026-08-20 — no number here survives a commit, so it is not kept.
  - the merge (DEC-052) could not be a git merge: with both branches' `plan_done/`
    trees as ancestors, INV-6 and INV-7 contradict each other and no resolution
    validates. It is a graft instead, and `watch-primitive-a304293` holds the
    pre-merge tip and its worklog. The branch's plan_done commits can never be an
    ancestor of a green master.
  - DEC-041's audit stop stands: the next full audit is a proposal or an ask
    away; the per-step fast check is the habit in between (DEC-044).
  - DEC-020: the repository root is also the plugin root; `plugin/` subdirectory
    move is the escape hatch.
  - GitHub configuration and pushes are Max's own (DEC-014).
