id:         S129
goal:       watch primitive: self-terminating four-exit watcher with registration
accepts:    `--watch LOG REGEX --ceiling DUR` exits on its own on all four paths, each observed red-first — success marker (0, matched line printed), `--fail-re` marker (4), watched `--pid` dead (3, only after a final marker check of the log), ceiling reached (124); a marker written before arming is still caught; arming writes a record under `.git/moltke_watch/` and every exit path writes its outcome into that record, including a kill; `--watch` runs before the INV-11 gate so an unmarked repo can never fake exit 0; a missing `--ceiling` is refused with the §12 rule named; AGENTS.md gains §12 (primitive first, shell poll loop only as the no-tool fallback, banned forms named), the §4 gate line, and the §10 prohibition, byte-identical in templates/AGENTS.md; specs CLI table row, INV-11 amendment, MANUAL section and mode row, README test count, golden refreshed, all in this commit; plugin.json 0.3.0
touches:    bin/moltke.py, tests/test_s014_watch.py, tests/golden/cli_surface.txt, AGENTS.md, templates/AGENTS.md, adocs/specs.md, MANUAL.md, README.md, .claude-plugin/plugin.json
excludes:   arm-time enforcement and watch-record reporting in hooks (S130); stall detection via log mtime (rejected in DEC-049, deferred); a watch skill; Windows `--pid` support (os.kill(pid, 0) is not a liveness probe there; refused with a message)
decisions:  DEC-049
closes:
blocks:
paused_by:
done:      2026-08-18: --watch shipped, four self-terminating exits each observed red-first as subprocess exit codes (14 tests, suite 112 -> 126 green, --validate clean); registration under .git/moltke_watch/ with outcomes on every path including SIGTERM. README checked: test count updated. MANUAL checked: Watching long runs section, mode row, exit-code and gate-exemption text added. AGENTS.md section 13 + gate + prohibition, template identical. plugin.json 0.3.0.
