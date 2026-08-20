# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-20 by `moltke --step status`.

- Last done: S155
- In progress: none
- Next: S156
- Blocked: none
- Parked:
  - two Claude config roots on this machine, each with its own plugin registry and
    its own install (DEC-057), and the two take a release by different routes:
    `~/.claude-work` for the desktop app from a `directory` source on the
    checkout, `~/.claude` for the CLI from the `git` source, which resolves
    against `origin/master`. The directory source's cache is a snapshot, and an
    edit reaches the live hooks only after `version` is bumped **and**
    `claude plugin update moltke@moltke` is run in that root — the update
    compares `version` alone, so without the bump it reports success and copies
    nothing (S155, DEC-061). Scope is per install: a root holding both `user`
    and `project` scope needs the update twice. Machine detail is in
    `.moltke.local.md`; the general rule is in MANUAL's Install section.
  - nothing in a session reports which install is answering, so a stale or absent
    root fails silently — S139 excluded the fix as a behaviour change (DEC-057),
    and it is unstepped. Live as of S155: the two roots now run different
    versions, and no session says which one it is talking to.
  - master is unpushed ahead of origin/master (`b37ed95`, S134); the CLI root runs
    `6ca6455` at 0.12.0, and stays there until master is pushed, because its git
    source cannot see a bump that exists only in the checkout — 0.13.0 shipped
    with that root unreached (DEC-061). Pushes are Max's own. The count was
    written as 2 and was 30 by 2026-08-20 — no number here survives a commit, so
    it is not kept.
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
