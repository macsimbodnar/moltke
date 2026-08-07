id:         S052
goal:       --step does not traceback in a marked repository without adocs/
accepts:    --step status, --step done, and --step start in a marked repository whose adocs/ is absent refuse with an actionable message naming --scaffold, instead of raising FileNotFoundError; this matters more since S039, which now prints four staleness lines steering the user into exactly that command; the same repository's other modes are unaffected; red observed with the traceback
touches:    bin/moltke.py step_status and the --step entry points; tests/test_s007_step.py
excludes:   creating adocs/ implicitly, which would hide a repository that was never scaffolded
decisions:
closes:     2026-08-07_adversarial.2-F05
blocks:
paused_by:
done:
