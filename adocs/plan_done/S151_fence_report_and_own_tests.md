id:         S151
goal:       the reviewer fence refuses overwriting another report and permits correcting its own new test
accepts:    a reviewer write to an existing file under adocs/audit/ that is not the report named by the current baseline is refused, and a write to a tests/ file the same run created is permitted; both decided from moltke_audit_baseline.json; red observed first on each direction
touches:    bin/moltke.py mode_pre_write reviewer branch, the audit baseline read
excludes:   fencing Bash, which DEC-022 accepted as unpoliced
decisions:
closes:     2026-08-19_adversarial-F11
blocks:
paused_by:
done:      reviewer_may_write decided both halves on existence alone and had each backwards
            (F11): every path under adocs/audit/ was permitted, so a Write at an earlier
            report's path destroyed evidence against AGENTS.md 2's add files, never overwrite;
            every existing path under tests/ was refused, so correcting a typo in the run's own
            red test went through Bash, where nothing is fenced or classified. The 2026-08-19
            run did exactly that and disclosed it.
            The question is when a file arrived, not whether it exists, and --audit new already
            records that. reviewer_write_refusal now permits a path that is not there yet, this
            run's report as the baseline names it, and anything git reports as having arrived
            since the baseline was taken; it refuses what was already here, with a different
            message per half. audit_baseline is shared with --audit check, so both judge a run
            against the same record.
            Where there is no git to date anything the fallback is what each half did before:
            report permitted, existing test refused. That direction was found by the suite --
            the first fallback permitted on both and took test_existing_test_file_is_blocked
            from green to 0 != 2, which is DEC-022's rule and not mine to relax.
            Bash stays unfenced by design (DEC-022): the fence is the fast clear failure on the
            common path, --audit check is the reconciliation. 496 green, --validate clean.
            specs' --pre-write row, MANUAL's fence paragraph and table row, the agent definition
            and README's one-line agent description all say when instead of whether.
author:    Maksym Bodnar
