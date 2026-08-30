# Status

Convenience view, rewritten by hand at the end of any turn that changed plan
state. The filesystem beats this file: on disagreement, `plan_current/` wins
and this file is rewritten to match it.

Updated: 2026-08-30 by hand (S180 done: 1.1.1 released and tagged).

- Last done: S180 — 1.1.1 released: the .3 re-run round (S174-S179) ships;
  annotated tag v1.1.1 on the release commit
- In progress: none
- Next: nothing planned. Max pushes commits and tag
  (`git push --follow-tags`), then updates each installed config root
  (`claude plugin update moltke@moltke`).
- Blocked: none
- Parked:
  - the 2026-08-18 merge (DEC-052) was a graft, not a git merge, and the
    pre-merge tip is lost: `watch-primitive-a304293` exists neither on
    origin nor anywhere in this clone (DEC-070). The unmerged 0.x line's
    record is `plan_done/`, the audit reports, and DEC-052.
  - DEC-020: the repository root is also the plugin root; a `plugin/`
    subdirectory move is the escape hatch if the root gets crowded.
  - pruned on the v1 pivot (S160), deliberately: the two 0.x install-route
    notes, and the DEC-041 audit-stop and DEC-014 git-surface lines, which
    are now the AUDIT and GIT Project rules in AGENTS.md.
