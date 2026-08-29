# Status

Convenience view, rewritten by hand at the end of any turn that changed plan
state. The filesystem beats this file: on disagreement, `plan_current/` wins
and this file is rewritten to match it.

Updated: 2026-08-29 by hand (S172 completion).

- Last done: S172
- In progress: S171 (release 1.1.0, tagged; paused behind S173)
- Next: S173, then S171 finishes the release
- Blocked: none
- Parked:
  - the 2026-08-18 merge (DEC-052) was a graft, not a git merge;
    `watch-primitive-a304293` holds the pre-merge tip. The INV-6/INV-7
    contradiction that forced the graft retired with DEC-062, but the branch
    stays as the archive of the unmerged line.
  - DEC-020: the repository root is also the plugin root; a `plugin/`
    subdirectory move is the escape hatch if the root gets crowded.
  - pruned on the v1 pivot (S160), deliberately: the two 0.x install-route
    notes, and the DEC-041 audit-stop and DEC-014 git-surface lines, which
    are now the AUDIT and GIT Project rules in AGENTS.md.
