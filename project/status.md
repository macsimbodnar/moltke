# Status

Convenience view, rewritten at the end of every work turn. The filesystem beats
this file: on disagreement, `plan_current/` wins.

Updated: 2026-08-02 by `moltke --step status`.

- Last done: S011
- In progress: none
- Next: S012
- Blocked: none
- Parked:
  - S012 (install verification) is Max's: the agent changes no GitHub or Claude Code configuration (DEC-014, DEC-019). Until it passes, the hooks and skills here are wired but never exercised by a live session.
  - DEC-020: the repository root is also the plugin root, so project/, tests/, AGENTS.md, and CLAUDE.md ship inside every install. Escape hatch is a plugin/ subdirectory move.
  - plugin.json carries no `repository` URL yet; add it when the GitHub repository exists.
  - GitHub configuration (visibility, remotes, branches, protection, pushes) is Max's own; agent commits only (DEC-014). DEC-002 confirmation resolves when Max pushes.
  - GitHub repository rename and local directory rename to `moltke` are Max's own (DEC-014, DEC-015).
  - hooks are wired but inert here until the plugin is installed (S010); until then enforcement is `--validate` by hand.
  - DEC-018 (thin Cursor pointer despite native `AGENTS.md` support) was agent-chosen as low-stakes; reversible by deleting `templates/cursor_rules`.
  - after a few weeks of real use: does `status.md` earn its place (specs open item)
