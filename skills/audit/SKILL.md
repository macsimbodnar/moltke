---
name: audit
description: Run an adversarial audit, security review, or bug hunt through the adversarial_reviewer subagent, record findings as evidence in adocs/audit/, then turn each finding into a plan step or a recorded decision. Use when asked to audit, review, or hunt for bugs.
---

# Audit

Evidence first, fixes second, and never in the same breath.

## 1. Open the report

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --audit new <type>
```

Types are yours to pick but must match `[A-Za-z0-9_-]+`, since the type becomes
part of a filename and of every finding id in the report. `adversarial`,
`security`, and `bugs` are the usual ones.
It creates `adocs/audit/YYYY-MM-DD_<type>.md` and never overwrites an existing
report, because a report is evidence of one run. A second run on the same day
becomes `YYYY-MM-DD_<type>.2.md`, and its findings are numbered from that name.

## 2. Run the reviewer

Spawn the `adversarial_reviewer` subagent. Tell it the report path, the scope,
and the commit. It can read anything, and a hook blocks its `Write` and `Edit`
outside `adocs/audit/` and new files under `tests/`. That fence is not the
guarantee: the reviewer also holds `Bash`, which no hook matcher sees, so
mutation is possible by design (DEC-022) and is reconciled in step 3 instead.

The fence covers this repository only, and so does step 3. A write that resolves
outside it — the installed plugin's own `bin/moltke.py` in the plugin cache, or
`~/.claude/settings.json` — is neither blocked nor reported, so the reviewer's
own instructions are what keep it inside, and that is where to look first if a
run behaves oddly.

Do not review the code yourself in this turn. The separation is the point: you
are about to be the one who fixes these findings, and a reviewer who expects to
fix things reports fewer of them.

## 3. Reconcile what the run changed, then fix nothing

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --audit check
```

It compares the tree against the baseline `--audit new` recorded. The report,
any new files under `tests/`, and an append to `adocs/worklog.md` that matches
what `--log-prompt` writes are expected; anything else exits 1 and is listed.
The worklog is named in the listing either way, because an append there is the
one edit that can turn off the `Stop` recap gate for the surrounding turn.
Review each one with `git diff` and keep or revert it deliberately, before any
finding is acted on — a report produced by a run that also patched the code is
not evidence of what was there.

Then read the report. Every finding is `open` at this stage. Fixing now, before
the findings are recorded and planned, destroys the evidence trail and is the one
thing this skill exists to prevent.

## 4. Give every finding a home

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --audit list
```

It prints each finding, its status, and what references it, and exits non-zero
while any open finding has neither. Each one ends in exactly one of two places:

- **A plan step.** `--step new <name>`, then set `closes: <finding_id>` in the
  step file. Status becomes `planned`.
- **A decision.** Append a `decisions.md` entry stating why it will not be
  acted on, referencing the finding id. Status becomes `accepted`.

Findings map one-to-one. Do not bundle three findings into one step: they close
independently, and a bundle hides which ones actually got fixed.

Correctness defects jump the queue ahead of planned work. Reorder `plan.md`
accordingly rather than appending them at the end out of politeness.

## 5. Close by re-running, never by asserting

A finding moves to `closed` only after the audit is re-run and no longer
reports it. Fixing without re-running leaves it `planned`. That is deliberate:
"I fixed it" is a claim, "the audit no longer finds it" is evidence.

Re-running means step 1 again and comparing. It does not mean waiting for
tomorrow: a same-day re-run gets its own suffixed report.

## 6. Know when to stop

The loop is: fix, release, re-run, triage. It has an end, and the end is a
severity profile rather than an empty report (DEC-035).

**When a re-run reports no `high` and no `medium`, stop.** Record the lows as
always, then discharge them as `accepted` in one decision entry rather than
planning a step each, and schedule no further audit. Only lows means the
codebase has stopped giving up real defects, and an auditor asked to find
something will keep finding something — that is drift, not diligence.

A regression the audited batch introduced does not count towards continuing. Fix
it, but read it as evidence that the batch was wrong, not that the codebase has
more to give.

Two conditions must hold for a run to count as a stopping run, because "only
lows" has to mean the reviewer looked and found little:

- it re-measured every prior finding from that finding's own reproduction
- its mutation testing killed what it planted

If either is missing, the run does not stop anything. Run it again properly.

## Rules that hold regardless

- The report is written before any fix, and is never edited while fixing.
- A report with open findings and no corresponding steps is not finished work.
- Audits run against the code, not against the specs.
