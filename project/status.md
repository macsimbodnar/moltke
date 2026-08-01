# Status

Convenience view, rewritten at end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins (AGENTS.md §1).

Updated: 2026-08-01, S005 completion.

- Last done: S005 — all five hook modes implemented and wired in `hooks/hooks.json`, contract verified against live docs; suite 49/49
- In progress: none (`plan_current/` empty)
- Next: S006 — `init` skill and the `templates/` tree
- Blocked: none
- Parked:
  - GitHub configuration (visibility, remotes, branches, protection, pushes) is Max's own; agent commits only (DEC-014). DEC-002 confirmation resolves when Max pushes.
  - GitHub repository rename and local directory rename to `moltke` are Max's own (DEC-014, DEC-015).
  - INV-11 vs `--scaffold`: scaffolding must run in unmarked repos; carve-out to be recorded in S006 (noted in the S006 step file).
  - hooks are wired but inert here until the plugin is installed (S010); until then enforcement is `--validate` by hand.
  - after a few weeks of real use: does `status.md` earn its place (specs open item)
