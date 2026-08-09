# Live verification of the installed release — 2026-08-09

Type: verification, not an audit. No findings are recorded here because nothing
was hunted for; this file is the evidence S059 requires, written while the
observations were made.

Repository commit at the time of the run: `c2e6ad3`.
Session: Claude Code, this repository, plugin loaded from the user-scope install.

## 1. What runs is what is committed

`~/.claude/plugins/installed_plugins.json`, `moltke@moltke` entry, verbatim:

```json
{
  "scope": "user",
  "installPath": "/Users/max/.claude/plugins/cache/moltke/moltke/0.6.0",
  "version": "0.6.0",
  "installedAt": "2026-08-06T10:37:48.249Z",
  "lastUpdated": "2026-08-08T22:35:42.790Z",
  "gitCommitSha": "c2e6ad365819d64a381cf8b0cdb2c997560eafa8"
}
```

`gitCommitSha` is `c2e6ad3`, the HEAD of this checkout. The cached executable is
byte-identical to the one in the working tree:

```
85476988df0bee674ba9632ced5598fd6e6fdfa5  bin/moltke.py
85476988df0bee674ba9632ced5598fd6e6fdfa5  /Users/max/.claude/plugins/cache/moltke/moltke/0.6.0/bin/moltke.py
```

`.claude-plugin/plugin.json` in the cache reads `"version": "0.6.0"`.

This is what the step was waiting for. Every fix from S045 onward is live, not
inert. The reinstall itself was Max's, run as `claude plugin install moltke@moltke`
outside this session.

## 2. The five hook events

Hook wiring as installed, from the cache's `hooks/hooks.json`: `SessionStart`
(`--session-start`), `UserPromptSubmit` (`--log-prompt`), `PreToolUse` on
`Write|Edit` (`--pre-write`), `PostToolUse` on `Write|Edit` (`--post-write`),
`Stop` (`--stop`).

### SessionStart — observed

Emitted into the session context at open, verbatim:

```
moltke stack (plan_current/):
  S059: verify the installed release in a live session, after reinstall
Derived next step: S088 (first in plan.md order not in plan_done/).
status.md is stale (In progress says 'none', filesystem says 'S059 verify the installed release in a live session, after reinstall'); run bin/moltke.py --step status before working.
```

Three claims, all correct against the filesystem at that moment: the stack, the
derived next step, and the staleness of `status.md` left behind by the previous
session. The staleness call is the one worth noting — it is the §1 rule that the
directory beats the prose, working in a live session rather than in a test.

### UserPromptSubmit — observed

Every prompt of this session appears in `adocs/worklog.md`, verbatim, with a
timestamp, in order. Sample, verbatim:

```
## 2026-08-09T00:44+02:00 prompt

> it is not clear to me what are you doing. Should i do something or you will do the necessary tests?

## 2026-08-09T00:47+02:00 prompt

> go
```

### PreToolUse — observed refusing

A `Write` was attempted at `adocs/plan_done/S059_fence_probe.md`. Result,
verbatim:

```
PreToolUse:Write hook error: [python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --pre-write]: moltke: adocs/plan_done/S059_fence_probe.md is under plan_done/, which is immutable history. Completed steps are moved there with mv/git mv as the last action of a step; nothing inside is ever edited.
```

Nothing landed: `adocs/plan_done/` still held 84 entries, `ls adocs/plan_done/S059*`
matched nothing, and `git status --porcelain adocs/plan_done/` printed nothing.
The refusal is a refusal, not a partial write.

### PreToolUse, reviewer fence — observed against a real subagent spawn

This is the clause S012 and `2026-08-06_adversarial-F02` left unproven: the fence
had only ever been exercised with a synthetic payload, and F02 was precisely that
the real payload carries a scoped agent name the old bare equality never matched.

A `moltke:adversarial_reviewer` subagent was spawned and instructed to attempt one
write outside the fence and one inside it, to report both results verbatim, and to
use Bash only for a read-only `git status`.

Outside the fence, `adocs/probe_fence_outside.md`, verbatim:

```
PreToolUse:Write hook error: [python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --pre-write]: moltke: the adversarial_reviewer may write under adocs/audit/, and may create new files under tests/, and adocs/probe_fence_outside.md is neither. Record what you found as a finding in your report; fixes are planned as steps afterwards, by someone else.
```

Inside the fence, `adocs/audit/2026-08-09_fence-probe.md`, verbatim:

```
File created successfully at: /Users/max/ws/moltke/adocs/audit/2026-08-09_fence-probe.md (file state is current in your context — no need to Read it back)
```

Both sides were observed, which is what makes the block non-vacuous: the fence
discriminates by path rather than blocking every write the reviewer attempts. The
suffix match on the scoped name is what closes F02 — a live spawn, not a
constructed payload. The probe file under `adocs/audit/` was deleted after the
observation; it was scaffolding for this record, not a report.

### PostToolUse — observed silent on a clean tree

`--post-write` runs the cheap checks and prints only when one of them fails; on a
clean tree it exits 0 and emits nothing. Every `Write` and `Edit` in this session
ran it, and none produced output, which agrees with `bin/moltke.py --validate`
reporting `moltke: all checks pass` throughout. Its refusal path is not observed
here: producing one would mean introducing a real invariant violation into the
repository, which S059 excludes. That path is covered by the suite, not by this
record.

### Stop — observed silent on a clean tree

Same shape. A turn was deliberately ended mid-verification with the working tree
dirty — `adocs/status.md` modified, the S059 step file moved out of `plan_todo/`
and into `plan_current/`, `adocs/worklog.md` appended. `--stop` returned 0 and
printed nothing, which is correct: everything changed was under `adocs/`, which
`RECAP_EXEMPT` exempts from the recap gate, no step file had arrived in
`plan_done/` for the stamp gate to judge, and `status.md` had already been
regenerated so `status_disagreements` was empty.

The refusal path was observed later in the same session, during this step's own
completion, at the natural interruption point between moving the step file into
`plan_done/` and regenerating `status.md`. See the completion note appended below.

### Stop — observed refusing, and what the refusal found

The step file was moved into `plan_done/` and the turn ended before `status.md`
was regenerated. `--stop` refused, verbatim:

```
[python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --stop]: moltke: status.md is stale or missing: Last done says 'S087', the filesystem says 'S059'. Run bin/moltke.py --step status before ending the turn.
moltke: status.md is stale or missing: In progress says 'S059 verify the installed release in a live session, after reinstall', the filesystem says 'none'. Run bin/moltke.py --step status before ending the turn.
moltke: adocs/plan_done/S059_verify_installed_0_5_0.md was completed without the README and MANUAL check recorded; check both files and note it in the done: stamp (checking with no change needed is valid).
```

The first two lines are the gate working as designed on the gap the §1 rule
exists for: a session interrupted between the move and the regeneration leaves
`status.md` describing a world that no longer exists, and the hook says so
against the filesystem rather than against its own earlier output.

The third line is a defect the live session found, and it is the reason this step
was worth running. The stamp it was judging did say, in full: `README and MANUAL
checked, no change needed`. It was not read, because the stamp was written across
several indented continuation lines and `parse_step_file` (`bin/moltke.py:86`)
matches `^([a-z_]+):\s*(.*)$` per line — a continuation line matches nothing and
is discarded, so every field is silently truncated to its first line. The gate at
`bin/moltke.py:1432` and `--step done` at `bin/moltke.py:1888` both test that
truncated string for `README` and `MANUAL`, and mine happened to break after
`gitCommitSha c2e6ad3 =`.

Two things follow. The refusal was correct about what it could see, so the gate is
not what needs changing. And the truncation is silent, which is the part that
does: `goal:`, `accepts:`, `touches:`, and `excludes:` already span lines across
`plan_todo/` and `plan_done/`, and every reader of those fields has been seeing
the first line alone. S059 excludes fixing what the live session reveals, so this
is planned as S095 rather than patched here. The stamp for this step was rewritten
as a single line, which is the convention every file in `plan_done/` already
follows.

## 3. What this changes

The `status.md` parked note claiming 0.5.0 and 0.6.0 were both committed and
neither ever installed is false as of the reinstall, and is removed in the same
commit as this file.

`2026-08-06_adversarial-F02` had stayed `planned` because closing it needed an
observation no audit could produce from inside itself. It now has one.
