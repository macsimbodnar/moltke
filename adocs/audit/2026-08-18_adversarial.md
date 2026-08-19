# Audit 2026-08-18 adversarial

Scope: the whole shipped plugin at commit 724a5a8 — `bin/moltke.py`,
`hooks/hooks.json`, `skills/`, `agents/adversarial_reviewer.md`, `templates/`,
`.claude-plugin/`, `tests/`, and `README.md` / `MANUAL.md` treated as claims
about code. Extra depth on the never-audited surface: `--watch` (S014) and
`--pre-command` (S015). Older lifecycle code (`--step`, `--audit`, invariant
checks, Stop logic, scaffold) also in scope.

Method: read every source file; ran the full suite at HEAD (141 pass); built
throwaway git repos under a scratch dir and drove `bin/moltke.py` against them
to reproduce each defect from an exit code or a file state — never mutating
this repo or arming a watcher in it. Hook payload field names were checked
against the current Claude Code hook documentation (code.claude.com/docs) via a
docs lookup; where a finding rests on that rather than on a live hook firing,
it says so.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name:

```
### 2026-08-18_adversarial-F01  high  short title

Status: planned

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
```

Every finding ends in one of two places: a plan step whose `closes:` field
names it, or a decision entry stating why it will not be acted on, which moves
it to `accepted`. A finding moves to `closed` only after the audit is re-run
and no longer reports it. Fixing without re-running leaves it `planned`.

## Findings

### 2026-08-18_adversarial-F01  high  --log-prompt reads `prompt`; live UserPromptSubmit sends `user_prompt`, so the worklog is never written

Status: accepted

`mode_log_prompt` reads the user's text from the `prompt` key:

```
bin/moltke.py:389   prompt = hook_input().get("prompt", "")
```

Per the current Claude Code hook docs (code.claude.com/docs/en/hooks), the
UserPromptSubmit payload carries the user's text in `user_prompt`, not
`prompt`; the documented top-level fields are `session_id`, `prompt_id`,
`transcript_path`, `cwd`, `hook_event_name`, `user_prompt`, `turn_number`.
There is no `prompt` field. Reproduced against a marked repo, feeding each
field name on stdin:

```
$ printf '{"user_prompt":"hello from user_prompt"}' | moltke.py --log-prompt ; echo exit=$?
exit=0
$ cat adocs/worklog.md
# Worklog                         # <-- unchanged, nothing appended
$ printf '{"prompt":"hello from prompt"}' | moltke.py --log-prompt ; echo exit=$?
exit=0
$ cat adocs/worklog.md
# Worklog

## 2026-08-18T16:21+02:00 prompt

> hello from prompt
```

The S005 test hides this: it feeds the same wrong key the code reads, so it
passes while the live hook does not (a vacuous test w.r.t. the real payload):

```
tests/test_s005_hooks.py:38   payload = json.dumps({"prompt": "first line\nsecond line"})
```

Impact: in a live Claude Code session the UserPromptSubmit hook appends nothing
to `adocs/worklog.md`. Because `--log-prompt` always exits 0 by design (exit 2
would erase the prompt), the failure is completely silent. AGENTS.md §9 ("every
prompt is appended verbatim ... written mechanically") and the prime directive's
durable-memory claim are broken for every marked repository on the current
Claude Code. What I could not confirm first-hand: I did not run a live
UserPromptSubmit hook to capture the exact wire payload; the finding rests on
the current documented field name plus the reproduced fact that the code keys on
`prompt` and ignores `user_prompt`. The spec's "verified against live hook docs"
note is dated 2026-08-01, so the field likely drifted (or was mis-verified).

Suggested resolution: read `user_prompt` with `prompt` as a fallback
(`hook_input().get("user_prompt") or hook_input().get("prompt", "")`), and
change the S005 test to feed `user_prompt` so it exercises the real field.

### 2026-08-18_adversarial-F02  high  --watch ceiling does not bound a single scan; a caller regex that backtracks runs forever

Status: closed

The watch loop scans the whole log with the caller-supplied regex, then sleeps;
the ceiling deadline is only checked *between* polls, never during a scan:

```
bin/moltke.py:709   text = log_path.read_text(encoding="utf-8", errors="replace")
bin/moltke.py:712   match = pattern.search(text) if pattern else None
bin/moltke.py:798   hit = _watch_scan(log_path, done_re, fail_re)
bin/moltke.py:812   remaining = deadline - time.monotonic()   # only reached after the scan returns
```

`done_re = re.compile(argv[1])` is whatever the caller passed; Python's `re` has
no backtracking guard. A pathological regex against a non-matching line hangs
inside `pattern.search` and the ceiling never fires. Reproduced in a scratch
dir (`(a+)+$` is classic catastrophic backtracking):

```
$ python3 -c "open('run.log','w').write('a'*30 + 'X\n')"
$ /usr/bin/time -v timeout 30 moltke.py --watch run.log '(a+)+$' --ceiling 1s --interval 5s
	Command exited with non-zero status 124
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:30.00
```

The `--ceiling 1s` watcher ran the full 30s and was killed by the outer
`timeout`, not by moltke. The same root cause makes a huge log a problem
regardless of regex: `read_text` pulls the entire file into memory on every
poll (O(filesize) per interval), also outside the deadline.

Impact: the whole reason `--watch` exists (DEC-022) is that it "terminates on
its own" and the ceiling "bounds every mistake in the other three exits"
(AGENTS.md §13). A caller regex that backtracks — a mistake, not an attack, and
regexes are exactly what callers hand-write — produces the leaked, never-exiting
watcher DEC-022 set out to make unarmable. INV-13's self-termination guarantee
fails.

Suggested resolution: bound each scan out-of-band from the poll loop — a
`signal.alarm`/`SIGALRM` watchdog around the scan (POSIX, already assumed by
`--pid`), or scan incrementally with a per-iteration deadline. At minimum,
document that the ceiling does not cover a runaway scan and reject obviously
catastrophic patterns is not sufficient; the alarm is.

### 2026-08-18_adversarial-F03  high  reviewer write fence covers only Write/Edit; the reviewer's Bash writes anywhere unfenced

Status: accepted

The reviewer is granted Bash and Write:

```
agents/adversarial_reviewer.md:4   tools: Read, Grep, Glob, Bash, Write
```

The write fence is a PreToolUse hook, wired only for the Write and Edit tools
(and Monitor). There is no Bash matcher:

```
$ python3 -c "import json;print([e.get('matcher') for e in json.load(open('hooks/hooks.json'))['hooks']['PreToolUse']])"
['Write|Edit', 'Monitor']
$ grep -c Bash hooks/hooks.json
0
```

`mode_pre_write` only ever sees a Write/Edit path; a Bash command such as
`echo ... > bin/moltke.py`, `sed -i`, `tee`, or `git checkout` is never
presented to it. So the reviewer can modify source, tests, specs, or git
history through Bash with nothing intercepting it.

The docs assert the opposite, as a hard guarantee, in several places:

```
agents/adversarial_reviewer.md:9   Your write access is limited to `adocs/audit/`. That limit is enforced
MANUAL.md:195                       confined to `adocs/audit/` by the PreToolUse hook reading `agent_type`
adocs/specs.md:185                  The reviewer's write fence is enforced in `--pre-write`
```

Impact: "the reviewer produces evidence, not patches" (mode_pre_write comment,
DEC-016's protected differentiator) is enforced only for Write/Edit. A reviewer
that malfunctions, or is steered by injected text in the very code it audits,
can rewrite anything in the repo via Bash. The MANUAL already flags the fence's
dependence on `agent_type`, but the Bash hole is undocumented and larger: it
does not even require the field to be absent. I confirmed this from the tool
grant and hook config; I did not spawn a live subagent to write a file (the CLI
has no way to simulate a reviewer Bash write), but no hook exists that could
intercept one.

Suggested resolution: either drop Bash from the reviewer's tools (Read/Grep/Glob
cover inspection; reproductions that must run commands are a gap to design for
deliberately), or add a PreToolUse Bash matcher that refuses, when
`agent_type == adversarial_reviewer`, any command that writes outside
`adocs/audit/` — and state plainly that command-level write detection is
best-effort, since a shell fence is not airtight.

### 2026-08-18_adversarial-F04  medium  --pre-command persistent lint is bypassed by the substring "moltke --watch" anywhere in the command

Status: closed

The persistent-arm check treats a watcher as the primitive whenever the command
string merely *contains* something matching `moltke ... --watch`:

```
bin/moltke.py:474   if tool_input.get("persistent") and not re.search(r"moltke(\.py)?\b[^|;&]*--watch\b", command):
```

It is a substring presence test, not a check that the executed pipeline is the
primitive. A leaking `tail -f | grep` arms as long as the token appears — e.g.
in a comment. Reproduced (Monitor arm, `persistent: true`):

```
# control: clean leak is correctly blocked
$ mono 'tail -f run.log | grep BOOM' | moltke.py --pre-command ; echo exit=$?
moltke: a persistent watcher arms only through the watch primitive (INV-13...)
exit=2
# bypass: same leak, trailing comment mentioning the primitive
$ mono 'tail -f run.log | grep BOOM  # prefer moltke.py --watch here' | moltke.py --pre-command ; echo exit=$?
exit=0
# bypass: harmless echo of the token before the real leak
$ mono 'echo moltke --watch ; tail -f run.log | grep BOOM' | moltke.py --pre-command ; echo exit=$?
exit=0
```

Impact: INV-13 states the leaked-watcher class is "unarmable ... refused unless
its command carries `MOLTKE_UNBOUNDED_OK`". In fact any command carrying the
incidental substring `moltke --watch` — a natural thing for an agent to write in
a TODO or comment ("# use moltke.py --watch for long runs") — silently disables
the persistent lint and arms exactly the leak DEC-022 targets. The undocumented
second escape hatch is strictly worse than the documented `MOLTKE_UNBOUNDED_OK`
one because it triggers by accident. (The single-match `grep -m N` branch runs
first and is not bypassed this way; only the persistent-unbounded path is.)

Suggested resolution: require the primitive to be the actual command, not a
substring — anchor on the command starting with (optphrase) `python3 ...
moltke.py --watch` after stripping a leading interpreter, or parse the first
pipeline segment; and ignore comments. Keep `MOLTKE_UNBOUNDED_OK` as the one
intended escape.

### 2026-08-18_adversarial-F05  medium  Stop README/MANUAL gate skips a completion staged as a git rename

Status: accepted

The Stop hook's mechanical README/MANUAL check inspects only porcelain lines
whose status is `??` (untracked) or `A ` (staged add):

```
bin/moltke.py:543   if line[:2] in ("??", "A ") and entry.startswith(f"{DOCS}/plan_done/"):
```

`git status --porcelain` reports a step moved into `plan_done/` and then staged
as a rename (`R `), and `entry = line[3:]` for that line is the arrow form
(`plan_current/... -> plan_done/...`), which also does not start with
`plan_done/`. Both conditions miss it. Reproduced with a realistic template-sized
step file completed by hand (`git mv` + fill the `done:` line with a stamp that
omits README/MANUAL), everything else satisfied:

```
$ git status --porcelain
R  adocs/plan_current/S003_active.md -> adocs/plan_done/S003_active.md
M  adocs/status.md
$ printf '{}' | moltke.py --stop ; echo STOP=$?
STOP=0                              # <-- allowed; gate did not fire
# control: identical completion left untracked instead of staged
$ printf '{}' | moltke.py --stop
moltke: adocs/plan_done/S003_active.md was completed without the README and MANUAL check recorded...
```

Impact: the spec and MANUAL present this gate as a real mechanical backstop for
hand-completed steps ("a step file newly moved into plan_done/ must mention
README and MANUAL in its done: stamp", specs S005 note; MANUAL known-issues).
The workflow itself says completed steps are "moved there with mv/git mv", and
`git add -A` before ending a turn is routine — that staging turns the move into
an `R ` the gate ignores. A step completed by hand (bypassing `--step done`,
which does enforce the stamp) can end a turn with no README/MANUAL check. INV-5
does not cover README/MANUAL either, so `--validate` will not catch it.

Suggested resolution: also handle `R ` status — split on ` -> ` and test the
destination against `plan_done/` — or scope the check with `git status
--porcelain -- adocs/plan_done` (which collapses the rename to `A ` on the
destination, as INV-7 already relies on) and parse from there.

### 2026-08-18_adversarial-F06  low  step ids silently stop being recognized past S999

Status: closed

Step files are recognized by `STEP_FILE_RE = ^(S\d{3})_...` — exactly three
digits — but `next_step_id` formats with `:03d`, which does not cap width:

```
bin/moltke.py:72    STEP_FILE_RE = re.compile(r"^(S\d{3})_[A-Za-z0-9_]+\.md$")
bin/moltke.py:886   return f"S{highest + 1:03d}"
```

```
$ python3 -c "...; print(bool(m.STEP_FILE_RE.match('S1000_x.md')))"
False
$ python3 -c "print(f'S{999+1:03d}')"
S1000
```

Impact: once a project reaches S999, `--step new` allocates `S1000`, writes
`plan_todo/S1000_*.md`, and lists it in `plan.md`, but `plan_steps` /
`STEP_FILE_RE` never see the file again: it is invisible to every invariant
(INV-1..INV-6), to `--pre-write`'s step-file fence, and to `derived_next`. The
id counter, computed from recognized files, is stuck at 999, so the next
`--step new` collides on `S1000` again. `\bS\d{3}\b` in `plan.md` also fails to
match `S1000`. Latent — a project needs 1000 steps — but it is a silent
structural break, not a refusal. This repo is at S015, far from it.

Suggested resolution: widen to `S\d{3,}` in `STEP_FILE_RE` and the `\bS\d{3}\b`
plan/id scans, or cap and refuse past S999 with a message instead of silently
mis-generating.

## Probed and held

Attacked and found sound (absence of a finding here is a tested negative, not an
omission):

- **INV-7 / staged completion.** Feared a legit `--step done` + `git add -A`
  would trip INV-7 (`plan_done` changed). It does not: `git status --porcelain
  -- adocs/plan_done` collapses the staged rename to `A ` on the destination, so
  INV-7 sees the one legal change (an addition). Verified in a scratch repo.
- **`strip_guidance` / template-as-data.** Commented example steps, findings,
  and `DEC-001` in the templates are correctly stripped before counting;
  `field_value` reads unfilled `<!-- ... -->` placeholders as empty. Re-derived
  from code and consistent with the S006/S007/S008 regression rows.
- **Malformed `.moltke.json`.** Non-JSON, non-dict, and junk field values are
  handled without a crash: `load_marker` returns `(None, [violation])`, `_limit`
  falls back to defaults on a non-dict config, and the enabled/absent gates still
  short-circuit. No traceback path found.
- **Damaged / malformed watch records.** `watch_records` skips files that fail
  to parse as a JSON object (try/except), so a corrupt record under
  `.git/moltke_watch/` degrades reporting rather than crashing session-start or
  stop.
- **`parse_duration` edge cases.** `0` and negatives are refused by mode_watch's
  `<= 0` guards; `1e3`, `0x10`, `nan`, `inf`, and blank all return None and are
  refused. No unbounded or zero-interval watcher slips through.
- **Stop block cap / INV-12 deadlock.** The cap keys on `prompt_id`, which the
  current docs confirm the Stop payload carries and which is stable across
  consecutive stops for one prompt; after 3 blocks the stop is allowed. Even if
  the field were absent (always `""`), the counter still advances and caps, so no
  deadlock. Held.
- **`--pre-command` single-match branch.** The `grep -m N` / `--max-count`
  follow is refused regardless of the `--watch` substring, since that branch runs
  before the persistent check and does not consult the token (only the persistent
  path is bypassable, F04).
- **`--pre-write` reviewer fence for Write/Edit.** For the Write/Edit tools the
  fence itself is correct: writes outside `adocs/audit/` by `agent_type ==
  adversarial_reviewer` are blocked, and paths outside the repo abstain. The gap
  is the ungated Bash tool (F03), not this branch.
- **Same-second watch record filenames.** Names are `{int(time)}_{pid}.json`;
  two live watchers collide only at identical second *and* identical pid, which a
  single process cannot produce concurrently. Not reproduced.
