# Audit 2026-08-07 adversarial

Scope: `bin/moltke.py`, `hooks/hooks.json`, `agents/adversarial_reviewer.md`,
`skills/`, `tests/`, and the claims made about them in `README.md`, `MANUAL.md`,
`adocs/specs.md`, and `AGENTS.md`. Commit `1500b83` (S026) plus one uncommitted
change, `.claude-plugin/plugin.json` bumped `0.2.0` → `0.3.0`.

Method: two jobs. First, a verdict on each of the fourteen findings in
`adocs/audit/2026-08-06_adversarial.md`, decided against the current code and
reproduced with `bin/moltke.py` in throwaway repositories, never against the step
files or the commit messages. Second, a fresh adversarial pass over the twelve
steps of new surface that landed since (S014..S026, S030), including mutation
testing: each new behaviour was deleted in a copy of the repository outside it and
the suite re-run, to see whether the tests that name it actually bite.

Baseline at the start of the run:

```
$ python3 -m unittest discover -s tests
Ran 173 tests in 29.279s
OK
$ python3 bin/moltke.py --validate
moltke: all checks pass
```

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name:

```
### 2026-08-07_adversarial-F01  high  short title

Status: open

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
```

Every finding ends in one of two places: a plan step whose `closes:` field
names it, or a decision entry stating why it will not be acted on, which moves
it to `accepted`. A finding moves to `closed` only after the audit is re-run
and no longer reports it. Fixing without re-running leaves it `planned`.

Summary: 11 new findings. 4 high, 4 medium, 3 low. Of the fourteen prior
findings, twelve no longer reproduce, one (F03) reproduces exactly as before but
was deliberately accepted by DEC-022, and one (F02) is fixed in this checkout but
cannot be settled here for a live session — the installed plugin is still 0.2.0.

Four of the new findings sit in the machinery S017, S018 and S015 added. The
pattern is the mirror image of last time: last time the enforcement never fired,
this time it fires and then cannot be satisfied, or it fires on the wrong thing,
or it stops firing on the one path the reviewer would actually take.

## Verdicts on the 2026-08-06 findings

One line each, decided against the code at `1500b83`.

- **F01** (Stop recap gate cannot fire live) — **no longer reproduces**.
  `bin/moltke.py:636-655` reads headings, not size. With the live-session
  precondition present (`--log-prompt` first, exactly as `UserPromptSubmit`
  does), `--stop` still blocks: `exit=2`, `moltke: source changed but
  adocs/worklog.md has no recap heading after the last logged prompt`; appending
  `## 2026-08-07 recap S001` clears it, `exit=0`. See F02 below for a case where
  it silently stops firing again.
- **F02** (reviewer fence never matches, fails open) — **no longer reproduces in
  this checkout; not settleable here for a live session, and still reproducing in
  the installed plugin.** The suffix match is at `bin/moltke.py:580-581`; a
  payload carrying `agent_type: "moltke:adversarial_reviewer"` and
  `file_path: src/main.py` now exits 2. Whether Claude Code sends that exact
  string cannot be established by reading this checkout — S016 records observing
  it live, and this run has no way to re-observe it. What *is* observable here is
  that it does not matter yet: `~/.claude/plugins/installed_plugins.json` pins
  `moltke@moltke` to `installPath .../cache/moltke/moltke/0.2.0`,
  `gitCommitSha 106477472b03ab75b67b269e505ab65d929169f7` (S013), and
  `grep -n agent_type ~/.claude/plugins/cache/moltke/moltke/0.2.0/bin/moltke.py`
  gives line 408, `if payload.get("agent_type") == REVIEWER_AGENT and parts[:2]
  != (DOCS, "audit"):` — the bare equality F02 was about. Every hook firing on
  this machine today runs that file. `adocs/status.md:16` already parks this.
- **F03** (reviewer holds Bash, fence bypassable) — **still reproduces, by
  decision**. `agents/adversarial_reviewer.md:4` still grants
  `tools: Read, Grep, Glob, Bash, Write`; `hooks/hooks.json` still matches
  `"Write|Edit"` only. DEC-022 accepted this and replaced prevention with
  `--audit check`. The finding is discharged as `accepted` rather than fixed, and
  the replacement has a hole of its own: F01 below.
- **F04** (immutability evaporates at the next commit) — **no longer
  reproduces**. Tampering with `adocs/plan_done/S001_base.md` and
  `adocs/decisions.md` and then committing it gives
  `INV-7: ... was M in commit e5cd3f8d`, `INV-8: ... lost 1 line(s) in commit
  e5cd3f8d`, exit 1. A committed deletion is caught too (`was D in commit
  47282bc3`). See F03 below for what the fix costs.
- **F05** (fenced guidance discharges a finding) — **no longer reproduces**.
  With the baseline violation established first, adding the finding id inside a
  fence in `decisions.md` leaves `--validate` at exit 1 and `--audit list` at
  `no reference`. A bare prose mention outside a fence still discharges it, which
  was the optional half of the suggested resolution, not the finding.
- **F06** (documented exit codes wrong for every refusal) — **no longer
  reproduces**. The code is unchanged (`refuse` still prints to stderr and
  returns 1) and the documentation now states that mapping: `README.md:69-83`,
  `MANUAL.md:137-157`, pinned by `tests/test_s025_exit_codes.py`. One path still
  contradicts it: F11 below.
- **F07** (green-suite gate not enforced) — **no longer reproduces with a valid
  `test_command`**; `--step done` with `"test_command": "exit 3"` refuses,
  exit 1, and leaves the step in `plan_current/`. It still reproduces when the
  key is present but malformed: F07 below.
- **F08** (worklog is an unremovable secret sink) — **no longer reproduces**.
  `APPEND_ONLY_FILES` is `(adocs/decisions.md,)` at `bin/moltke.py:277`, so
  cleaning the worklog is an ordinary edit, and `tests/test_s022_secrets.py`
  scans it inside the normal suite, non-vacuously (each shape is asserted against
  its own example first).
- **F09** (a finding cannot be closed the day it is fixed) — **no longer
  reproduces**. Two `--audit new adversarial` calls on the same day produce
  `2026-08-07_adversarial.md` and `2026-08-07_adversarial.2.md`, neither
  overwritten, ids numbered from their own stems.
- **F10** (surface guard covers argparse only) — **no longer reproduces**.
  Deleting the `Stop` event from `hooks/hooks.json` in a copy of the repository
  now fails `test_surface_matches_the_golden`; adding a fourth skill fails the
  golden plus both documentation cross-checks.
- **F11** (typo in plan.md creates a permanent phantom) — **no longer
  reproduces as a silent defect**; `INV-3` names it. The documented residual is
  real and unchanged: with the phantom first in plan order, `--validate` reports
  it while `--session-start` still announces
  `Derived next step: S099 (first in plan.md order not in plan_done/)`.
- **F12** (INV-7 wording contradicts implementation) — **no longer reproduces**.
  `adocs/specs.md:34` now states the committed baseline and marks the session-start
  wording superseded, dated, in place.
- **F13** (documentation drift, three items) — **no longer reproduces**. The
  install section names the hosted repository unconditionally
  (`MANUAL.md:22-27`); `.claude-plugin/plugin.json` carries
  `"repository": "https://github.com/macsimbodnar/moltke"`;
  `adocs/plan_todo/` exists with a `.gitkeep`.
- **F14** (prompt logging fails silently) — **no longer reproduces**.
  `--log-prompt` in a marked repository with no `adocs/` writes
  `adocs/worklog.md` and the prompt survives; a genuinely failing append leaves
  `.git/moltke_log_failure.json` and `--session-start` reports it once. One
  condition still loses prompts with no breadcrumb, and it is not the documented
  "outside a git repository" one: F04 below.

## Findings

### 2026-08-07_adversarial-F01  high  `--audit check` cannot see a change the run commits

Status: open

Evidence: `audit_check` (`bin/moltke.py:1149-1200`) diffs two `git status`
snapshots. A file that was clean when `--audit new` ran and that the run modifies
**and commits** appears in neither snapshot, so it is not merely misclassified —
it is absent. Reproduced in a committed fixture repository, control first:

```
=== F1: reviewer patches a CLEAN tracked file and commits it ===
--- a. patched, NOT committed (control): exit=1
  stdout: expected, this run's report and new tests:
            adocs/audit/2026-08-07_adversarial.md: ??
          unexpected, not attributable to writing the report:
            src/main.py: M
--- b. same patch, committed during the run: exit=0
  stdout: no change since --audit new; the report itself has not been written yet.
  HEAD src/main.py is now: print('patched by the reviewer')
```

The same holds for the case the fence exists to stop — weakening an existing
test:

```
=== F2: reviewer weakens an EXISTING test and commits it ===
--- weakened test, committed: exit=0
  stdout: no change since --audit new; the report itself has not been written yet.
```

`MANUAL.md:212-214` claims the opposite in as many words: "changes the reviewer
commits itself stop being reported as changed and show up as 'reverted or
committed', which is flagged as unexpected rather than hidden". That is true only
for a file that was already dirty at baseline — the branch at
`bin/moltke.py:1174-1175`, which needs `was` to be non-`None`. For a clean file,
the common case, there is no `was` and no `now`.

Note the second failure inside the first: the message printed at exit 0 is
`no change since --audit new; the report itself has not been written yet`, while
the report had in fact been written and committed. The reconciliation reports
"nothing happened" for a run that rewrote source.

`tests/test_s008_audit.py:262-352` (`TestAuditReconciliation`) covers the
uncommitted variants of all of this and never commits, so the suite reports the
mechanism as covered.

Impact: DEC-022 traded the write fence away for this check —
"prevention gives way to detection", `adocs/specs.md:168-182`. Detection is
defeated by `git commit`, which the reviewer holds `Bash` for, and which is a
plausible thing for a confused reviewer to do rather than a hostile one. The
audit skill's step 3 (`skills/audit/SKILL.md:33-43`) tells the operator that a
clean `--audit check` means the report is uncontaminated. It does not mean that.

Suggested resolution: compare against `HEAD` as well as against the working tree
— record the baseline `HEAD` sha in `.git/moltke_audit_baseline.json` and report
any commit made since it as part of the run's footprint, expected only if it
touches nothing but the report and new tests. That also fixes the misleading
"no change since --audit new" line. Not applied here.

### 2026-08-07_adversarial-F02  high  an unbalanced code fence hides an open finding from INV-10 and the recap gate

Status: open

Evidence: `strip_guidance` (`bin/moltke.py:94-103`) pairs triple-backtick markers
globally and non-greedily, with no notion of line-start or of balance, so an odd
marker shifts every later pairing and deletes real content between two unrelated
fences. Two scanners read their whole input through it: `report_findings`
(`bin/moltke.py:351-361`) and `recap_pending` (`bin/moltke.py:636-655`).

An audit report with two unclosed evidence fences loses the finding between them.
Control first, so the exit 0 is not the checker being broken:

```
=== J2: two unclosed fences hide the finding between them ===
--- control: both fences closed: exit=1
  stdout: VIOLATION: INV-10: open finding 2026-08-01_adversarial-F02 in
          2026-08-01_adversarial.md has no step closes: reference and no
          decisions.md entry; plan it or record why it is accepted
--- both fences left unclosed: exit=0
  stdout: moltke: all checks pass
--- audit list: exit=0
  stdout: 2026-08-01_adversarial.md
            2026-08-01_adversarial-F01  accepted  (no reference)
```

`--audit list` does not report the finding as unreferenced. It does not list it
at all.

The same mechanism silently disables the S015 recap gate. A recap whose body
pastes a diff and opens a fence it never closes, followed by a prompt that pastes
a fenced snippet — both entirely ordinary — makes `Stop` allow an unrecapped
turn:

```
=== C4: a stray fence in a recap + a fenced paste in the next prompt = false ALLOW ===
--- control: clean recap, turn two unrecapped -> must BLOCK: exit=2
--- same, but the recap body opens a fence it never closes: exit=0
  headings seen by the gate: ['## 2026-08-01 prompt', '## ...T11:17 prompt', '## 2026-08-07 recap S001']
  headings actually in the file: ['## 2026-08-01 prompt', '## ...T11:17 prompt', '## 2026-08-07 recap S001', '## ...T11:17 prompt']
```

The gate loses the last prompt heading, sees an older recap as the newest
heading, and concludes the turn was recapped.

This report reproduced the defect on itself while being written; see the
post-report verification section at the end, which is the strongest evidence in
this finding. The worklog is currently clean: it holds no triple-backtick markers
at all and keeps all 68 of its headings through `strip_guidance`. The report path
is live the moment a reviewer pastes command output, which is what the agent
definition asks for.

Impact: two of the workflow's evidence guarantees fail open on ordinary content
rather than on tampering. INV-10 exists to stop a finding being filed and
forgotten; a stray backtick does exactly that, and `--validate` says
`all checks pass`. `adocs/specs.md:318-325` states the rule this violates:
"template guidance is never data" was meant to make guidance invisible, not to
make data invisible.

Suggested resolution: anchor the fence regex to the start of a line, with
`re.M | re.S`, so a quoted marker inside a worklog blockquote or inside an inline
code span is not a fence at all, and treat an unmatched trailing fence as text
rather than swallowing to the next one. Add a red-first case for each scanner.
Consider having `--audit new` warn when a report's marker count is odd. Not
applied here.

### 2026-08-07_adversarial-F03  high  one committed tampering makes INV-7 and INV-8 permanently red, and the prescribed fix does not clear it

Status: open

Evidence: the S018 history baselines (`bin/moltke.py:258-269`,
`bin/moltke.py:290-303`) report any commit whose `--name-status` is not `A` under
`plan_done/`, or whose `--numstat` removed a line from `decisions.md`. That commit
stays in history forever, so the violation is permanent. Doing exactly what the
violation message says does not clear it:

```
--- 1. tampering committed: exit=1
  VIOLATION: INV-7: adocs/plan_done/S001_base.md was M in commit e5cd3f8d ...
    Recover the original with git show $(...) and restore it in a new commit;
    never rewrite the history that recorded it
  VIOLATION: INV-8: adocs/decisions.md lost 1 line(s) in commit e5cd3f8d ...
    Restore the removed content in a new commit ...
--- 2. after following the prescribed fix: exit=1
  VIOLATION: INV-7: adocs/plan_done/S001_base.md was M in commit e5cd3f8d ...
  VIOLATION: INV-8: adocs/decisions.md lost 1 line(s) in commit e5cd3f8d ...
--- 3. --stop, same repo: exit=2
```

The only operation that would clear it is a history rewrite, which the same
message forbids and `AGENTS.md` §11 prohibits outright. `git revert` does not
help: it adds a commit, it does not remove one.

This is not hypothetical for this workflow. `git log --reverse --no-renames
--numstat -- project/decisions.md` shows `e8084d3` with `83  67` — the DEC-013
one-time authorised reorder, 67 lines removed. Under today's INV-8 that repository
would be permanently red. It is green now only because S013 renamed the file to
`adocs/decisions.md` and `--no-renames` starts the history there; a round-trip
rename does *not* restore the exemption, so the escape is not repeatable either.

Impact: any single accident — an agent that edits `plan_done/` with `sed`, a
merge that touches a completed step, a decision entry corrected in place — puts
the repository into a state where `--validate` can never exit 0 again and `--stop`
blocks every turn until the `STOP_CAP` waiver fires. AGENTS.md §5 requires every
commit to be green; after one such commit no commit can be. The waiver then makes
things worse: after three attempts `--stop` allows the stop with a warning, so
every *other* Stop check — stale status, missing recap, unchecked README — is
waved through for the rest of that prompt.

Suggested resolution: give the invariant a legal terminal state. Options worth
weighing: accept a repair commit that restores the file to its original bytes and
stop reporting once the current content matches the `--diff-filter=A` version;
or keep reporting but demote a repaired violation to a note that does not fail the
exit code; or record an explicit, dated waiver in `decisions.md` that the check
reads, which is what DEC-013 already did by hand. This is a decision for the user,
not the agent. Not applied here.

### 2026-08-07_adversarial-F04  high  in a linked git worktree the audit baseline, the log breadcrumb, and the Stop deadlock cap all vanish

Status: open

Evidence: three helpers decide "is there a git repository here" with
`(root / ".git").is_dir()` — `_log_failure_path` (`bin/moltke.py:474-476`),
`_stop_state_path` (`bin/moltke.py:621-623`), `_audit_baseline_path`
(`bin/moltke.py:1071-1073`). In a linked worktree, and in a submodule, `.git` is a
**file**. Reproduced with `git worktree add`:

```
=== H: a linked git worktree (.git is a file, not a directory) ===
  .git in the worktree is a file
  git works there: True
--- --validate in the worktree: exit=0
  stdout: moltke: all checks pass
--- --audit new in the worktree: exit=0
  stderr: moltke: no git worktree here, so --audit check cannot reconcile this run;
          whatever the reviewer changes will go unnoticed.
--- --audit check in the worktree: exit=1
  stderr: moltke: no audit baseline recorded here; run --audit new <type> first ...
  --stop exit codes over 5 consecutive attempts, same prompt_id: [2, 2, 2, 2, 2]

=== H2: same sequence in an ordinary clone, for contrast ===
  --stop exit codes: [2, 2, 2, 0, 0]
```

Three separate failures in one condition. `--audit new` says "no git worktree
here" inside a git worktree where `git status` works, and records no baseline.
`--audit check` then refuses forever and names a remedy that will never work.
And `--stop` never reaches its cap: `[2, 2, 2, 2, 2]` against `[2, 2, 2, 0, 0]`.

That third one is an invariant, not a nuisance. `adocs/specs.md:42` states INV-12
with DEC-006's reason — "a `Stop` hook has a cap on consecutive blocks; an
unactionable message deadlocks the session" — and `bin/moltke.py:703-709` calls
the cap "the no-deadlock property of DEC-006 / INV-12". In a linked worktree the
property is absent, and combined with F03 above a session there can be
unrecoverably wedged.

`record_log_failure` is inert in the same condition, so S014's fix for F14 silently
degrades to the pre-S014 behaviour: prompts lost, no breadcrumb. `MANUAL.md:277-279`
attributes that only to being "outside a git repository".

Impact: parallel agent work on one repository is the obvious use for
`git worktree`, and submodules hit the same path. Every state file moltke keeps
disappears with no diagnostic, while `--validate` reports `all checks pass`.

Suggested resolution: resolve the git directory instead of guessing — one
`git -C <root> rev-parse --absolute-git-dir` gives the right location for a plain
clone, a linked worktree, and a submodule, and its failure is the real "no git
here" signal. Then correct the `--audit new` warning text, which today is a
statement about `.git` being a directory dressed up as a statement about git.
Not applied here.

### 2026-08-07_adversarial-F05  medium  `--audit check` blames the plugin's own worklog write on the reviewer

Status: open

Evidence: `--audit new` records the baseline (`bin/moltke.py:1119-1142`), and the
`UserPromptSubmit` hook appends to `adocs/worklog.md` on every subsequent prompt
(`bin/moltke.py:528-545`). Any audit that spans a prompt therefore has a
worklog change in its footprint, attributed to the run. On this repository, right
now:

```
$ python3 bin/moltke.py --audit check
expected, this run's report and new tests:
  adocs/audit/2026-08-07_adversarial.md: ??
unexpected, not attributable to writing the report:
  adocs/worklog.md: changed again (was M, now M)
The reviewer holds Bash and is not fenced from mutating the repository (DEC-022).
Review each change above before acting on any finding: git diff, then keep or
revert deliberately.
exit=1
```

The reviewer has not touched `adocs/worklog.md` and cannot: it is outside the
fence. Reproduced from scratch, isolating the single cause:

```
--- check immediately after --audit new: exit=0
--- check after ONE user prompt: exit=1
  unexpected, not attributable to writing the report:
    adocs/worklog.md: M
```

Impact: the reconciliation the audit skill runs at step 3 emits a false positive
on essentially every real audit, exits 1, and instructs the operator to review a
change the tool itself made. A gate that is wrong every time is a gate people
learn to wave through — and F01 above is what it lets past while it cries wolf.

Suggested resolution: classify `adocs/worklog.md` as expected when its diff is
append-only, or re-snapshot it at `--audit check` time from the same source that
wrote it, or exclude the paths moltke's own hooks write. Prefer the first: an
append is what the hook does, a rewrite is what a reviewer covering its tracks
would do, and the distinction is one `git diff --numstat`. Not applied here.

### 2026-08-07_adversarial-F06  medium  the Stop recap gate treats `.claude-plugin/` as not-source

Status: open

Evidence: `bin/moltke.py:670-671`.

```python
changed_source = [line for line in porcelain
                  if not line[3:].startswith((f"{DOCS}/", ".claude"))]
```

`.claude` is a bare prefix, so it also matches `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, and anything else beginning with those seven
characters. Measured one path at a time, everything else equal:

```
  src/main.py                      exit=2  BLOCKS (recap required)
  bin/moltke.py                    exit=2  BLOCKS (recap required)
  .claude-plugin/plugin.json       exit=0  allows
  .claudefoo                       exit=0  allows
  .claude/settings.json            exit=0  allows
  adocs/specs.md                   exit=0  allows
```

`.claude-plugin/plugin.json` is the plugin manifest: the version there is the only
thing that decides what every installed copy of moltke executes
(`MANUAL.md:43-46`, `MANUAL.md:170-174`). It is the single highest-consequence
tracked file in the repository, and it is exempt from the recap requirement. The
working tree carries exactly that change right now, uncommitted.

Impact: a release can be cut with no worklog recap of it. Smaller, but real:
`.clauderc` or any future `.claude*` file at the root inherits the same hole.

Suggested resolution: match `.claude/` with the separator, and list the exempt
prefixes explicitly rather than relying on a shared stem. A test that walks a
table of representative paths and asserts block-or-allow per path would pin it.
Not applied here.

### 2026-08-07_adversarial-F07  medium  a malformed `test_command` silently turns the suite gate off, and `--step done` says the key is absent

Status: open

Evidence: `run_test_command` (`bin/moltke.py:943-952`) treats anything that is not
a non-empty string as "not configured" and returns `None`, which
`step_done` (`bin/moltke.py:1005-1007`) reads as "proceed". `check_marker`
(`bin/moltke.py:71-77`) does flag the value, but `mode_step` is never given the
marker violations — only `--validate`, `--post-write`, and `--stop` receive them
(`bin/moltke.py:1330-1341`). Four malformed values, each with a green completion:

```
  test_command=''
    --validate exit=1 says: ['VIOLATION: .moltke.json: "test_command" must be a
      non-empty shell command string, got ''; remove the key to leave the suite
      gate unconfigured']
    --step done exit=0 moved_to_done=True
    --step done said: 'moltke: no "test_command" in .moltke.json, so nothing here
      ran the suite. ...'
  test_command='   '            -> same, moved_to_done=True
  test_command=['python3', '-m', 'unittest'] -> same, moved_to_done=True
  test_command=0                -> same, moved_to_done=True
```

Control, same fixture with a valid failing command: `--step done` refuses with
exit 1 and the step stays in `plan_current/`.

The message is not just permissive, it is wrong: it reports that there is no
`test_command` in the marker when there is one. `bin/moltke.py:68-70` states the
intent this violates — "A blank value is a violation rather than a no-op:
silently gating nothing is the failure this key exists to remove."

Impact: the failure mode DEC-023 was written to remove, reached by a typo. A
repository that believes its completions are suite-gated has them ungated, and
the one command that would tell it so is a different command than the one it is
running. `MANUAL.md:83-91` promises `--step done` refuses on a non-zero exit and
that a blank value is a marker violation; both halves are true separately and do
not meet.

Suggested resolution: have `--step done` refuse when `test_command` is present and
malformed, distinct from absent, and say which. Cheapest correct form is to pass
`marker_violations` into `mode_step` and refuse on any of them before touching the
plan. Not applied here.

### 2026-08-07_adversarial-F08  medium  `status.md` staleness is detected only through its `Next:` line

Status: open

Evidence: `status_next` (`bin/moltke.py:438-443`) extracts one id with
`re.search(r"Next:.*?\b(S\d{3})\b", ...)`, and both detectors compare only that —
`mode_session_start` (`bin/moltke.py:461-463`) and `mode_stop`
(`bin/moltke.py:664-666`). Every other line may say anything. With
`plan_current/` holding `S003` and `status.md` claiming otherwise:

```
  plan_current holds: ['S003_active.md']
  status.md says In progress: nothing at all, Last done: S999
--- --validate: exit=0
  stdout: moltke: all checks pass
--- --stop: exit=0
  session-start: moltke stack (plan_current/):
  S003: active
  Derived next step: S002 (first in plan.md order not in plan_done/).
```

No staleness line. This repository is in that state as I write:
`adocs/status.md:9` reads `- In progress: none` while
`adocs/plan_current/S027_close_audit.md` exists, and `--session-start` prints the
stack containing S027 with no complaint.

Impact: `AGENTS.md` §1 makes this the exact scenario the check exists for — "a
crashed or interrupted session leaves it stale", "if it disagrees with the
contents of `plan_current/`, the directory wins and `status.md` is regenerated
from it before any work starts". The `Next:` line is the one field the filesystem
and the file rarely disagree about, because both derive it the same way; the
in-progress stack is the field a crash actually corrupts. `MANUAL.md:97-98` and
`MANUAL.md:102-103` state the guarantee unqualified.

Suggested resolution: compare the whole regenerated body, not one field —
`step_status` already builds it, so the check is "does `status.md` equal what
`--step status` would write, ignoring the `Updated:` line and the Parked block".
Then a stale file is detected whatever went stale. Not applied here.

### 2026-08-07_adversarial-F09  low  `--audit new <type>` writes outside `adocs/audit/` when the type contains a path separator

Status: open

Evidence: `next_report_path` (`bin/moltke.py:1102-1116`) interpolates the type
into a filename with no validation, and `audit_new` then calls
`report.parent.mkdir(parents=True, exist_ok=True)`. Reproduced:

```
$ python3 bin/moltke.py --audit new ../../outside/pwned
moltke: created adocs/audit/2026-08-07_../../outside/pwned.md. Write every
finding before fixing anything; finding ids are pwned-F01, -F02, ...
exit=0

  .../repo/adocs/audit/2026-08-07_..          <- directory, created
  .../repo/adocs/audit/outside/pwned.md       <- the report
```

Deeper types climb further; the printed path is `relative_to(root)` computed
lexically, so it always looks like it landed under `adocs/audit/`. The suggested
finding-id stem degrades to the last path component (`pwned-F01`), which no longer
matches any report `INV-10` can see, and the report is outside the
`audit_dir.glob("*.md")` both `inv_10_audit_findings` and `audit_list` use — so
its findings are counted by nothing. Types with spaces or dots are accepted too:
`--audit new UPPER.2` produces `2026-08-07_UPPER.2.md`, colliding with the
namespace S020 reserved for same-day re-runs.

Impact: self-inflicted rather than hostile — the type comes from the invoking
agent — but the result is a report that looks filed and is invisible to every
check, plus stray directories in the tree. Low because it needs a strange type,
recorded because the failure is silent and the printed path actively misleads.

Suggested resolution: restrict the type to `[A-Za-z0-9_-]+` and refuse otherwise,
naming the rule. Not applied here.

### 2026-08-07_adversarial-F10  low  the reviewer's `tests/` allowance is escapable with a relative `..` path

Status: open

Evidence: `reviewer_may_write` (`bin/moltke.py:551-559`) inspects `rel.parts`,
which pathlib does not normalise, so a first component of `tests` is enough:

```
  bin/newfile.py                        exit=2  BLOCKED
  tests/../bin/newfile.py               exit=0  ALLOWED
  tests/../bin/moltke.py                exit=0  ALLOWED
  /abs/path/tests/../bin/newfile.py     exit=2  BLOCKED
```

Absolute paths are safe because `mode_pre_write` (`bin/moltke.py:568`) resolves
them first; only the relative branch keeps `..` intact.

Not confirmed: whether Claude Code ever sends a relative `tool_input.file_path`.
Its `Write` tool documents an absolute path, and I did not attempt a live probe —
a probe that succeeds leaves a file in the repository and contaminates this run.
So this is reachable for certain through the documented `--pre-write PATH`
argument, which `MANUAL.md:128` presents as a mode other tools may call, and
unproven through the hook.

Impact: low. The fence is already not the guarantee (DEC-022), and the same
reviewer holds `Bash`. Recorded because it is a hole in the half of the fence that
is claimed to work, and it costs one `resolve()` to close.

Suggested resolution: normalise before matching — resolve relative paths against
`root` in `mode_pre_write` and reject any `rel` containing `..`. Not applied here.

### 2026-08-07_adversarial-F11  low  the `test_command` refusal writes to both streams, against the documented mapping

Status: open

Evidence: `run_test_command` prints the banner to stdout (`bin/moltke.py:953`)
and refuses on stderr (`bin/moltke.py:971`):

```
--- done with a failing suite: exit=1
  stdout: moltke: running the suite gate: exit 3
  stderr: moltke: the "test_command" gate failed with exit 3: exit 3
          last 20 lines:
          Fix the suite. Never weaken a test to get past this
```

`README.md:75` assigns the `test_command` gate to the "refusals ... stderr" row,
and `tests/test_s025_exit_codes.py:57-61` encodes that as
`assertFalse(result.stdout.strip(), "a refusal must not go to stdout")`. The
three cases in `TestRefusalsGoToStderr` are a step refusal, an unknown operation,
and `--audit check` without a baseline; the `test_command` refusal, the one path
that would fail the assertion, is not among them.

Impact: minor for humans, real for the script `MANUAL.md:149-151` invites — a
consumer that follows the documented rule and reads stderr on exit 1 gets the
refusal, so nothing is lost; one that switches streams on exit code sees partial
output. The larger point is that S025's own test states a rule the code breaks and
avoids the case that proves it.

Suggested resolution: send the banner to stderr with the rest of the refusal, or
document the gate as producing both, and add the case to
`TestRefusalsGoToStderr` either way. Not applied here.

## What was checked and found sound

Recorded so a later run knows this ground was covered, and so the findings above
are not read as a verdict on the whole of S014..S026.

- **The new tests are not vacuous.** Each new behaviour was removed in a copy of
  the repository outside it and the suite re-run. Twelve mutations, twelve reds,
  no survivors: deleting the `Stop` hook event and adding a fourth skill both fail
  the golden; dropping INV-3's reverse direction fails
  `test_inv3_plan_id_with_no_step_file`; making `reviewer_may_write` return `True`
  fails four fence tests; removing the `adocs/` mkdir from `--log-prompt` fails
  `test_prompt_survives_a_missing_docs_directory`; making `recap_pending` return
  `False` fails four Stop tests; removing either history baseline fails the S018
  tests; reading `decisions.md` raw again fails three S019 tests; removing the
  `test_command` gate call fails both S021 tests; restoring the same-day refusal
  fails three S020 tests; reverting INV-10's stem match to `startswith` fails
  `test_a_rerun_finding_id_does_not_satisfy_the_first_report`; turning
  `audit_check`'s unexpected list into the expected one fails four S017 tests.
- The S020 sequence suffix behaves under repetition: three consecutive
  `--audit new adversarial` calls give `.md`, `.2.md`, `.3.md`, no overwrite, each
  template naming its own stem.
- `--audit check` correctly catches the uncommitted cases: source edit, modified
  existing test, second edit to an already-dirty file, and a pre-existing change
  reverted. Pre-existing dirt is not blamed on the run.
- The `test_command` gate runs after every other gate and before any mutation: a
  refusal leaves the step in `plan_current/` with no `done:` stamp written.
- The gate's timeout path is clean where it is most likely not to be: a command
  that spawns a surviving child and holds the pipe still returns at the timeout
  (3.0s against a 3s limit in an instrumented run) rather than hanging in
  `communicate()`.
- INV-7's history check reads a committed deletion as well as a committed
  modification, and `--no-renames` keeps a move *into* `plan_done/` legal.
- `strip_guidance` is now applied in `finding_references`; F05's exception is
  gone, and an HTML-comment mention is stripped the same way.
- The worklog secret detector is non-vacuous by construction and quiet on the
  benign shapes this worklog is full of (git shas, md5 digests, UUIDs, the
  `BEGIN CERTIFICATE` header).
- `README.md`'s "173 tests, no skips" is accurate at this commit.

## Post-report verification, 2026-08-07

Added after the findings above were written. No finding is altered; this records
what happened when the report was first saved to disk, which upgrades F02 from
reproduced-in-a-fixture to reproduced-in-production.

**F02 fired on this report.** The first save of this file contained eleven
findings. The `PostToolUse` hook reported two:

```
moltke: INV-10: open finding 2026-08-07_adversarial-F01 in
2026-08-07_adversarial.md has no step closes: reference ...
moltke: INV-10: open finding 2026-08-07_adversarial-F02 in
2026-08-07_adversarial.md has no step closes: reference ...
```

and `--audit list` agreed, listing F01 and F02 and nothing else:

```
2026-08-07_adversarial.md
  2026-08-07_adversarial-F01  open  (no reference)
  2026-08-07_adversarial-F02  open  (no reference)
moltke: 2 open finding(s) have no plan step and no decision.
```

F03 through F11 — including three of the four high findings — were invisible to
INV-10 and to `--audit list`. The cause is exactly what F02 describes: the file
held 39 triple-backtick markers, an odd number, because three lines of prose
quoted a marker inside an inline code span while discussing the defect. Five
stray markers shifted the pairing and `strip_guidance` deleted nine findings
before `report_findings` ever saw them.

Two things follow. First, the finding is not theoretical: the very first
real-world document to hit it was the report describing it, written by an agent
following the report format the repository ships. Second, INV-10's guarantee —
that a finding cannot be filed and forgotten — silently held for two of eleven
findings while `--validate` and the hook both behaved as though they had checked
the file.

The three offending lines were then reworded to describe the markers instead of
quoting them, which is the only change made to this report after the hook ran. No
finding text, severity, evidence, or status was altered. `--audit list` now sees
all eleven.
