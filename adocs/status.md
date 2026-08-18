# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-18 by `moltke --step status`.

- Last done: S137
- In progress: none
- Next: S132
- Blocked: none
- Parked:
  - 0.12.0 is installed (2026-08-18, sha 6ca6455) and is what the live hooks run;
    master and origin/master agree at that sha. S139 is therefore part done: the
    version is verified, the live Monitor refusal and a SessionStart carrying
    watch state are not — this session's SessionStart ran 0.11.0.
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
