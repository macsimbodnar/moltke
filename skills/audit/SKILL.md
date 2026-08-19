---
name: audit
description: Run an adversarial audit, security review, or bug hunt through the adversarial_reviewer subagent, record findings as evidence in adocs/audit/, then turn each finding into a plan step or a recorded decision. Use when asked to audit, review, or hunt for bugs.
---

# Audit

Evidence first, fixes second, and never in the same breath.

This is tier 3 of the review model (AGENTS.md §9): it runs on the user's ask,
or after the user accepts a proposal. Propose one when risk warrants it — a
security-touching change, a public-surface change, a long stretch since the
last run — and take "postpone" for an answer: park the proposal as one line in
status.md's Parked block and do not ask again unprompted. The per-step fast
check is not this and needs none of the machinery below.

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

## 2. Run the reviewer, on a clean context

Spawn the `adversarial_reviewer` subagent, fresh. Never continue an earlier
reviewer with more context: a run is one spawn, and a spawn starts empty.

**Tell it four things and nothing else** (DEC-036):

- the repository path and the commit it is auditing
- the report path `--audit new` just created, and the finding id prefix
- the type of audit, and the scope boundary if the scope is narrower than
  everything
- that verdicts on prior findings are in scope, which it will find in the
  tracked reports under `adocs/audit/` by reading them

**Do not tell it** what changed since the last run, which steps landed, what you
think is fragile, what to prioritise, what the recurring defect shape has been,
or which findings you expect it to confirm. All of that is your model of the
code, blind spots included, and an auditor handed it inherits them: one told
where to look looks there, and one told what the last batch fixed is primed to
agree that it is fixed. It reads `git log`, `adocs/`, and the code, exactly as a
reviewer arriving cold would.

Red team and blue team. The blue team does not brief the red team.

Nothing enforces this — the spawn prompt is yours to write, like the reviewer's
`Bash` limit is its own to keep. The cost is real and accepted: runs are slower
and less targeted, and a first run under this rule may re-derive what the last
one knew.

It can read anything, and a hook blocks its `Write` and `Edit`
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

It compares the tree against the baseline `--audit new` recorded. The report and
any new files under `tests/` are expected; anything else exits 1 and is listed.
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

A finding moves to `closed` on a re-run that no longer reports it, or by a
recorded decision naming it. The re-run is the stronger evidence — "I fixed it"
is a claim, "the audit no longer finds it" is proof — and the decision route is
how the loop ends when the user says it ends rather than when the rule fires.

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
