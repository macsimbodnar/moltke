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
done:      2026-08-09: --goal and --stamp are refused when they contain a line break, before anything is written, closing 2026-08-09_adversarial-F03. S095 gave parse_step_file a rule for multi-line values and no writer honoured the other half: write_step, append_to_plan and with_field each interpolate into one f-string, so a newline landed flush left, the one shape the parser is documented to drop. --goal put a list entry into plan.md that nobody typed and --validate then reported it; --stamp with the doc check on line two passed the gate that reads the string, wrote a file that reads back without it, left --validate green, and blocked every Stop for the rest of the turn with a remedy that cannot be followed, since plan_done/ is fenced and editing it from Bash turns the block into INV-7. Refused rather than reflowed, because a stamp is evidence and rewriting it quietly is the same class of defect as truncating it quietly. 5 tests, red observed on two; the other three drive both operands through the CLI and read the written file back through parse_step_file, which is the round trip the S095 tests skipped by hand-writing their fixtures and the reason this survived that step. Suite 427 OK, --validate green. README test count 422 to 427; MANUAL's --goal and --stamp paragraph states the refusal; specs gained a dated note.
