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

Types are free-form; `adversarial`, `security`, and `bugs` are the usual ones.
It creates `adocs/audit/YYYY-MM-DD_<type>.md` and refuses to overwrite an
existing report, because a report is evidence of one run.

## 2. Run the reviewer

Spawn the `adversarial_reviewer` subagent. Tell it the report path, the scope,
and the commit. It can read anything, and a hook blocks its `Write` and `Edit`
outside `adocs/audit/` and new files under `tests/`. That fence is not the
guarantee: the reviewer also holds `Bash`, which no hook matcher sees, so
mutation is possible by design (DEC-022) and is reconciled in step 3 instead.

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

A finding moves to `closed` only after the audit is re-run and no longer
reports it. Fixing without re-running leaves it `planned`. That is deliberate:
"I fixed it" is a claim, "the audit no longer finds it" is evidence.

Re-running means step 1 again with a new date, and comparing.

## Rules that hold regardless

- The report is written before any fix, and is never edited while fixing.
- A report with open findings and no corresponding steps is not finished work.
- Audits run against the code, not against the specs.
