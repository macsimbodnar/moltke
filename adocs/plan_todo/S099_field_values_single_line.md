id:         S099
goal:       a written field value cannot land in a shape the parser drops
accepts:    --step new --goal with a newline in it does not put an unasked-for
            line into plan.md: either it refuses before anything is written, or
            the goal reaches plan.md and the step file in a shape parse_step_file
            reads back whole. Whichever is chosen, --validate is exit 0 afterwards
            rather than reporting a violation the tool itself created.
            --step done --stamp with the README and MANUAL mention on a second
            line does not complete green and then read back without it. The stamp
            the gate accepted and the stamp the file carries are the same string,
            asserted by reading the written file back through parse_step_file.
            The Stop gate no longer blocks a turn with a remedy that cannot be
            followed: no state reachable through --step leaves plan_done/ holding
            a stamp its own gate rejects.
            Tests drive both cases through the CLI and read the result back —
            the round trip the S095 tests skipped by hand-writing their fixtures,
            which is why this survived that step. They fail without the fix.
touches:    bin/moltke.py mode_step operand handling, write_step, append_to_plan,
            with_field; tests/test_s007_step.py
excludes:   changing parse_step_file's rule, which S095 settled and which is the
            reader half; the single-line stamp convention every plan_done/ file
            follows, which is a habit rather than a constraint
decisions:
closes:     2026-08-09_adversarial-F03
blocks:
paused_by:
done:
