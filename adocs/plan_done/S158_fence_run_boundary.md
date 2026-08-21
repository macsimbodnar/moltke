id:         S158
goal:       the reviewer fence knows when a run ended, and dates a file git cannot see
accepts:    a reviewer write to the report named by a baseline whose run has
            ended is refused, so an audit that never ran --audit new cannot
            overwrite the previous run's report by name; and a file git cannot
            see at all -- a tests/ path under gitignore -- is not refused as
            "was here before this run" when this run wrote it; red observed on
            each. The rename source this accepts named as a second case is not
            one: worktree_state already lets a recreated source's own untracked
            line beat its departure, so it dates as new and is permitted (S155
            fast check verified it against the code). A red test written for it
            comes back green.
touches:    bin/moltke.py reviewer_write_refusal, _arrived_during_the_run, and
            whatever records that a run has ended
excludes:   fencing Bash, which DEC-022 accepted as unpoliced; widening
            worktree_state to --ignored, which --audit check shares
decisions:
closes:
blocks:
paused_by:
done:      2026-08-21. --audit check now stamps the baseline `ended`, which is the end of a run because MANUAL's table and the audit skill both run it once the reviewer has returned; the fence refuses a write to an ended run's report by name and lets an ended baseline date nothing else, falling back to the no-baseline halves. A path git cannot see at all is permitted where it stands: _invisible_to_git asks `git check-ignore -q --` per path, so worktree_state is not widened to --ignored, which --audit check shares. Accepted cost, stated in the skill: a reviewer that runs --audit check itself through Bash locks itself out of its own report, a loud block over a silent pass.
            Red observed on both halves before the fix (5 of 11 failing); the rename-source case S158's accepts named as a second red test came back green on arrival, as the S155 fast check predicted. check-ignore's index awareness mutation-checked with --no-index. Suite 538 OK, --validate green. README, MANUAL, specs.md and skills/audit/SKILL.md updated; testing.md carries five rows.
author:    Maksym Bodnar
