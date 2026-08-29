---
name: audit
description: Run an adversarial audit, security review, or bug hunt through the adversarial_reviewer subagent, record findings as evidence in adocs/audit/, then turn each finding into a plan step or a recorded decision. Use when asked to audit, review, or hunt for bugs.
---

# Audit

Evidence first, fixes second, and never in the same breath. This is the full
audit the AUDIT project rule names; the per-step fast check is not this and
needs none of the machinery below.

## 1. Open the report

The report is `adocs/audit/YYYY-MM-DD_<type>.md`. Types are yours to pick but
must match `[A-Za-z0-9_-]+` — `adversarial`, `security`, and `bugs` are the
usual ones — since the type becomes part of the filename and of every finding
id. A report is evidence of one run and is never overwritten: if the name is
taken, this is a same-day re-run — use `.2`, then `.3`, and number the
findings from that name. Create the file with a title line naming the commit
audited; the reviewer appends the findings.

## 2. Run the reviewer, on a clean context

Spawn the `adversarial_reviewer` subagent, fresh. A run is one spawn, and a
spawn starts empty — never continue an earlier reviewer with more context.

**Tell it four things and nothing else** (DEC-036):

- the repository path and the commit it is auditing
- the report path and the finding id prefix (the report's own name)
- the type of audit, and the scope boundary if narrower than everything
- that verdicts on prior findings are in scope, which it will find in the
  tracked reports under `adocs/audit/` by reading them

**Do not tell it** what changed since the last run, which steps landed, what
you think is fragile, what to prioritise, or which findings you expect it to
confirm. All of that is your model of the code, blind spots included, and an
auditor handed it inherits them. It reads `git log`, `adocs/`, and the code,
exactly as a reviewer arriving cold would. Red team and blue team: the blue
team does not brief the red team.

Nothing enforces any of this — the spawn prompt is yours to write, and the
reviewer's restraint is its own to keep. That discipline is what makes the
report evidence rather than an echo.

Do not review the code yourself in this turn. You are about to be the one who
fixes these findings, and a reviewer who expects to fix things reports fewer
of them.

## 3. Reconcile, then fix nothing

When the reviewer returns, run `git status` and `git diff`: the run should
have written its report and, at most, new regression tests — nothing else.
Anything else it changed, review deliberately and keep or revert before any
finding is acted on; a report produced by a run that also patched the code is
not evidence of what was there.

Then read the report. Every finding is `open`. Fixing now, before the
findings are recorded and planned, destroys the evidence trail and is the one
thing this skill exists to prevent.

## 4. Give every finding a home

Each finding ends in exactly one of two places:

- **A plan step.** Create it by hand per AGENTS.md, set
  `closes: <finding id>` in the step file, mark the finding `planned` in the
  report.
- **A decision.** A `decisions.md` entry stating why it will not be acted on,
  referencing the finding id; mark it `accepted`.

Findings map one-to-one — a bundle hides which ones actually got fixed.
Correctness defects jump the queue: reorder `plan.md` rather than appending
them out of politeness. Commit the report, the steps, and any decisions
together, per COMMITS.

## 5. Close by re-running, never by asserting

A finding moves to `closed` on a re-run that no longer reports it, or by a
recorded decision naming it. "I fixed it" is a claim; "the audit no longer
finds it" is proof. A re-run is step 1 again, same day gets a suffixed
report.

## 6. Know when to stop

The loop — fix, re-run, triage — ends on a severity profile, not an empty
report (DEC-035): **when a re-run reports no high and no medium, stop.**
Record the lows, discharge them as `accepted` in one decision entry, and
schedule no further audit. An auditor asked to find something will keep
finding something — that is drift, not diligence. A run only counts as a
stopping run if it re-measured every prior finding from that finding's own
reproduction.

## Rules that hold regardless

- The report is written before any fix, and never edited while fixing.
- A report with open findings and no steps or decisions is unfinished work.
- Audits run against the code, not against the specs.
