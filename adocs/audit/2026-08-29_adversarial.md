# Audit 2026-08-29 adversarial — commit 4bb0e87

Finding ids in this report read `2026-08-29_adversarial-F<nn>`. Every finding
carries a status of `open`, `planned`, `closed`, or `accepted`. Written before
any fix.

Scope: the whole repository at `4bb0e87` — the shipped 1.0.0 product
(`skills/`, `agents/adversarial_reviewer.md`, `templates/`, `.claude-plugin/`,
`AGENTS.md`, `README.md`, `MANUAL.md`) and this repository's own `adocs/`,
read as claims about the product. Verdicts on the nineteen prior findings
still marked `planned` are included, re-measured where the target still exists.

Method: read every shipped file; diffed the root `AGENTS.md` base sections
against `templates/AGENTS.md` (identical); grepped skills, agent, templates,
and docs for stale 0.x surface (`moltke.py`, `.moltke.json`, `testing.md`,
worklog, hook paths — none found); checked `decisions.md` index against its
body and id ordering; checked step-id uniqueness across `plan_done/`;
verified the installed 1.0.0 cache under `~/.claude/plugins/cache` against
this checkout (identical apart from `.in_use`) and measured what it ships.
There is no suite to run, per the TESTS rule; INV-18 was checked by listing
the tree (markdown and two JSON manifests only, no executables, no hooks).

## Findings

### 2026-08-29_adversarial-F01  medium  init never wires the ruleset into an existing `CLAUDE.md`, so the product is silently inert for the most common adopter

Status: planned  (S164)

Evidence: `skills/init/SKILL.md:52-59` — scaffold is "never overwrite",
"skipping and reporting anything that already exists (report it as `kept`)",
and `CLAUDE.md` is created "from `templates/CLAUDE.md` (one line:
`@AGENTS.md`)". The Detect section (`skills/init/SKILL.md:12-23`) offers an
append path for an existing `AGENTS.md` (line 17) but has no analogous
handling for an existing `CLAUDE.md` or `.cursor/rules/moltke.mdc`.
`AGENTS.md:10` (shipped as `templates/AGENTS.md:10`): "Claude Code entry
point: `CLAUDE.md` containing `@AGENTS.md`."

Impact: an established repository adopting moltke almost always already has a
`CLAUDE.md`. Init records the interview into `AGENTS.md`, reports `CLAUDE.md`
as `kept`, and the product's own stated entry point never references the
ruleset — Claude Code sessions read the pre-existing `CLAUDE.md` and never
see `AGENTS.md` or the Orient protocol. Nothing fails and nothing warns; the
workflow is simply not in force, which is the exact failure mode ("a root
without moltke gets no skills ... silently") the MANUAL warns about for
installs but the skill reproduces for setup.

Suggested resolution: mirror the existing-`AGENTS.md` branch — when
`CLAUDE.md` exists without an `@AGENTS.md` reference, offer to append that
one line (append, not overwrite; INV-19 intact) and report what was done;
same offer for an existing `.cursor/rules/moltke.mdc`.

### 2026-08-29_adversarial-F02  low  init's Detect table does not cover its input space, and the uncovered case discards the interview

Status: planned  (S165)

Evidence: `skills/init/SKILL.md:12-23` defines three branches: (a) `adocs/`
exists AND `AGENTS.md` has `## Project rules` → already set up, stop; (b)
`AGENTS.md` exists but is not moltke's ruleset → offer append; (c) "Neither:
continue." A repository where `AGENTS.md` IS moltke's ruleset but `adocs/` is
missing (deleted, or the file copied from a sibling repo) matches none of the
three: it is not (a) — `adocs/` is missing — and not (b) — the ruleset is
moltke's. Falling through to (c) runs the interview, and scaffold
(`skills/init/SKILL.md:52-55`) then skips the existing `AGENTS.md` as `kept`,
so the nine freshly recorded rule lines have nowhere to land.

Impact: a re-init over partial state runs a full interview whose answers are
then silently dropped by the never-overwrite rule; the user believes rules
were recorded that no file holds, which breaks the prime directive (state
derivable from tracked files).

Suggested resolution: make the Detect matrix exhaustive: an existing moltke
`AGENTS.md` without `adocs/` scaffolds only the missing pieces and rewrites
only the `## Project rules` section (the operation `/moltke:rules` already
performs), never the whole file.

### 2026-08-29_adversarial-F03  low  init hardcodes the adoption decision as `DEC-001`, which instructs an INV-20 violation whenever `decisions.md` pre-exists

Status: planned  (S166)

Evidence: `skills/init/SKILL.md:68-69`: "record the adoption as the first
decision in `adocs/decisions.md`: `DEC-001`" — unconditionally. Scaffold
keeps a pre-existing `adocs/decisions.md` (line 55, INV-19), which may
already hold a `DEC-001`. `adocs/specs.md:24` (INV-20): "allocated ids are
never reused or renumbered". The project's own migration prompt gets this
right: `adocs/migration_prompt.md` step 5 says "next free DEC id, ids never
reused".

Impact: init run against a repository with an existing decisions ledger (the
append path of Detect branch (b), or F02's fall-through) writes a duplicate
`DEC-001`, violating the invariant the skill is scaffolding.

Suggested resolution: word it as the migration prompt does — the next free
`DEC-<nnn>`, `DEC-001` only when the file is fresh from the template.

### 2026-08-29_adversarial-F04  low  MANUAL's Teams section sanctions a renumber that INV-20 and the shipped ruleset forbid without exception

Status: planned  (S167)

Evidence: `MANUAL.md:97-98`: "That is the one renumber the never-reuse rule
sanctions, because two files claiming one id is worse." Versus
`adocs/specs.md:24` (INV-20): "allocated ids are never reused or renumbered"
— no exception — and `AGENTS.md:63` = `templates/AGENTS.md:63`: "ids are
never reused or renumbered, even for a deleted step."

Impact: on the one path where the rule matters (two branches allocated the
same step id, pre-merge), the user-facing manual and the ruleset agents obey
contradict each other. An agent asked to perform MANUAL's merge procedure is
forbidden it by the `AGENTS.md` it just read; specs > plan > status gives it
no way to prefer MANUAL. The docs promise a behaviour the ruleset does not
permit.

Suggested resolution: state the merge-collision exception in the ruleset and
INV-20 (one sentence: "except the pre-merge renumber of a colliding id, noted
in the merge commit"), or drop the sanction from MANUAL.

### 2026-08-29_adversarial-F05  low  the audit skill's type grammar cannot express its own re-run naming, and tracked reports already violate it

Status: planned  (S168)

Evidence: `skills/audit/SKILL.md:15`: type "must match `[A-Za-z0-9_-]+` ...
since the type becomes part of the filename and of every finding id". Three
lines later (`skills/audit/SKILL.md:18`): a same-day re-run "use[s] `.2`,
then `.3`, and number[s] the findings from that name" — a dot the grammar
excludes. `adocs/specs.md:24` (INV-20) fixes the id shape as
`YYYY-MM-DD_<type>-F<nn>`, which cannot parse the ids that exist in tracked
evidence: `adocs/audit/2026-08-07_adversarial.2.md` carries findings named
`2026-08-07_adversarial.2-F01` etc.

Impact: anything (or anyone) taking the stated grammar literally — a future
scanner, a `closes:` cross-referencer, an agent validating a report name —
rejects every same-day re-run report and its finding ids, including four
reports already in `adocs/audit/`.

Suggested resolution: name the optional run suffix in both places:
`YYYY-MM-DD_<type>[.N]-F<nn>`, type `[A-Za-z0-9_-]+`.

### 2026-08-29_adversarial-F06  low  the 1.0.0 artifact is 92% moltke's own memory, and the MANUAL disclosure DEC-020 conditioned that on is gone

Status: planned  (S169)

Evidence: `du -sh ~/.claude/plugins/cache/moltke/moltke/1.0.0/` → 1.2M total,
of which `adocs/` is 1.1M (162 `plan_done/` step files, 13 audit reports, the
migration prompt). DEC-020 accepted the repo-root-as-plugin-root layout with
"record the consequence as a known issue in MANUAL rather than
restructuring". `MANUAL.md:116-121` (Known limits) lists two items; neither
is this. `adocs/status.md` still parks the DEC-020 escape hatch ("a `plugin/`
subdirectory move").

Impact: every installer downloads and caches this project's entire plan and
audit history per config root and per version; the decision that accepted
the layout was conditioned on a disclosure the v1 rewrite dropped, so the
tree now disagrees with its own decision record.

Suggested resolution: one Known-limits line in MANUAL restoring the
disclosure, or take the DEC-020 escape hatch and move the plugin under
`plugin/` before the tree grows further.

### 2026-08-29_adversarial-F07  low  README's Ship procedure pushes before the version bump is committed, and step 4 then no-ops

Status: planned  (S170)

Evidence: `README.md:45-47`: "1. commit on `master` ... 2. bump `version` in
`.claude-plugin/plugin.json` 3. push". No commit between 2 and 3; the same
section states "updates compare `version` and nothing else".

Impact: followed literally, the push does not carry the bump, `claude plugin
update` in step 4 finds no version change and does nothing, and the operator
believes a release shipped that no root received.

Suggested resolution: reorder to bump → commit → push (the bump commit is
the release commit).

### 2026-08-29_adversarial-F08  low  this checkout's `.moltke.local.md` still makes 0.x claims, and Orient reads it every session

Status: accepted  (DEC-067)

Evidence: the untracked `/Users/max/ws/moltke/.moltke.local.md` (ignored via
`.gitignore`) still reads "moltke created this file, keeps it out of git via
`.git/info/exclude`, and injects its content into every session's context" —
the 0.x template wording; v1 has no injection and the exclusion here is
`.gitignore`, not `.git/info/exclude`. It also still carries the "Delete this
guidance once you have real content" placeholder. `AGENTS.md:19-20` (Orient
step 3) directs every session to read it.

Impact: machine-local only and invisible to a clone, but on this machine
every session pays to read stale guidance that asserts behaviour v1 removed
— exactly the drift DEC-065 scrubbed from the tracked documents.

Suggested resolution: replace its body with the v1 template text
(`templates/moltke_local.md`) or with real machine-local content; not a
tracked change, so no step needed — the operator can do it directly.

## Verdicts on prior findings

Nineteen findings across the tracked reports stood at `planned`; none had
received the closing re-run before 1.0.0 shipped. This run is that re-run.
Per this repository's rules the Status flips below are the invoking session's
to write into the earlier reports; this report records the evidence.

- `2026-08-11_adversarial-F01..F05` and `2026-08-19_adversarial-F01..F07,
  F09..F13` (17 findings) — **close as retired.** Every one targets the 0.x
  enforcement product: `bin/moltke.py`, hooks wiring, the write fence,
  `--watch`, `--audit check`, the suite. DEC-062/S160 deleted that product
  wholesale; the tree at `4bb0e87` has no `bin/`, `hooks/`, or `tests/`, and
  no shipped file references them (grep of `skills/`, `agents/`,
  `templates/`, `AGENTS.md`, `CLAUDE.md`: no match). The reproductions cannot
  be run because the code they exercise no longer exists anywhere in the
  product. Closed by retirement of the target, not by repair — a decision
  entry naming them would be the cleaner discharge, since DEC-062 does not
  name finding ids.
- `2026-08-11_adversarial-F06` (decisions.md index missing entries, body not
  newest-last) — **closed, re-measured against the living file.** Index and
  body both hold 65 `DEC-` entries, the sets match exactly, and body heading
  ids are strictly ascending (checked by diffing the extracted id lists and
  an ordering scan; both clean).
- `2026-08-19_adversarial-F08` (the shipped audit skill documents the worklog
  and `--log-prompt`) — **closed, re-measured.** `grep -rn "worklog\|log-prompt"
  skills/ agents/` finds nothing; the S160 rewrite removed the surface.

One clarification for future re-runs: the only `Status: open` line in the
older reports outside a template example sits at
`adocs/audit/2026-08-08_adversarial.2.md:561`, inside a quoted fixture
(`2026-08-01_adversarial-F02 "a draft finding"`, lines 551-568) used as
evidence for an INV-14 reproduction. It is not a real finding and needs no
verdict.

## Where the product holds

Checked and clean, recorded so the absence of findings there is a result and
not a gap: root `AGENTS.md` base sections are byte-identical to
`templates/AGENTS.md`; INV-18 holds (markdown plus two JSON manifests, no
executables); step ids in `plan_done/` are unique and the S163 drop burned
its id (`plan.md`: "the next step gets an id above S163"); `plan.md`,
`status.md`, and the plan directories agree (nothing open, nothing current);
the installed 1.0.0 cache is byte-identical to this checkout apart from
`.in_use`; the documented cache path in `adocs/migration_prompt.md` matches
the real layout; MANUAL's install URL matches the git remote and
`plugin.json`.
