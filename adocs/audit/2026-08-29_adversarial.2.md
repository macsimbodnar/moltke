# Audit 2026-08-29 adversarial, run 2 — commit e52b91d

Finding ids in this report read `2026-08-29_adversarial.2-F<nn>`. Every
finding carries a status of `open`, `planned`, `closed`, or `accepted`.
Written before any fix.

Scope: the whole repository at `e52b91d` (tagged `v1.1.0`) — the shipped
plugin product (`skills/`, `agents/adversarial_reviewer.md`, `templates/`,
`.claude-plugin/`, `AGENTS.md`, `README.md`, `MANUAL.md`) and this
repository's own `adocs/`, read as claims about the product. This run is the
closing re-run for the eight findings of `2026-08-29_adversarial.md`
(commit `4bb0e87`); each was re-measured from its own reproduction against
the S164–S170 fixes, and the verdicts are below the findings.

Method: read every shipped file; diffed root `AGENTS.md` base sections
against `templates/AGENTS.md` (identical outside `## Project rules`);
re-walked init's Detect matrix over (AGENTS.md absent / non-moltke / moltke)
× (adocs/ present / absent); grepped skills, agent, templates, and docs for
stale 0.x surface (`moltke.py`, worklog, `--log-prompt`, hook paths — only
the deliberate historical mentions in README's Ship note and MANUAL's
Migrating section remain); checked `decisions.md` index against body (sets
match, body ids strictly ascending, DEC-066..068 present); checked every
`Status:` line across all fourteen prior reports (the only remaining
`open`/`planned` lines outside fenced format examples are the seven
run-1 findings this re-run closes); verified `v1.1.0` is an annotated tag on
the audited commit and `plugin.json` says 1.1.0; confirmed INV-18 by listing
the tree (markdown plus two JSON manifests, no executable bits, no hooks).
No suite exists to run, per the TESTS rule.

## Findings

### 2026-08-29_adversarial.2-F01  medium  plan.md and status.md both misstate plan state at the release commit — S171 is in progress and invisible to Orient

Status: planned  (S171)

Evidence: `adocs/plan_current/S171_release_1_1_0.md` exists with
`author: Maksym Bodnar` set and an empty `done:` stamp — the step is started
and unfinished. Yet `adocs/plan.md:13-15` reads "## Open / Nothing open past
the 2026-08-29 audit steps; the next id is S171", and `adocs/status.md:7-12`
reads "Updated: 2026-08-29 by hand (S170 completion). / Last done: S170 /
In progress: none / Next: none". Neither file has been touched since S170:
`git log --oneline -1 -- adocs/plan.md adocs/status.md` → `43f6022 Complete
S170`. The step's creation commit (`git show 6e4e626 --stat`: only
`adocs/plan_todo/S171_release_1_1_0.md`) never added it to plan.md's Open
list, and the start turn (`git show e52b91d --stat`: only `plugin.json` and
the todo→current move) never rewrote status.md. The rules violated:
`AGENTS.md:68-69` "Order lives in `plan.md`'s Open list and nowhere else;
the next step is the first entry there", `AGENTS.md:89-90` "`status.md`:
rewrite by hand at the end of any turn that changed plan state", and the
shipped template's own contract, `templates/adocs/plan.md:8` "Every open
step file appears as an entry under Open".

Impact: Orient (`AGENTS.md:16-22`) says status.md plus plan.md is "enough to
act on" — a cold session orienting at `e52b91d` reads that nothing is in
progress and nothing is next, while a release is mid-flight (tag created,
push pending, accepts unmet). Worse, plan.md's prose asserts "the next id is
S171" after S171 was allocated: an agent trusting the plan file over a
directory scan mints a duplicate S171 — the exact id-collision class INV-20
exists to prevent, in the project that ships the rule. The dogfooding
repository is the product's primary evidence that the ruleset works; at the
audited commit it demonstrates the opposite.

Suggested resolution: fold into S171's completion — list S171 under Open now
(or complete the step), rewrite status.md from the plan directories, and
replace the "next id is S171" prose with either the Open entry or the next
truly free id.

### 2026-08-29_adversarial.2-F02  low  init's "already set up" branch checks nothing but existence, so 1.0.0-initialised repositories can never be repaired by re-running init

Status: planned  (S172)

Evidence: `skills/init/SKILL.md:14-16` — Detect branch (a): "`adocs/` exists
and `AGENTS.md` has a `## Project rules` section: already set up. Read
`adocs/status.md` and `adocs/plan.md` back to the user ... stop." The
entry-point wiring added by S164 lives in step 3 (`skills/init/SKILL.md:74-81`)
and is reached by branches (b), (c), and (d); branch (c) even says so
explicitly ("entry-point wiring included", line 26). Branch (a) stops before
step 3, unconditionally. The same existence-only test means an `adocs/` with
missing pieces (a clone where an empty `plan_todo/` never got its `.gitkeep`,
a deleted `audit/` directory) also stops at "already set up" with no path to
re-scaffold what is missing.

Impact: the population run 1's F01 named — established repositories with a
pre-existing unwired `CLAUDE.md` — includes every repository initialised by
1.0.0's init, which did not wire. For them the 1.1.0 fix is unreachable:
re-running `/moltke:init` hits branch (a) and stops without ever checking
whether the entry point references the ruleset, so the workflow stays
silently not-in-force — the second-run version of the defect S164 fixed for
first runs. Same stop also refuses to repair a partially present `adocs/`.

Suggested resolution: branch (a), before stopping, checks entry-point wiring
(`CLAUDE.md` and `.cursor/rules/moltke.mdc` reference `@AGENTS.md`) and the
adocs layout, and makes the same append/scaffold-missing offers step 3 makes;
never-overwrite unchanged.

### 2026-08-29_adversarial.2-F03  low  init step 4 assumes fresh-template adocs and, on the kept-files paths, instructs allocating "ids from S001" into a plan that already holds them

Status: planned  (S173)

Evidence: `skills/init/SKILL.md:90-91` — step 4 opens "The scaffold leaves
`specs.md` and `plan.md` holding comments" and runs unconditionally after
step 3. Item 4 (lines 103-106): "Create one per planned step in
`adocs/plan_todo/` ... ids from S001 in creation order". Item 6 (lines
109-110): "Fill `status.md`: nothing done, nothing in progress". But step 3
keeps pre-existing files (lines 60-61), and two Detect paths reach step 4
with a populated `adocs/`: branch (b) — a non-moltke `AGENTS.md` beside an
existing `adocs/` — runs "the interview as normal" (lines 17-22) and nothing
skips step 4; and branch (d) — `AGENTS.md` absent, `adocs/` present (e.g. a
moltke repo whose ruleset was consolidated away) — falls through to the full
flow. On both, specs.md and plan.md were kept, not scaffolded, and step 4's
premise is false.

Impact: an agent following the skill literally in such a repository proposes
a "first plan" over an existing one, allocates step ids "from S001" into a
`plan_todo/` whose ids are long past that — the id reuse INV-20 and the
just-installed ruleset forbid — and resets `status.md` to "nothing done"
over real state. Requires the kept-files path, so fresh adoptions are
unaffected.

Suggested resolution: gate step 4 on which files step 3 actually created:
run it only when `specs.md` and `plan.md` came fresh from templates;
otherwise stop after the scaffold report and orient from the existing plan
(read status.md and plan.md back, as branch (a) does).

## Verdicts on the 2026-08-29_adversarial.md findings

All eight re-measured at `e52b91d` from each finding's own reproduction.
Per this repository's rules the Status flips belong in the earlier report
and are the invoking session's to write; this report records the evidence.

- `2026-08-29_adversarial-F01` (init never wires an existing `CLAUDE.md`) —
  **close.** `skills/init/SKILL.md:74-81` now offers the one-line append for
  an existing `CLAUDE.md` without an `@AGENTS.md` reference and for an
  unwired `.cursor/rules/moltke.mdc`, reported as `wired` rather than `kept`,
  append-only. The residual second-run gap (the offer is unreachable from
  Detect branch (a)) is recorded separately as this report's F02, per
  one-finding-one-home.
- `2026-08-29_adversarial-F02` (Detect table not exhaustive) — **close.**
  `skills/init/SKILL.md:23-29` adds the moltke-`AGENTS.md`-without-`adocs/`
  branch (skip the interview, scaffold only what is missing, rule changes go
  through `/moltke:rules`), and the fall-through is now "None of the above".
  The four states of (AGENTS.md kind × adocs presence) each match exactly
  one branch; no path re-interviews into a file the scaffold refuses to
  write.
- `2026-08-29_adversarial-F03` (adoption hardcoded as `DEC-001`) —
  **close.** `skills/init/SKILL.md:83-86`: "the next free `DEC-<nnn>` —
  `DEC-001` only when the file is fresh from the template, since ids are
  never reused."
- `2026-08-29_adversarial-F04` (MANUAL sanctions a renumber the ruleset
  forbids) — **close** (DEC-068). INV-20 (`adocs/specs.md:26-29`) and the
  never-reuse paragraph in both `AGENTS.md:64-67` and
  `templates/AGENTS.md:64-67` now state the merge-collision exception;
  `MANUAL.md:97-98` unchanged; the base sections of the two AGENTS.md copies
  diff clean.
- `2026-08-29_adversarial-F05` (id grammar cannot express `.2` re-runs) —
  **close.** `skills/audit/SKILL.md:14` names the report
  `YYYY-MM-DD_<type>[.N].md`, `adocs/specs.md:25-26` (INV-20) names the
  finding id `YYYY-MM-DD_<type>[.N]-F<nn>` with type `[A-Za-z0-9_-]+`, and
  `agents/adversarial_reviewer.md:60,64` states the same; the four tracked
  `.2`/`.3`/`.4` reports and this one parse under it.
- `2026-08-29_adversarial-F06` (install weight disclosure gone) — **close.**
  `MANUAL.md:122-126` (Known limits) discloses that an install ships the
  repository whole, `adocs/` history as most of the megabyte-plus, cached
  per root and per version, DEC-020 named, `plugin/` escape hatch parked.
- `2026-08-29_adversarial-F07` (Ship pushes before the bump is committed) —
  **close.** `README.md:43-50` now reads bump → commit ("the bump commit is
  the release commit") → push → update, and `e52b91d` itself followed that
  order.
- `2026-08-29_adversarial-F08` (stale 0.x `.moltke.local.md`) — **stays
  accepted** (DEC-067). Additionally re-measured: the file's body on this
  machine now matches the v1 template (`templates/moltke_local.md`); the
  0.x claims are gone, as DEC-067 said the operator would do.

Older reports: no real `open` or `planned` finding remains anywhere in
`adocs/audit/` — every remaining `Status: open`/`Status: planned` line sits
inside a fenced finding-format example in a report preamble (checked each
hit individually), plus the known quoted fixture at
`2026-08-08_adversarial.2.md:561`. The seventeen retirement closures and the
two re-measured closures promised by run 1 were all applied, with DEC-066 as
the named discharge.

## Where the product holds

Checked and clean, recorded so the absence of findings there is a result and
not a gap: root `AGENTS.md` base sections byte-identical to
`templates/AGENTS.md`; INV-18 holds (no executable files anywhere in the
tree, `find -perm +111` empty); INV-20 holds in the ledgers (`decisions.md`
index and body sets match, body strictly ascending; `plan_done/` step ids
unique; S171 allocated once — the duplicate risk in F01 is prospective);
`v1.1.0` is an annotated tag on the audited commit and `plugin.json` says
1.1.0 with a version-only diff from S170's tree; the S164–S170 step files
carry correct `closes:` fields and completion stamps; the migration prompt's
cache path, DEC-id wording, and cleanup list are consistent with the v1
product; MANUAL's install URL matches the git remote and `plugin.json`'s
repository field; the audit skill, reviewer agent, and INV-20 now state one
id grammar between them.
