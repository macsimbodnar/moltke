id:         S006
goal:       init skill and the templates/ tree
accepts:    running it twice is idempotent; declining writes {"enabled": false} and is durable across sessions; a repository with an existing AGENTS.md is never overwritten without asking; scaffolding writes AGENTS.md, CLAUDE.md, the Cursor pointer, .moltke.json, and a populated project/; templates carry no project-specific content (DEC-002); Cursor rules format verified against live docs
touches:    skills/init/, templates/
decisions:  DEC-002, DEC-003, DEC-005
note:       resolve INV-11 vs --scaffold, surfaced in S002: scaffolding must run in unmarked repos, but INV-11 says every mode exits 0 without a marker; record the carve-out in specs and decisions.md
done:       2026-08-01 suite green 61/61; red observed (6 failures, 3 errors) before implementation; end-to-end scaffold of a throwaway repo verified, which caught the phantom-next-step defect (regression test added, red observed, fixed); README and MANUAL checked, absent by plan (S011)
