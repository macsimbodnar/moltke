# Status

Convenience view, rewritten at end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins (AGENTS.md §1).

Updated: 2026-08-01, S006 completion.

- Last done: S006 — `init` skill, full `templates/` tree, `--scaffold` and `--decline`; a scaffolded repo validates clean and blocks nothing on the first turn; suite 61/61
- In progress: none (`plan_current/` empty)
- Next: S007 — `step` skill
- Blocked: none
- Parked:
  - GitHub configuration (visibility, remotes, branches, protection, pushes) is Max's own; agent commits only (DEC-014). DEC-002 confirmation resolves when Max pushes.
  - GitHub repository rename and local directory rename to `moltke` are Max's own (DEC-014, DEC-015).
  - hooks are wired but inert here until the plugin is installed (S010); until then enforcement is `--validate` by hand.
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - after a few weeks of real use: does `status.md` earn its place (specs open item)
