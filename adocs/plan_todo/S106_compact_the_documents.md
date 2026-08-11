id:         S106
goal:       the always-read documents hold current state, not history
accepts:    adocs/specs.md is rewritten to current state only — prime directive,
            the invariants in their current wording with retired numbers marked,
            layout, the surface table, non-goals — at roughly 10 KB, with the
            dated inline notes deleted; their narrative already lives in each
            step's done: stamp and commit message.
            adocs/decisions.md keeps all entries with stable ids but compressed:
            a one-line-per-entry index at the top, then per entry the decision and
            a one-line why; target roughly 20 KB. Every finding id that marks an
            audit finding accepted is retained, so --audit list still exits 0.
            adocs/worklog.md is truncated to a stub pointing at git history.
            After the compaction: --validate exit 0, --audit list exit 0, the full
            suite green, and the measured always-read set (AGENTS.md, status.md,
            plan.md, specs.md, decisions.md) is at or under 50 KB, recorded
            before/after in the recap.
touches:    adocs/specs.md; adocs/decisions.md; adocs/worklog.md
excludes:   adocs/testing.md, which is never read into context and whose rows
            INV-5 requires per done step; the audit reports, which are evidence;
            any code change, which is S105's job
decisions:  DEC-042
closes:
blocks:
paused_by:
done:
