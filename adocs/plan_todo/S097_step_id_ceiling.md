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
done:
