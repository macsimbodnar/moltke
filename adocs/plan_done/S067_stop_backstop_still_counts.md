id:         S067
goal:       the Stop backstop still counts a turn and still prints what it found
accepts:    an OSError reaching main from --stop still advances the deadlock counter and still prints every problem run_checks and the earlier gates collected, so the cap fires and the session cannot wedge; five stops on the finding's own broken-symlink fixture read 2 2 2 0 0 rather than 2 2 2 2 2; the message names the path as before; MANUAL's promise that the Stop hook can never wedge a session is true again; red observed with the finding's sequence and the absent state file
touches:    bin/moltke.py mode_stop error handling and the main backstop; tests/test_s005_hooks.py
excludes:   reverting S060, whose exit-1 traceback was the worse failure
decisions:  
closes:     2026-08-08_adversarial.2-F01
blocks:
paused_by:
done:      2026-08-08: --stop reports and counts on every path. S060's backstop returned before the retry counter mode_stop writes at the end, so an OSError from status_disagreements, the porcelain gates, or stop_turn_key dropped every problem already collected and blocked forever — the one thing INV-12 and DEC-006 say --stop may never do, and a regression this batch introduced. Each section now catches its own failure and turns it into a problem, which the function already knows how to report, and the porcelain gates lifted into porcelain_problems so the catch sits next to what raises. Every git call goes through one _git_run returning None when there is no git, since _git_lines was made tolerant of a missing binary and the three direct subprocess.run sites were not, turning the documented abstention into INV-7 and INV-8 read failures. 5 tests, red observed on all four triggers: broken symlink, directory-where-step-file, unreadable worklog, git off PATH. Suite 312 OK, --validate green. README test count 308 to 312; MANUAL's no-wedge promise is true again and needed no rewording; specs gained a dated note.
