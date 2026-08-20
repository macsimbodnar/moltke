id:         S158
goal:       the reviewer fence knows when a run ended, and dates a file git cannot see
accepts:    a reviewer write to the report named by a baseline whose run has
            ended is refused, so an audit that never ran --audit new cannot
            overwrite the previous run's report by name; and a file git cannot
            see as new -- tests/ under gitignore, a rename source recreated
            during the run -- is not refused as "was here before this run" when
            this run wrote it; red observed on each
touches:    bin/moltke.py reviewer_write_refusal, _arrived_during_the_run, and
            whatever records that a run has ended
excludes:   fencing Bash, which DEC-022 accepted as unpoliced; widening
            worktree_state to --ignored, which --audit check shares
decisions:
closes:
blocks:
paused_by:
done:
