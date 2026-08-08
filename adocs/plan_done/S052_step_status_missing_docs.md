id:         S052
goal:       --step does not traceback in a marked repository without adocs/
accepts:    --step status, --step done, and --step start in a marked repository whose adocs/ is absent refuse with an actionable message naming --scaffold, instead of raising FileNotFoundError; this matters more since S039, which now prints four staleness lines steering the user into exactly that command; the same repository's other modes are unaffected; red observed with the traceback
touches:    bin/moltke.py step_status and the --step entry points; tests/test_s007_step.py
excludes:   creating adocs/ implicitly, which would hide a repository that was never scaffolded
decisions:
closes:     2026-08-07_adversarial.2-F05
blocks:
paused_by:
done:      2026-08-08: --step refuses naming --scaffold in a marked repository with no adocs/, instead of raising FileNotFoundError out of step_status, step_start, and step_done, and an OSError from any operation becomes a refusal for the partially scaffolded tree. The directory is not created implicitly: a repository never scaffolded says so rather than being half-built by a status write. The steering was the other half — with no adocs/ all four derived fields disagree, so --session-start and --stop both named --step status, the one command that could not work there; both now name --scaffold first through one _stale_remedy. 6 tests, red observed (traceback for status and new, misleading refusals for start, done, block), plus the finding's transcript re-measured. Suite 258 OK, --validate green. README test count 252 to 258; MANUAL states the refusal under the mode table; specs gained a dated note.
