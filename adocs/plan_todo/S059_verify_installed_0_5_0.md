id:         S059
goal:       verify the installed 0.5.0 in a live session, after reinstall
accepts:    the installed plugin resolves to 0.5.0 rather than the cached older version, evidenced from ~/.claude/plugins/installed_plugins.json and the cached bin/moltke.py; all five hook events observed firing in a live session against this repository, with the SessionStart context, a logged prompt, a refused write into plan_done/, a post-write scan, and a Stop refusal each recorded verbatim; the reviewer fence observed against a live plugin subagent spawn rather than a synthetic payload, which is what S012's clause 6 and finding F02 left unproven; status.md's parked note about the installed version being stale is removed in the same commit, or narrowed to what is still true
touches:    adocs/audit/ or adocs/testing.md for the observations; adocs/status.md; MANUAL.md if any documented behaviour differs live
excludes:   the reinstall itself, which is Max's own (claude plugin install moltke@moltke); changing behaviour to fix what the live session reveals, which becomes its own step
decisions:  DEC-034
closes:
blocks:
paused_by:
done:
