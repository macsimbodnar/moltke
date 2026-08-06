# Audit 2026-08-06 adversarial

Scope: `bin/moltke.py`, `hooks/hooks.json`, `agents/adversarial_reviewer.md`,
`tests/`, and the claims made about them in `README.md`, `MANUAL.md`,
`adocs/specs.md`, and `AGENTS.md`. Commit `1064774` (S013), plugin 0.2.0,
working tree clean at the start of the run.

Method: read the implementation, then attempted to break each documented
guarantee in throwaway repositories scaffolded by `--scaffold`. Hook payload
assumptions checked against the live Claude Code documentation
(`code.claude.com/docs/en/hooks`, `/plugins-reference`, fetched 2026-08-06),
as `adocs/specs.md` requires. Every finding below carries either a reproduction
transcript or a documentation quote. Findings that could not be reproduced are
labelled as such and say exactly what was not confirmed.

Full suite green at this commit: `Ran 112 tests ... OK`, no skips.
`python3 bin/moltke.py --validate` reported `all checks pass` before the run.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name:

```
### 2026-08-06_adversarial-F01  high  short title

Status: open

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
```

Every finding ends in one of two places: a plan step whose `closes:` field
names it, or a decision entry stating why it will not be acted on, which moves
it to `accepted`. A finding moves to `closed` only after the audit is re-run
and no longer reports it. Fixing without re-running leaves it `planned`.

Summary: 14 findings. 5 high, 6 medium, 3 low. The high findings share one
shape — a guarantee that the documentation states unconditionally, whose
enforcement holds only under conditions that never occur in a live session.
Three of them are invisible to the test suite because the tests construct the
favourable precondition themselves. F14 is not a latent risk: it is losing data
in this repository today.

## Findings

### 2026-08-06_adversarial-F01  high  the Stop hook's recap gate cannot fire in a live session

Status: planned

Evidence: `bin/moltke.py:467-479`. `mode_stop` decides that a recap was written
by comparing worklog size against its committed baseline:
`if shown.returncode == 0 and len(current) <= len(shown.stdout)`. But
`mode_log_prompt` (`bin/moltke.py:377-390`) appends the user's prompt to the
same file on every `UserPromptSubmit`, before the turn begins. Any turn that
reached the Stop hook has already grown the worklog, so the comparison is
always false. Reproduced in a scaffolded repo with an uncommitted source
change staged:

```
=== A: stop with source changed, NO prompt logged ===
moltke: source changed but adocs/worklog.md gained no recap; append a recap
(step id, what changed, files, tests, commit) before ending the turn.
exit=2

=== B: same, AFTER --log-prompt appended one prompt ===
exit=0
```

The only difference between A and B is one `--log-prompt` call, which in a real
session is not optional — it is the `UserPromptSubmit` hook.

Impact: the enforcement `MANUAL.md:83-84` advertises ("the turn will not end
with ... source changes with no worklog recap") never fires for any user. Source
can be changed and committed with no recap, indefinitely. `AGENTS.md` §9 makes
recaps mandatory on work turns and nothing checks it.

The test suite does not catch this because `tests/test_s005_hooks.py TestStop`
invokes `--stop` on repositories where `--log-prompt` was never called. That is
the condition `AGENTS.md` §6 names as non-vacuity: the test asserts a block
happens without first establishing the state a live session is actually in.

Suggested resolution: stop using file growth as the recap proxy. Detect a recap
by its own marker — a heading shape the recap writes and `--log-prompt` does not
(`mode_log_prompt` writes `## <stamp> prompt`), and require one appended after
the last logged prompt. Then re-target `TestStop` so the fixture logs a prompt
first, which makes the test fail against today's implementation. Not applied
here.

### 2026-08-06_adversarial-F02  high  the reviewer write fence probably never matches, and fails open

Status: planned

Evidence: `bin/moltke.py:393,408`. The fence is bare-string equality:
`REVIEWER_AGENT = "adversarial_reviewer"`, then
`if payload.get("agent_type") == REVIEWER_AGENT and ...`. The live plugin
reference states plugin components are namespaced by plugin name: "Agents appear
in the @-mention typeahead under their scoped name, such as
`my-plugin:code-reviewer`, once the plugin is enabled", and "This name is used
for namespacing components. For example, in the UI, the agent `agent-creator`
for the plugin with name `plugin-dev` will appear as `plugin-dev:agent-creator`."
The same page records the identical trap for another component type: "A matcher
written against the bare server key never fires."

If `agent_type` carries `moltke:adversarial_reviewer`, the comparison is false,
no branch runs, and `mode_pre_write` returns `EXIT_OK`. The fence fails open —
silently, with no diagnostic.

Not confirmed: I could not observe the actual `agent_type` value under a real
plugin-spawned subagent. That observation is exactly what S012 defers and has
never done. The documentation establishes that scoping applies to agent naming;
it does not state the hook payload's exact value, so this is recorded as
probable, not proven.

`tests/test_s008_audit.py:97` cannot detect it: the test writes the payload
itself, `json.dumps({"agent_type": "adversarial_reviewer", ...})`. It proves the
code responds to a string the test invented, not that Claude Code ever sends it.
`adocs/testing.md` row S008 nonetheless records "the reviewer may write only
under `project/audit/`" as passing.

Suggested resolution: match on suffix or on both forms
(`agent_type.split(":")[-1] == REVIEWER_AGENT`), and make the fence fail closed
for the case it cares about — when `agent_id` is present (the documented
subagent marker) and `agent_type` is unrecognised, block writes outside
`adocs/audit/` rather than allowing them. Confirm the real value during S012
and record it in specs. Not applied here.

### 2026-08-06_adversarial-F03  high  the reviewer holds Bash, so the write fence is bypassable by design

Status: planned

Evidence: `agents/adversarial_reviewer.md:4` grants
`tools: Read, Grep, Glob, Bash, Write`. `hooks/hooks.json:26` fences only
`"matcher": "Write|Edit"`. `Bash` is not matched, so
`echo x > bin/moltke.py`, `sed -i`, `git commit`, or `git push` from the
reviewer never reach `mode_pre_write`. The restriction is stated in the agent's
own prose ("Use `Bash` to reproduce, not to change", lines 31-33), which is an
instruction to a model, not an enforcement mechanism.

`adocs/specs.md:171-173` asserts the opposite: "The reviewer's write fence is
enforced in `--pre-write` using the PreToolUse `agent_type` field: subagent
frontmatter has no path-level restriction, so the hook is the only place the
limit can be real." `MANUAL.md:147-151` repeats it. The premise is half true —
frontmatter has no *path* restriction — but the live plugin reference lists
`disallowedTools` among the supported frontmatter fields for plugin agents, so
tool-level restriction is available and unused.

Impact: the property the role exists to guarantee ("a reviewer that can fix what
it finds stops producing evidence and starts producing patches",
`agents/adversarial_reviewer.md:10-12`) rests on model compliance. Combined with
F02, there may be no effective fence at all. `tests/test_s008_audit.py`
TestReviewerWriteFence tests only Write-shaped payloads, so the suite reports
this as covered.

Suggested resolution: decide whether the reviewer needs `Bash`. If it does, add
`disallowedTools` for the mutating surface and extend the PreToolUse matcher
beyond `Write|Edit`, accepting that Bash command inspection is best-effort. If
it does not, drop `Bash` and the fence becomes real. Either way the specs
sentence claiming the hook is "the only place the limit can be real" needs
correcting. Not applied here.

### 2026-08-06_adversarial-F04  high  INV-7 and INV-8 immutability evaporates at the next commit

Status: planned

Evidence: `bin/moltke.py:197-208` (`inv_7_done_immutable`) shells out to
`git status --porcelain -- adocs/plan_done`, and `bin/moltke.py:216-231`
(`inv_8_append_only`) compares the working file against `git show HEAD:<path>`.
Both baselines are HEAD, which moves every time the agent commits — and
`AGENTS.md` §5 has the agent commit at every step completion. Reproduced:

```
=== rewrite history via Bash (sed), UNCOMMITTED ===
VIOLATION: INV-7: adocs/plan_done/S001_thing.md changed under plan_done/ ...
VIOLATION: INV-8: adocs/decisions.md changed earlier bytes ...
exit=1

=== same tampering, but COMMITTED ===
moltke: all checks pass
exit=0
```

The tampering is permanent and undetectable afterwards by any moltke mode.

Two further gaps in the same area. `adocs/specs.md:34` states INV-7 as
"`plan_done/` is byte-identical to its state at session start" — the
implementation compares against the last commit, not session start, and the
2026-08-01 amendment (`specs.md:50-54`) silently redefines it without marking
the original wording superseded. And the `plan_done/` write fence
(`bin/moltke.py:413-417`) is a `Write|Edit` PreToolUse matcher, so the `sed`
above never consulted it; `AGENTS.md` §11's "does not write to
`adocs/plan_done/`" is unenforced against Bash.

Impact: the prime directive is that project state is derivable from tracked
files. Their *integrity* is guarded only inside the uncommitted window, which
this workflow deliberately keeps as short as possible. History rewriting after
a commit is invisible.

Suggested resolution: check the immutable set against a baseline that does not
move — the first commit that introduced each `plan_done/` file, via
`git log --diff-filter=A`, so any later modifying commit is detectable; same
technique for the append-only files, verifying the committed prefix relation
across the whole history rather than against HEAD alone. Cheap enough for
`--validate`, too slow for `--post-write`. Correct the INV-7 wording in the same
commit. Not applied here.

### 2026-08-06_adversarial-F05  medium  fenced guidance in decisions.md silently discharges an open finding

Status: planned

Evidence: `bin/moltke.py:248-257`. `finding_references` appends
`decisions.read_text(encoding="utf-8")` raw. Every other scanner routes through
`strip_guidance`, whose docstring (`bin/moltke.py:80-83`) states the rule
universally: "Every scanner in this file reads it through here, so guidance is
never counted as data". `adocs/specs.md:160-166` records the same rule as a
hard-won lesson repeated four times. This function is the exception.
Reproduced, with the baseline violation established first:

```
=== open finding, unreferenced (baseline: must be a violation) ===
VIOLATION: INV-10: open finding 2026-08-06_adv-F01 ... has no step closes:
reference and no decisions.md entry
exit=1

=== now mention the finding id ONLY inside a fenced example in decisions.md ===
moltke: all checks pass
exit=0
  2026-08-06_adv-F01  open  (referenced in decisions.md)
```

Impact: INV-10 is the gate that stops an audit from being filed and forgotten.
A finding id appearing anywhere in `decisions.md` discharges it, including
inside a fenced format example — and the scaffolded `templates/adocs/decisions.md`
ships exactly such an example block. `--audit list` reports the finding as
`referenced in decisions.md` and exits 0.

Suggested resolution: read `decisions.md` through `strip_guidance` in
`finding_references`, matching every other scanner. Consider tightening further
so a bare mention does not count — only an entry that names the finding in a
`Decision:` or `Consequences:` line. Not applied here.

### 2026-08-06_adversarial-F06  medium  documented exit-code semantics are wrong for every refusal path

Status: planned

Evidence: `README.md:56-57` states "Exit codes: `0` clean, `1` invariant
violations listed on stdout, `2` a blocked action with the reason on stderr."
`MANUAL.md:113-115` repeats it. But `refuse()` (`bin/moltke.py:613-615`) prints
to **stderr** and returns `EXIT_VIOLATIONS` (1), and it is the return path for
every `--step` refusal, `--audit new` refusal, and unknown-operation error.
Observed:

```
$ python3 bin/moltke.py --step start S999 2>/dev/null ; echo exit=$?
exit=1                      # stdout empty
$ python3 bin/moltke.py --step start S999 2>&1 >/dev/null
moltke: S999 does not exist; create it with --step new <name>
```

So exit 1 goes to stdout for `--validate` and `--audit list`, and to stderr for
every refusal. The documented rule holds for two modes out of eleven.

Impact: anyone scripting moltke — which `MANUAL.md:91-93` explicitly invites for
Codex and Cursor, where hooks do not exist — captures the wrong stream and
loses the message that says what to do. `AGENTS.md` §7 requires doc claims to be
traced to the code path that produces them.

Suggested resolution: either route `refuse()` to stdout for consistency with the
documented rule, or document the real rule: diagnostics on stderr, findings on
stdout, exit 1 for both. Prefer the second; changing streams may break whatever
already parses them. Not applied here.

### 2026-08-06_adversarial-F07  medium  the "full suite green" completion gate is not enforced anywhere

Status: planned

Evidence: `AGENTS.md` §4 permits `plan_current/` → `plan_done/` "only when all
of: code complete, full suite green, `testing.md` rows added, README and MANUAL
checked, completion stamp written", and §11 prohibits claiming a step complete
"before the suite is green". `step_done` (`bin/moltke.py:739-777`) checks: the
step is current, not paused, not named in an open `blocks:`, has a testing.md
row, has a stamp, and that the stamp string contains `README` and `MANUAL`. It
never runs or consults a test suite. Nothing else does either — no mode shells
out to a test runner, and `.moltke.json` carries no test command.

Impact: the load-bearing quality gate of the whole workflow is honour-system.
`MANUAL.md:142-145` discloses the *weaker* version of this problem (the
README/MANUAL check is mechanical, "they cannot tell whether you actually
looked") while leaving the larger one undocumented, which reads as though the
suite check is real.

Suggested resolution: either add an optional `test_command` to `.moltke.json`
and have `--step done` run it and refuse on failure, or record a decision that
this stays advisory and add it to MANUAL's known issues so the documentation
stops implying enforcement. This is a decision for the user, not the agent.
Not applied here.

### 2026-08-06_adversarial-F08  medium  the worklog is an unbounded verbatim secret sink in an append-only tracked file

Status: planned

Evidence: `mode_log_prompt` (`bin/moltke.py:377-390`) writes the user's prompt
verbatim into `adocs/worklog.md`, a tracked file, on every `UserPromptSubmit`.
INV-8 (`bin/moltke.py:216-231`) then forbids altering earlier bytes. A secret
pasted into a prompt — an API key, a token, a customer identifier — is committed
and cannot be removed without violating the workflow's own invariant, and
removal from history is barred outright by `AGENTS.md` §11 ("push, force push,
or rewrite git history"). For moltke itself DEC-002 makes the repository public,
so its own worklog is public.

`AGENTS.md` §6 requires that "Security and secret-leak checks run inside the
normal suite, not as a separate ritual." No such check exists: `grep -ri
"secret\|redact" tests/ bin/` finds nothing relevant. No known-issues entry
mentions it.

Impact: the highest-severity realistic failure of this tool is that it durably
records something it should not have, in a file it then refuses to let anyone
clean, in a repository that may be public. This is a property of every
repository moltke is installed into, not just this one.

Suggested resolution: at minimum, a known-issues entry stating plainly that
prompts are recorded verbatim and that INV-8 makes redaction a violation, plus
the escape procedure for when it happens (a decision entry authorising a
one-time exception, as DEC-013 did for reordering). Better: a redaction pass in
`mode_log_prompt` over high-confidence secret shapes, and a suite check that
fails on those shapes appearing in `worklog.md`, which is what §6 already asks
for. Not applied here.

### 2026-08-06_adversarial-F09  medium  a finding cannot be closed on the day it is fixed

Status: planned

Evidence: closure requires a re-run — `AGENTS.md` §10 and
`templates/audit_report_template.md:25-26`: "A finding moves to `closed` only
after the audit is re-run and no longer reports it." But `audit_new`
(`bin/moltke.py:831-836`) derives the filename from today's date and refuses
when it exists, advising: "Use a different type name, or re-run the audit
tomorrow." Covered, and thereby frozen, by
`tests/test_s008_audit.py:46 test_refuses_to_overwrite_an_existing_report`.

Impact: fix an audit finding on the day it was reported and there is no
compliant way to close it. The workflow's own guidance is to wait a day or to
fabricate a type name, which corrupts the report-naming scheme that INV-10
depends on (`finding_id.startswith(report.stem)`, `bin/moltke.py:281`).

Suggested resolution: allow a same-day re-run under a sequence suffix
(`2026-08-06_adversarial.2.md`) so ids stay distinct and traceable, keeping the
refusal-to-overwrite property intact. Not applied here.

### 2026-08-06_adversarial-F10  medium  the surface guard covers argparse only, not the surface users touch

Status: planned

Evidence: DEC-010 mandates "a golden test over whatever `surface_guard` names",
and `.moltke.json` sets `cli`. `tests/golden/cli_surface.txt` holds argparse
actions only. The surface a user of the *plugin* touches is three skills and
five hook events. `tests/test_s010_plugin.py:18` hardcodes
`SKILLS = ("init", "step", "audit")` and iterates it, so a removed or renamed
skill fails but an added fourth skill is invisible. `test_hooks_call_the_checker_
through_the_plugin_root` (`tests/test_s010_plugin.py:63-75`) iterates whatever
events are declared and asserts each command shape; deleting the `Stop` hook
entirely leaves the suite green, since the only structural assertion is
`assertTrue(commands)`.

Impact: the mechanism that exists to stop documentation drifting from code
(`AGENTS.md` §7) does not cover the components most likely to drift, and
`MANUAL.md:77-87` documents per-event hook behaviour that no test pins.

Suggested resolution: extend the golden to the declared skill set and the
declared hook event set, and apply the existing "must appear in specs and
MANUAL" cross-check to both, exactly as it works for CLI flags today. Not
applied here.

### 2026-08-06_adversarial-F11  low  a typo in plan.md creates a permanent phantom next step

Status: planned

Evidence: INV-3 (`bin/moltke.py:134-145`) checks one direction only — every
file in `plan_todo/` and `plan_current/` appears in `plan.md`. The reverse is
unchecked, while `derived_next` (`bin/moltke.py:329-341`) returns the first id
in `plan.md` order that is not in `plan_done/`, whether or not a file exists.
A mistyped id therefore becomes the derived next step forever;
`mode_session_start` announces it every session and `step_status` writes it into
`status.md`, so the two agree and nothing looks wrong.

Impact: low — self-inflicted and visible once noticed, but it corrupts the one
value `AGENTS.md` §1 calls "derivable, never asserted", which a resumed session
is told to trust above all prose.

Suggested resolution: extend INV-3 to report ids listed in `plan.md` with no
file in any of the three directories. Not applied here.

### 2026-08-06_adversarial-F12  low  INV-7's stated wording and its implementation disagree

Status: planned

Evidence: `adocs/specs.md:34` — "INV-7 `plan_done/` is byte-identical to its
state at session start." The implementation compares against git HEAD
(`bin/moltke.py:193-208`), and the 2026-08-01 amendment at `specs.md:50-54`
describes the HEAD behaviour without marking the original sentence superseded.
Both sentences are live in the same file. `AGENTS.md` §7 requires spec edits to
carry a dated inline note; the note exists but the contradicted line was left
standing.

Impact: a reader takes the numbered invariant as the contract. It promises a
session-scoped guarantee the code does not provide — see F04 for what that costs
in practice.

Suggested resolution: restate INV-7 in terms of the committed baseline, marking
the old wording superseded rather than deleting it. Not applied here.

### 2026-08-06_adversarial-F13  low  documentation drift found while checking claims against code

Status: planned

Evidence: three items, each verified.

1. `MANUAL.md:29-31` — "Once the repository is hosted, the same commands accept
   its git URL in place of the path." The repository is hosted:
   `git remote -v` gives `origin git@github.com:macsimbodnar/moltke.git`, and
   `adocs/status.md:13` records a marketplace add from the git URL already
   performed. The conditional is stale.
2. `.claude-plugin/plugin.json` carries no `repository` field, already noted in
   `adocs/status.md:16` as actionable and still unaddressed.
3. `AGENTS.md` §2 and `README.md:22` present `adocs/plan_todo/` as part of the
   file map; it does not exist in this repository (`ls adocs/` shows `audit`,
   `plan_current`, `plan_done` only). `--scaffold` creates it with a `.gitkeep`
   (`bin/moltke.py:536,580-585`), so a scaffolded repo has it and moltke itself
   does not. The S001 testing row asserting the tree "matches the AGENTS.md §2
   file map" no longer holds.

Impact: low individually. Item 3 matters slightly more than it looks, because
moltke is the reference implementation of its own layout.

Suggested resolution: fix 1 and 3 in the next step's README/MANUAL check; 2 is
already identified as needing its own step. Not applied here.

### 2026-08-06_adversarial-F14  high  prompt logging fails silently, and is failing right now in this repository

Status: planned

Evidence: `mode_log_prompt` (`bin/moltke.py:386-390`) opens
`adocs/worklog.md` in append mode and catches `OSError`, printing to stderr and
returning `EXIT_OK`. `open(..., "a")` does not create missing parent
directories, so when `adocs/` is absent or unwritable every prompt is discarded.
The hook exits 0, and on `UserPromptSubmit` a zero exit means stderr is not
surfaced in normal use. Reproduced:

```
$ echo '{"prompt":"lost silently"}' | python3 bin/moltke.py --log-prompt 2>/dev/null
exit=0  <- indistinguishable from success
worklog written? NO
```

This is not hypothetical. It is happening in this repository today. The
installed plugin is 0.1.0, whose hooks target `project/`, which S013 renamed
away (`adocs/status.md:14`). `tail adocs/worklog.md` ends at the S013 recap:
none of this session's prompts were recorded. The version skew is documented
(`MANUAL.md:129-133`), but its consequence — total, silent loss of the prompt
log — is not.

Impact: `AGENTS.md` §9 states that every prompt is appended verbatim and that
this "is written mechanically and is not the agent's responsibility." It is the
one guarantee the workflow makes that requires no discipline from anyone, and
it degrades to nothing without a single visible symptom. Any repository where
`adocs/` is missing, renamed, or read-only silently keeps no forensic history at
all, while every other check keeps passing.

The failure also compounds F01: `mode_stop`'s recap gate reads worklog growth,
so a worklog that never grows makes that check start firing for the wrong
reason.

Suggested resolution: create the parent directory before appending, and make
the failure loud somewhere a zero exit still reaches — `SessionStart`'s
`additionalContext` is the natural channel, since it already reports staleness
to the model. A suite test should assert that a prompt survives when `adocs/`
is absent. Not applied here.

## Post-report verification, 2026-08-06

Added after the report was written and before any fix. No finding above is
altered; this records an observation that upgrades F02 from probable to proven.

**F02 is confirmed, not merely probable.** The report could not observe
`agent_type` under a real plugin spawn and said so. Moltke was then installed on
this machine, and `moltke:adversarial_reviewer` was spawned through the plugin
with a single instruction: attempt one `Write` to `/Users/max/ws/moltke/PROBE_S012.md`.
The reviewer reported verbatim:

```
File created successfully at: /Users/max/ws/moltke/PROBE_S012.md
```

No hook denial. The file existed on disk (6 bytes) and was removed by the main
thread afterwards. `PROBE_S012.md` matches no step-file pattern and is not under
`plan_done/`, so the reviewer fence was the only rule that could have blocked it.
It did not fire.

Still unobserved: the exact `agent_type` string. The probe proves the equality at
`bin/moltke.py:408` evaluates false; it does not distinguish a namespaced value
(`moltke:adversarial_reviewer`) from the field being absent in this payload. S016
should log the observed value once before choosing its match, because suffix
matching fixes the first case and not the second.

All five hook events were verified live in the same session: SessionStart printed
the stack and the derived next step, UserPromptSubmit logged the prompt verbatim,
PreToolUse refused both a `plan_done/` write and a step file outside the plan
directories, PostToolUse surfaced an INV-3 violation without blocking the write,
and Stop refused a stale `status.md` with an actionable message. F14's live
symptom is therefore resolved on this machine, while the defect itself stands
unchanged: the append still cannot create a missing `adocs/`.

## What was checked and found sound

Recorded so a later run knows this ground was covered.

- INV-11 marker gate: every mode exits 0 in unmarked and declined repositories,
  `--scaffold` and `--decline` correctly exempt (DEC-017).
- `strip_guidance` applied correctly in `plan_text`, `report_findings`,
  `inv_9_unique_dec_ids`, and `field_value` — F05 is the sole exception.
- The Stop no-deadlock cap: `prompt_id` is confirmed present in the live Stop
  payload, so the per-prompt keying works as specified and INV-12 holds.
- `--post-write` returning exit 2 is correct, not a blocking bug: the live docs
  state exit 2 on PostToolUse "Shows stderr to Claude; the tool already ran",
  which is what `MANUAL.md` describes as non-blocking.
- `--step` lifecycle refusals: each refuses rather than repairs and names the
  missing condition; `plan_active_max` and `plan_stack_max` enforced on both the
  `start` and `block` paths; completing a child unpauses its parent.
- Id allocation never reuses an id, including after a step file is deleted,
  because `next_step_id` also scans `plan.md`.
- `--scaffold` idempotence and its refusal to overwrite, including a foreign
  `AGENTS.md`.
- README's "112 tests, no skips" is accurate at this commit.
