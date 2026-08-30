# Status

Convenience view, rewritten by hand at the end of any turn that changed plan
state. The filesystem beats this file: on disagreement, `plan_current/` wins
and this file is rewritten to match it.

Updated: 2026-08-30 by hand (the .3 round closed by Max, no audit re-run).

- Last done: S179 — the 0.x archive branch is lost; DEC-070 records it and
  the parked note stops claiming otherwise
- In progress: none
- Next: nothing planned. The .3 re-run's round (S174-S179) is done and
  closed — Max declined a closing audit re-run (AUDIT is on-demand only).
  Open call: ship the round as 1.1.1 or wait. 1.1.0 is pushed, tagged on
  origin, and installed in the config root.
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
