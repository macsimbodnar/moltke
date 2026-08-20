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
done:
