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
done:      2026-08-11: the always-read documents hold current state, not history (DEC-042). specs.md rewritten 84,637 to 8,413 bytes — prime directive, sixteen invariants in current wording with INV-8 marked retired, layout, the golden-guarded CLI surface table, non-goals; the dated notes are deleted and their narrative lives in step stamps and commit messages. decisions.md compacted 70,505 to 23,258 bytes keeping all 42 entries with stable ids, an index at top, decisions capped to their operative sentences, one-line whys, and every finding id that discharges an accepted audit finding — --audit list exit 0 proves the references held. worklog.md truncated to a stub naming the commit holding its history. status.md's stale Parked claim from DEC-041 rewritten to the current state. Measured always-read set: 180,518 bytes at e22a911 to 49,900 now (~12.5k tokens), under the 50 KB acceptance. Suite 438 OK, --validate green. README checked, no change — the test count did not move; MANUAL checked, no change — S105 already rewrote its INV-8 passages and nothing here changes documented behaviour.
