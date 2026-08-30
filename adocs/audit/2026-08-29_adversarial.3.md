# Audit 2026-08-29 adversarial, run 3 — commit 6cc8f96

Finding ids in this report read `2026-08-29_adversarial.3-F<nn>`. Every
finding carries a status of `open`, `planned`, `closed`, or `accepted`.
Written before any fix.

Scope: the whole repository at `6cc8f96` (tagged `v1.1.0`) — the shipped
plugin product (`skills/`, `agents/adversarial_reviewer.md`, `templates/`,
`.claude-plugin/`, `AGENTS.md`, `README.md`, `MANUAL.md`) and this
repository's own `adocs/`, read as claims about the product. This run is the
closing re-run for the three findings of `2026-08-29_adversarial.2.md`
(commit `e52b91d`); each was re-measured from its own reproduction against
the S171–S173 fixes, and the verdicts are below the findings.

Method: read every shipped file; diffed root `AGENTS.md` base sections
against `templates/AGENTS.md` (identical outside `## Project rules`);
re-walked init's Detect branches and the S172/S173-repaired steps 3–4 over
the kept-file states; checked `decisions.md` index against body (68 ids each,
sets match, body strictly ascending); checked every `Status:` line across
all fifteen prior reports — outside the three run-2 findings this re-run
closes, every remaining `open`/`planned` hit sits inside a fenced
finding-format example (all eleven checked individually, plus the known
quoted fixture at `2026-08-08_adversarial.2.md:561`); verified `v1.1.0` is
an annotated tag on the audited commit (`git rev-parse 'v1.1.0^{commit}'` →
`6cc8f96…`) and `plugin.json` says 1.1.0; confirmed INV-18 by listing the
tree (`find . -type f -perm +111` outside `.git/` is empty; markdown plus
two JSON manifests); step ids unique across the three plan directories, with
the burned gaps S043, S053, S131, S133, S135, S163 noted; `master` is 22
commits ahead of `origin/master` (`a5513e0`), so nothing of the 1.1.0 line
is pushed yet — matching status.md. No suite exists to run, per the TESTS
rule. No network from this session (`git ls-remote` fails on auth), noted
where it limits a finding.

## Findings

### 2026-08-29_adversarial.3-F01  medium  init's step 4 rewrites a kept status.md — contradicting INV-19, S173's own accepts, and the Parked carry-forward rule

Status: closed  (S174)

Evidence: `skills/init/SKILL.md:117-118`, step 4 item 6: "**Status.**
Rewrite `status.md` to match the plan directories, fresh or kept — the
directories are the state, this file is the view." Three texts contradict
it. `adocs/specs.md:22-23` (INV-19): "`init` never overwrites an existing
file; everything it skips is reported as kept" — no exception stated. The
step's own intro, `skills/init/SKILL.md:97-99`: "where a file was kept
rather than created, fill only what is empty and extend rather than restate
what is already recorded" — item 6 is neither fill-only-empty nor extend.
And the step that shipped the line,
`adocs/plan_done/S173_first_plan_respects_kept_files.md`, whose `accepts`
reads "status.md is filled only when it is fresh from the template — no
path directs id reuse or overwrites recorded state" and whose stamp claims
"no instruction now directs id reuse or overwrites recorded state": the
shipped instruction rewrites a kept file, so the accepts does not hold in
the text it accepted. The data-loss path: `AGENTS.md:89-91` — "Everything
under `Parked:` is human memory — carry it forward, prune it only
deliberately"; Parked content is not derivable from the plan directories,
so "rewrite to match the plan directories" performed literally erases it,
and nothing in the skill says to carry it forward.

Impact: on the kept-adocs paths (Detect branches (b) and (d)) init
overwrites an existing file the invariant says it never touches, and the
one part of status.md that is not a regenerable view — the Parked list,
the user's shared scratchpad per `MANUAL.md:84-86` — is destroyed by the
literal instruction. Separately, `plan_done/` now holds a completion stamp
asserting a property the shipped text lacks; readers trusting the stamp
(which the ruleset forbids editing) inherit a false claim.

Suggested resolution: reword item 6 as the workflow's maintenance operation
with its safety stated — on a kept `status.md`, update the view fields to
match the plan directories and carry `Parked:` forward verbatim — and
either scope INV-19 to the scaffold step or state the status-view exception
in it. S173's stamp is history; the correction is a new step, not an edit.

### 2026-08-29_adversarial.3-F02  low  the already-set-up repair path scaffolds template-fresh status.md/plan.md over real history, then reads the false view back as orientation

Status: closed  (S175)

Evidence: `skills/init/SKILL.md:14-21`, Detect branch (a): "anything step 3
would create unprompted that is missing gets the offer to create it …
Then read `adocs/status.md` and `adocs/plan.md` back to the user (the
Orient order) … stop." Step 3 creates both files from `templates/adocs/`
(`skills/init/SKILL.md:72-73`). `templates/adocs/status.md` reads "Last
done: nothing yet / In progress: none / Next: no steps planned yet";
`templates/adocs/plan.md` has an empty Open list under its own contract
"Every open step file appears as an entry under Open". Branch (a) stops
before step 4, so item 6's rewrite-to-match and item 4's Open-list fill are
unreachable, and nothing in the branch says to reconcile the created files
with `plan_todo/` / `plan_done/`.

Impact: a set-up repository that lost `status.md` or `plan.md` — the exact
partial states S172 set out to repair — gets a file asserting "nothing
done, nothing planned" beside a populated plan history, and init endorses
the false view by reading it back as the Orient result: it manufactures the
prose/filesystem disagreement the product's core rule ("filesystem beats
prose") exists to prevent.

Suggested resolution: in branch (a), after creating a missing `status.md`
or `plan.md` from the template, rewrite them from the plan directories
(status view fields; Open list from `plan_todo/`) before reading them back.

### 2026-08-29_adversarial.3-F03  low  "ids from the next free S<nnn>" re-issues burned ids in any plan with gaps — the reading AGENTS.md forbids

Status: closed  (S176)

Evidence: `skills/init/SKILL.md:110-113`, step 4 item 4: step files get
"ids from the next free `S<nnn>` (S001 only when the plan directories are
empty)". `AGENTS.md:62-63` (= `templates/AGENTS.md`): "A new id is one more
than the highest ever allocated, across all three directories — ids are
never reused or renumbered, even for a deleted step." The two readings
differ exactly when a plan has gaps, and gaps are normal: this repository's
own `plan_done/` is missing S043, S053, S131, S133, S135, and S163 (burned
ids; S163 dropped in `4bb0e87`). A directory scan cannot tell a burned id
from a never-allocated one, so "next free" read as smallest-unused yields
S043 here — an INV-20 violation. The neighbouring "next free `DEC-<nnn>`"
(`skills/init/SKILL.md:88-89`) is safe only because `decisions.md` retains
every id ever allocated; the plan directories do not retain deleted steps.

Impact: an agent running init's step 4 over a kept plan with burned ids
(Detect branches (b)/(d)) is directed to mint an id the ruleset installed
beside it forbids; the two texts one run produced disagree on the
allocation rule.

Suggested resolution: word item 4 as AGENTS.md does — one more than the
highest id anywhere in the three directories (S001 when they are empty).

### 2026-08-29_adversarial.3-F04  low  v1.1.0 was re-cut onto a different commit after the run-2 report recorded it, falsifying immutable evidence; five commits share one version with different product bytes

Status: accepted  (DEC-069)

Evidence: `adocs/audit/2026-08-29_adversarial.2.md:1,7` records "run 2 —
commit e52b91d" and "at `e52b91d` (tagged `v1.1.0`)", and its Method
(lines 25-26) "verified `v1.1.0` is an annotated tag on the audited
commit". At `6cc8f96`: `git rev-parse 'v1.1.0^{commit}'` → `6cc8f96…`. The
S171 stamp admits the move: "The tag was first cut on e52b91d and moved
here before any push." After the bump, four commits (`03e997e`, `03cfa20`,
`f01a595`, `956676e`) changed `skills/init/SKILL.md` while `plugin.json`
stayed at 1.1.0, so `e52b91d..6cc8f96` are five trees all self-identifying
as version 1.1.0. `README.md:45-47`: "the bump commit is the release
commit." No `decisions.md` entry records the deviation
(`AGENTS.md:84-85`: "stop, record a decision, amend the plan. Never
deviate silently"); the only record is the stamp.

Impact: two lines of an immutable audit report are now false, and per
`AGENTS.md:106-109` the report cannot be corrected — only a `Status:` line
may move. Nothing shipped wrong this time because master was never pushed
in between (`origin/master` is still `a5513e0`), but the pattern — bump
early, keep landing product changes, move the tag — is exactly how two
different trees ship as the same version, a failure "updates compare
`version` and nothing else" cannot detect.

Suggested resolution: a decision entry fixing the rule (tag once, on the
release commit, after all release-bound changes — or bump last), and noting
that the .2 report's tag line describes the tag's first position.

### 2026-08-29_adversarial.3-F05  low  releases now carry an annotated tag, but README's Ship procedure never mentions tagging — and S171's stamp skipped the DOCS check that gates completion

Status: closed  (S177)

Evidence: `adocs/plan_done/S171_release_1_1_0.md` accepts: "the release
commit carries an annotated tag v1.1.0"; stamp: "Max pushes commits and
the tag (git push --follow-tags)". `grep -in tag README.md MANUAL.md` → no
matches: `README.md:43-51`'s four-step Ship order (bump, commit, push,
update) has no tag step, and its plain push does not carry a tag. The DOCS
project rule (`AGENTS.md`, Project rules): "README and MANUAL checked at
every step completion"; S172's and S173's stamps both say "README and
MANUAL unchanged, checked" — S171's stamp says nothing about either
document.

Impact: the release procedure is no longer derivable from the tracked docs
(the prime directive): the next release follows README and produces no tag,
or pushes without `--follow-tags` and the tag never reaches origin. The
DOCS gate exists to catch exactly this drift and was skipped on the one
step that changed the procedure.

Suggested resolution: add the tag and the `--follow-tags` push to README's
Ship order, in a step, since the section claims to be the current
procedure.

### 2026-08-29_adversarial.3-F06  low  the archive branch status.md and DEC-052 point at does not exist in this clone or its fetched remote refs

Status: closed  (S179; DEC-070 — the tip is gone, the claim withdrawn)

Evidence: `adocs/status.md:14-17` (Parked): "`watch-primitive-a304293`
holds the pre-merge tip … the branch stays as the archive of the unmerged
line"; DEC-052 makes the same claim. `git for-each-ref | grep -i watch` →
nothing (refs are `master`, `v1`, `origin/{HEAD,master,v1}`);
`git cat-file -t a304293` → "Not a valid object name" — the pre-merge tip
is not even an object in this clone, the machine DEC-052 was recorded on.
Not confirmed live against origin (no network from this session:
`git ls-remote` fails on auth), but the remote-tracking refs from the last
fetch show no such branch.

Impact: the parked note exists to remember where the unmerged 0.x line
lives; as far as this repository can show, it lives nowhere. The archive
claim is prose with no filesystem behind it — unverifiable exactly where
the prime directive says state must be derivable.

Suggested resolution: verify against origin with network; if the branch
exists there, amend the parked note to say remote-only; if not, recreate it
from a reflog or backup, or rewrite the note (and supersede DEC-052's
claim) to say the tip is lost.

### 2026-08-29_adversarial.3-F07  low  /moltke:rules sanctions dropping any Project rules line while the base ruleset hard-references five catalog ids

Status: closed  (S178)

Evidence: `skills/rules/SKILL.md:21`: "**Drop**: delete the line." — no
restriction on which. The shipped base ruleset depends on catalog ids being
present: `templates/AGENTS.md:71` "Respect PLAN's active limit", `:77`
"the TESTS and DOCS rules are satisfied", `:79-80` "commit per COMMITS",
`:102` "Fast check, when REVIEW says so". The catalog itself provides
recorded "none"/"no" lines for disabling a topic (TESTS none, DOCS none,
REVIEW no — `skills/init/SKILL.md:50,52,53`), so Drop on a catalog topic
leaves the base referencing an undefined rule where a defined "none" line
was available.

Impact: one sanctioned `/moltke:rules` operation makes an installed ruleset
self-inconsistent — the finish gate ("TESTS and DOCS rules are satisfied")
becomes unevaluable and every agent improvises its own reading.

Suggested resolution: one sentence in the rules skill: catalog topics are
changed (to their "none" option when wanted off), never dropped; Drop is
for non-catalog ids.

## Verdicts on the 2026-08-29_adversarial.2 findings

All three re-measured at `6cc8f96` from each finding's own reproduction.
Per this repository's rules the Status flips belong in the earlier report
and are the invoking session's to write; this report records the evidence.

- `2026-08-29_adversarial.2-F01` (plan.md and status.md misstate plan state
  at the release commit) — **close.** `plan_todo/` and `plan_current/` hold
  only `.gitkeep`; `adocs/plan.md:15` "Nothing open. 1.1.0 is tagged; the
  next id is S174" is true (highest id ever allocated is S173, checked
  across all three directories); `adocs/status.md:7-12` says last done
  S171, in progress none, next none — matching the directories; both files
  were rewritten in the completion commit (`6cc8f96` touches both).
- `2026-08-29_adversarial.2-F02` (branch (a) checks nothing but existence,
  so 1.0.0-initialised repositories can never be repaired) — **close.**
  `skills/init/SKILL.md:14-21`: branch (a) now checks the repair cases
  before stopping — unwired entry points get step 3's wiring offer, missing
  scaffold files the creation offer. The finding's reproduction
  (1.0.0-initialised repo, unwired `CLAUDE.md`, re-run init) now reaches
  the offer. Residue — the created-from-template `status.md`/`plan.md` are
  read back unreconciled — is this report's F02, per one-finding-one-home.
- `2026-08-29_adversarial.2-F03` (step 4 assumes fresh templates, directs
  ids from S001 and a status reset) — **close.**
  `skills/init/SKILL.md:110-113` no longer directs S001 into a populated
  plan (next free, S001 only when the directories are empty), and item 6 no
  longer writes "nothing done" over real state. Residue recorded
  separately: the "next free" wording re-admits burned-id reuse (this
  report's F03), and the "fresh or kept" rewrite contradicts INV-19 and
  S173's own accepts (this report's F01).

Older reports: no real `open` or `planned` finding remains anywhere else in
`adocs/audit/` — every remaining `Status: open`/`Status: planned` line sits
inside a fenced finding-format example in a report preamble (all eleven
hits checked individually), plus the known quoted fixture at
`2026-08-08_adversarial.2.md:561`.

## Where the product holds

Checked and clean, recorded so the absence of findings there is a result
and not a gap: root `AGENTS.md` base sections byte-identical to
`templates/AGENTS.md`; INV-18 holds (no executable file anywhere outside
`.git/`, markdown plus two JSON manifests, no hooks); INV-20 holds in the
ledgers (`decisions.md` index and body both 68 ids, sets match, body
strictly ascending; step ids unique across the three plan directories);
`v1.1.0` is an annotated tag on the audited commit and `plugin.json` says
1.1.0; S171–S173 carry `closes:` fields matching the run-2 findings
one-to-one; the migration prompt, MANUAL's install URL, and `plugin.json`'s
repository field are mutually consistent; `master` at 22 commits ahead of
`origin/master` is exactly the unpushed state `status.md` describes.

Stop rule (DEC-035): this run reports one medium, so it is not a stopping
run.
