id:         S105
goal:       the tool stops enforcing document history, so the documents can shrink
accepts:    INV-8 is retired: rewriting or trimming adocs/decisions.md and
            adocs/worklog.md is no longer a violation, --validate stays exit 0
            after such an edit, and the INV-8 number is never reused.
            --step done prunes completed entries from plan.md, keeping the last 5
            done entries in plan order plus every entry that is not done, so
            plan.md is bounded by open work rather than by project age. Last done,
            derived next, --roadmap and next_step_id all still answer correctly
            over a pruned plan, pinned by tests.
            Tests that pinned append-only behaviour are deleted or re-targeted
            deliberately, each named in the recap with why, none weakened to pass.
            The golden CLI surface is unchanged.
touches:    bin/moltke.py (APPEND_ONLY_FILES, inv_8_append_only, step_done);
            tests/test_s003_invariants.py, tests/test_s004_invariants.py;
            adocs/decisions.md (DEC-042)
excludes:   compacting the documents themselves, which is S106 and must come
            after this or the tool blocks its own cleanup; touching the plan_done/
            write fence, which stays; changing INV-7
decisions:  DEC-042
closes:
blocks:
paused_by:
done:      2026-08-09: INV-8 is retired and its number is never reused (DEC-042); rewriting or trimming decisions.md and the worklog is an ordinary edit, and --step done prunes plan.md to the last 5 completed entries so the plan is bounded by open work rather than project age. Roadmap counts done from plan_done/ now, since the pruned list forgets. plan_done/ keeps every id, so DEC-008 and the S097 ceiling still see all of history, pinned by a test. 8 new tests, red observed on the property flips; 14 tests deleted deliberately with the invariant and named in testing.md, one re-targeted to its INV-7 half — the non-vacuity anchor holds INV-7 still firing so retirement is distinguishable from breakage. Golden CLI surface unchanged. Suite 438 OK, --validate green. README test count updated 444 to 438 in S106 batch? No — updated now; MANUAL's two INV-8 passages rewritten to the retirement, the historical monorepo passage kept as history; specs.md is S106's job.
