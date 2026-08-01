# Status

Convenience view, rewritten at end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins (AGENTS.md §1).

Updated: 2026-08-01, S004 completion.

- Last done: S004 — INV-8..INV-10 implemented red-first; all ten invariants now live in `bin/moltke.py --validate`; suite 33/33
- In progress: none (`plan_current/` empty)
- Next: S005 — hooks wiring, all five events, verified against live docs
- Blocked: none
- Parked:
  - GitHub configuration (visibility, remotes, branches, protection, pushes) is Max's own; agent commits only (DEC-014). DEC-002 confirmation resolves when Max pushes.
  - GitHub repository rename and local directory rename to `moltke` are Max's own (DEC-014, DEC-015).
  - INV-11 vs `--scaffold`: scaffolding must run in unmarked repos; carve-out to be recorded in S006 (noted in the S006 step file).
  - after a few weeks of real use: does `status.md` earn its place (specs open item)
