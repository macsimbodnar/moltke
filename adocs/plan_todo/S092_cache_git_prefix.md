id:         S092
goal:       git_prefix is computed once per root, not once per path
accepts:    One run_checks over this repository spawns a single
            git rev-parse --show-prefix, not 257.
            --validate and --stop on this repository drop from about 7s to under 1s.
            The S081 behaviour it exists for is unchanged: the monorepo fixture at
            tests/test_s003_invariants.py:371 still passes, and INV-7/INV-8 still
            print blob specs that resolve below the git top level.
            A test asserts an upper bound on _git_run calls for one run_checks over
            a fixture with several completed steps; it fails without the fix.
touches:    bin/moltke.py git_prefix, from_git_path, to_git_path, run_checks;
            tests/test_s003_invariants.py
excludes:   caching any other git query; changing what INV-7 or INV-8 check.
decisions:
closes:     2026-08-08_adversarial.4-F05
blocks:
paused_by:
done:
