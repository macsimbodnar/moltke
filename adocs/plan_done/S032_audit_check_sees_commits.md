id:         S032
goal:       --audit check sees a change the run commits
accepts:    a tracked file patched and committed during an audit run is reported as unexpected, not as no change at all; the baseline records the HEAD sha alongside the worktree state and the check compares HEAD too, so a commit made during the run is part of the run's footprint; the report's own commit is still expected; red observed by committing a source patch between --audit new and --audit check, which today prints 'no change since --audit new' and exits 0; MANUAL's claim that a committed change 'shows up as reverted or committed, which is flagged as unexpected' is corrected in the same commit if the fix does not make it true
touches:    bin/moltke.py worktree_state, audit_new, audit_check; tests/test_s008_audit.py TestAuditReconciliation; MANUAL.md
excludes:   inspecting commit contents beyond what changed; preventing the reviewer from committing, which DEC-022 settled against
decisions:
closes:     2026-08-07_adversarial-F01
blocks:
paused_by:
done:      2026-08-07: --audit new records the HEAD sha and --audit check reports git diff from it as part of the run's footprint, so a committed patch is no longer invisible; the same expected/unexpected rule applies to commits, and an unreachable baseline HEAD is reported. 4 tests, red observed as the finding's own 'no change since --audit new' message. Suite 204 OK, --validate green. README test count 200 to 204; MANUAL's --audit check entry rewritten, including removing the claim that a committed change 'shows up as reverted or committed', which was true only for a file already dirty at baseline.
