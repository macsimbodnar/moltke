id:         S097
goal:       allocating a step id no scanner can read is a refusal, not a success
accepts:    With `S999` present anywhere in plan.md, prose included, --step new
            refuses on stderr with exit 1, names the S999 ceiling and the plan.md
            token that caused it, and writes nothing: no file in plan_todo/, no
            entry in plan.md, --validate still exit 0. --step block refuses the
            same way.
            The refusal happens in mode_step before anything touches the
            filesystem, as S088's name check does.
            A test builds that fixture, runs --step new, and asserts the id space
            was not crossed; it fails without the fix.
            A second test pins the shape the defect produced: no S1000_*.md file
            exists afterwards and plan.md carries no four-digit entry.
            Ordinary allocation is unaffected: a repository whose highest id is
            S103 still allocates S104 and --validate stays green.
touches:    bin/moltke.py next_step_id, mode_step; tests/test_s007_step.py
excludes:   widening the id space to four digits, which is a decisions.md entry
            of its own and would change STEP_FILE_RE, PLAN_ENTRY_RE, pauser_id,
            inv_4_done_not_blocked and next_step_id together; changing what
            next_step_id reads (prose ids count on purpose, DEC-008);
            renumbering anything that exists
decisions:
closes:     2026-08-09_adversarial-F01
blocks:
paused_by:
done:      2026-08-09: --step new and --step block refuse when the next id would pass S999, before anything touches the filesystem, closing 2026-08-09_adversarial-F01. next_step_id had no upper bound while STEP_FILE_RE and PLAN_ENTRY_RE both require exactly three digits, so at the ceiling the allocator produced an id nothing in the tool can read: S1000_x.md on disk, S1000 listed in plan.md, and plan_steps, plan_order, derived_next, --roadmap and every invariant blind to it together with --validate green and no CLI path back. Two triggers, both real: any S999 token in plan.md prose, which the shipped plan template invites, and the id space genuinely running out. This is 2026-08-08_adversarial.4-F01 in its other half, since S088 validated the name in the same filename and left the id unchecked. The refusal names where the ceiling came from, so a prose token can be told from a real step; widening to four digits stays a decision rather than a rename. 5 tests, red observed on three; two are non-vacuity anchors, one holding that S999 itself is still allocatable. Suite 415 OK, --validate green. README test count 410 to 415; MANUAL checked, no change — it documents no id ceiling and the --step rows are unaffected; specs gained a dated note.
