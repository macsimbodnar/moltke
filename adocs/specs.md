# Specs: moltke

2026-08-01: created from `bootstrap.md` (DEC-012). The locked decisions of §2
moved to `adocs/decisions.md` as DEC-001..DEC-012; the first plan of §8 moved
to `adocs/plan.md` and step files S001..S011. Facts otherwise preserved.

2026-08-01: project renamed `max_agent_workflow` → `moltke` (DEC-015): CLI
`bin/moltke.py`, marker `.moltke.json`, skills `init`, `step`, `audit`.

2026-08-02 (S013): the workflow directory is renamed `project/` → `adocs/`,
agent documentation (DEC-021). Every path in this file, in `bin/moltke.py` via
the single `DOCS` constant, in the hook messages, and in the templates reads
`adocs/`. No migration path exists because no repository other than this one
had the plugin installed. Paths inside `plan_done/`, and inside `worklog.md`
and `decisions.md` entries predating DEC-021, still read `project/`: they are
immutable or append-only history and are never rewritten.

## Prime directive

Project state is always derivable from tracked files alone. An agent that
trusts nothing but the filesystem knows what to do next and why — in any
session, any tool, any machine.

## Invariants

Enforced by `bin/moltke.py` in marked repositories:

- INV-1  `plan_current/` holds at most `plan_active_max` non-paused steps.
- INV-2  stack depth in `plan_current/` never exceeds `plan_stack_max`.
- INV-3  every step file in `plan_todo/` and `plan_current/` appears in `plan.md`, and every id `plan.md` lists has a step file in one of the three directories. 2026-08-06 (S024): the second half is new; the invariant was one-directional before.
- INV-4  no step moves to `plan_done/` while another step names it in `blocks:`.
- INV-5  no step reaches `plan_done/` without a `done:` stamp and at least one `testing.md` row referencing its id.
- INV-6  step ids are unique across all three plan directories.
- INV-7  a file under `plan_done/` never changes or disappears after the commit that added it. 2026-08-06 (S018, F12): the original wording, "`plan_done/` is byte-identical to its state at session start", is superseded — it promised a session-scoped guarantee the code never implemented, and the 2026-08-01 amendment below redefined it without saying so.
- INV-8  no line `decisions.md` has ever held is removed or reordered. Inserting between entries passes; the ordering of the log is a convention, not an enforced property. 2026-08-06 (S030, DEC-025): narrowed from "`worklog.md` and `decisions.md`", which is superseded. The worklog is append-only by convention and no longer checked. 2026-08-07 (S054, DEC-030): the earlier wording, "grows only by appending; earlier bytes are unchanged", is superseded — it described an aspiration, not the check. The threat model is accident and drift, not a hostile author.
- INV-9  every `decisions.md` entry has a unique `DEC-<nnn>` id.
- INV-10 every audit finding is `open`, `planned`, `closed`, or `accepted`, and no report has `open` findings without a step or decision referencing them.
- INV-13 `plan.md`, `decisions.md`, `worklog.md`, and every audit report have an even number of code-fence markers. 2026-08-07 (S033): added, because an unclosed fence makes content invisible to every scanner that reads the file.

Properties of the checker itself:

- INV-11 every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is false. 2026-08-01 (S006, DEC-017): except the setup modes `--scaffold` and `--decline`, which run before the gate because they exist to create the marker; both still leave a declined repository untouched.
- INV-12 every blocking exit carries a message stating exactly what to do to unblock (DEC-006: a `Stop` hook has a cap on consecutive blocks; an unactionable message deadlocks the session).

2026-08-01 (S004): INV-8 uses the same git HEAD baseline as INV-7: the
committed content must be a byte-prefix of the current file; untracked files
have no baseline, so the check abstains. INV-10 fixes the audit finding
format ahead of S008: a finding is a `### <report>-F<nn>` heading followed by
a `Status: <value>` line in its section; the S008 report template must conform.

2026-08-01 (S003): INV-7 is checked against git HEAD: tracked files under
`plan_done/` are never modified or deleted; additions are the one legal change
(append by move only). Repos without git history have no baseline, so the
check abstains. INV-3 additionally treats a missing `plan.md` in an enabled
repo as a violation.

2026-08-07 (S054, DEC-030): INV-8's wording now describes the check rather than
an aspiration. What runs is a line rule — nothing the file has ever held is
removed or reordered — so an insertion between entries passes once committed
(finding 2026-08-07_adversarial.2-F07). The two halves of the check differ, and
the difference is worth knowing rather than smoothing over: the uncommitted
window is a byte-prefix comparison against `HEAD`, so a mid-file insertion is
reported until it is committed and not after. Neither half is being grown to
close that, because DEC-030 sets the threat model at accident and drift, and the
line rule is what catches an agent clobbering history by mistake.

2026-08-07 (S047, DEC-029): the `--stop` waiver counts retries within one turn.
"The same turn" is `prompt_id` and `session_id` when the payload carries them,
plus the count of prompt headings in `adocs/worklog.md`, which `UserPromptSubmit`
advances exactly once per turn — so the key no longer depends on a payload field
no observation in this repository establishes (finding 2026-08-07_adversarial.2-F01).
The count also resets when the set of problems changes, so partial progress does
not spend attempts, and the problems are printed before the waiver allows the
stop. Measured: eight turns read `2 2 2 2 2 2 2 2` where they read
`2 2 2 0 0 0 0 0`, while eight retries inside one turn still read
`2 2 2 0 0 0 0 0`, which is the no-deadlock property working. `mode_stop` reads
stdin once and shares the payload, since a second `hook_input()` in the same
process would see an empty dict.

2026-08-07 (S042): the suite-gate banner prints to stderr with the refusal it may
turn into. It went to stdout while `refuse` wrote to stderr, so the one refusal
that S025's own `TestRefusalsGoToStderr` did not cover was the one that broke the
rule it states, and a consumer switching streams on the exit code got half the
message (finding 2026-08-07_adversarial-F11). The banner is progress, not a
finding, and on a passing gate it is now stderr output on an exit 0 path — a case
S025 already documents. The "no `test_command` configured" notice stays on stdout,
because it accompanies a successful completion rather than a refusal.

2026-08-07 (S040): `--audit new` refuses a type that is not `[A-Za-z0-9_-]+`,
before anything touches the filesystem. The type went straight into a filename
and `audit_new` creates the parent directories, so `../../outside/pwned` wrote a
report outside the `audit_dir.glob("*.md")` that both `inv_10_audit_findings` and
`audit_list` read — filed, and counted by nothing — left a stray directory
behind, and degraded the finding-id stem to the last path component. The printed
path was computed lexically with `relative_to`, so it still looked contained
(finding 2026-08-07_adversarial-F09). A dot is refused too, because it would
collide with the `.2` namespace S020 reserved for same-day re-runs.

2026-08-07 (S041): `--pre-write` resolves the path before any rule reads it.
pathlib does not normalise `..`, so a relative path only had to begin with an
allowed component: `tests/../bin/moltke.py` was permitted for the reviewer while
its absolute form was blocked, since absolute paths were already resolved
(finding 2026-08-07_adversarial-F10). One `rel` feeds the reviewer fence, the
`plan_done` rule, and the step-file rule, so all three were affected and all
three are fixed together. A path that resolves outside the repository root stays
unpoliced, which is the existing boundary and is deliberate: moltke governs the
repository it is marked in. That narrows S041's own acceptance wording, which
asked for any escape to be refused; the finding claimed only the in-repository
case.

2026-08-07 (S036): `--audit new` records the worklog's length and content hash,
and `--audit check` treats a worklog change as expected when the file still
starts with exactly those bytes. `UserPromptSubmit` appends on every prompt, so
every audit spanning a prompt had a worklog change in its footprint, attributed
to a reviewer that is fenced out of that file and never touched it — a gate wrong
every time is one people learn to wave through, and F01 is what it was letting
past while it cried wolf (finding 2026-08-07_adversarial-F05). Scoped to appends,
not to the path: an append is what the hook does, a rewrite is what covering your
tracks looks like and stays reported. The length-plus-hash pair proves growth
without keeping a copy of the file. It applies to the committed side too, or
committing during a run would bring the false positive back.

2026-08-07 (S037): the `--stop` recap gate exempts `adocs/` and `.claude/` by
directory, with their separators, listed in `RECAP_EXEMPT`. `.claude` as a bare
prefix also matched `.claude-plugin/plugin.json` — the manifest whose `version`
decides what every installed copy of moltke executes, so a release could be cut
with no recap of it — and `.clauderc` or any future `.claude*` file at the root
inherited the same hole (finding 2026-08-07_adversarial-F06). The exemption is
for the two directories only; `adocsfoo/` is source like anything else.

2026-08-07 (S039): `status.md` staleness is judged on all four derived fields —
Last done, In progress, Next, Blocked — against exactly what `--step status`
would regenerate, sharing one `status_lines` so the check compares against the
writer rather than against a second description of it. The `Updated:` line and
everything from `- Parked:` onward are the human's and are ignored. Only `Next:`
was compared before, and that is the one field the file and the filesystem rarely
disagree about, because both derive it the same way; the in-progress stack is
what a crashed session corrupts, and AGENTS.md section 1 names exactly that
scenario (finding 2026-08-07_adversarial-F08). Two consequences of the stricter
comparison: `status_lines` distinguishes "no steps planned yet" from "no steps
left in plan.md", so a freshly scaffolded `status.md` matches what would be
regenerated, and `Last done` is read through `plan_order` rather than every id in
`plan.md`, which S045 had already fixed for `derived_next` and not here.

2026-08-07 (S038): `--step` receives the marker violations, as `--validate`,
`--post-write`, and `--stop` already did, and refuses every operation while the
marker is malformed. `check_marker` flagged a bad `test_command` and `mode_step`
never saw it, so `--step done` completed green while reporting that the key was
absent — the failure DEC-023 added the key to remove, reached by a typo, and
reported by a different command than the one being run (finding
2026-08-07_adversarial-F07). Blank, whitespace, a list, and a number all refuse
now, and the step stays in `plan_current/`.

2026-08-07 (S032): `--audit new` records the `HEAD` sha alongside the worktree
snapshot, and `--audit check` reports `git diff --name-status --no-renames` from
that sha to `HEAD` as part of the run's footprint. Comparing two `git status`
snapshots alone meant a clean tracked file the run patched and committed appeared
in neither, so the check printed "no change since --audit new" for a run that had
rewritten source — and DEC-022 traded the write fence away for exactly this check,
so `git commit` defeated its replacement (finding 2026-08-07_adversarial-F01). A
commit is classified by the same rule as a working-tree change: the report and
files added under `tests/` are expected, anything else is not. A baseline `HEAD`
that is no longer reachable is reported rather than skipped, since that means
history was rewritten under the run.

2026-08-07 (S033): `strip_guidance` pairs code-fence markers that open a line,
in order, and leaves an unpaired trailing marker as text. It paired ``` globally
and non-greedily before, so one stray marker shifted every later pairing and
deleted the real content between two unrelated fences — a rule for making
guidance invisible was making evidence invisible instead (finding
2026-08-07_adversarial-F02, which the report reproduced on itself: `--audit list`
saw two findings of eleven and exited 0). Line-anchoring also means a marker
quoted in a worklog prompt, which arrives as `> ```` because every prompt line is
quoted, is not a fence at all.

Two unclosed fences remain indistinguishable from one closed fence, and no
content heuristic can separate them: the templates deliberately put headings
inside fences, which is what `strip_guidance` exists for — the audit report
template's example finding is one. So that case is reported rather than guessed,
which is INV-13. `--post-write` does not run it; the worklog grows without bound
and this reads it whole.

2026-08-07 (S035): moltke's own state files are located by asking git, through a
single `git_dir` running `git rev-parse --absolute-git-dir`, not by testing
whether `.git` is a directory. In a linked worktree and in a submodule it is a
file, so all three call sites failed together and silently: no audit baseline,
with `--audit new` reporting "no git worktree here" inside a worktree where git
works; `--audit check` refusing forever and naming a remedy that could not work;
no prompt-failure breadcrumb, degrading S014's fix back to losing prompts; and no
`Stop` deadlock cap, which is INV-12 and DEC-006, measured as `[2,2,2,2,2]`
against a clone's `[2,2,2,0,0]` (finding 2026-08-07_adversarial-F04). All three
now resolve per worktree, which is what these files want to be. Verified across a
clone, a linked worktree, and a submodule, all `[2,2,2,0,0]`. A directory with no
git still abstains, and the `--audit new` warning now says "no git repository",
which is what it actually means.

2026-08-07 (S046, DEC-028): INV-8's history check keeps a high-water mark instead
of one fixed baseline, closing the gap DEC-027 accepted. Versions are walked
oldest first: one that still contains, in order, every line the mark requires
becomes the new mark; one that dropped something is a tampering and is skipped.
The file as it stands must contain the mark's lines, in order. A committed
rewrite of text appended after the first commit is now caught, and a repair still
clears. Two consequences worth knowing: mid-file insertion passes, because only
removal and reordering break a subsequence, and reordering entries is a violation
until reversed. The gap row DEC-027 measured, "the same rewrite committed", moved
from exit 0 to exit 1 with the other four states unchanged.

2026-08-07 (S034, DEC-026 and DEC-027): both invariants judge current content
against a fixed historical version instead of the existence of a bad commit, so
restoring what was removed clears the violation. S018's rule had no terminal
state: history is permanent, so following the violation message left `--validate`
at exit 1 forever and only a history rewrite — which the same message forbids —
would have cleared it (finding 2026-08-07_adversarial-F03). INV-7 compares each
`plan_done/` file against the version at the commit that added it, and a file
that is gone is a violation until it is restored. INV-8 compares `decisions.md`
against the version at its first commit. Both fetch blobs through one batched
`git cat-file`. The naive form of INV-8, requiring every past version to be a
prefix, is unsatisfiable after a repair because the tampered version is itself
history; DEC-027 records that, the two alternatives measured against the suite,
and the resulting gap — a rewrite of text appended after the first commit is
reported while uncommitted and not once committed, which is S046. The HEAD
comparisons covering the uncommitted window are unchanged.

2026-08-06 (S018): INV-7 and INV-8 each check two baselines, because HEAD alone
was never a baseline — it moves at every step completion, so committing the
tampering erased the violation (finding F04). The working-tree comparisons above
stay, covering the uncommitted window; git history covers everything already
committed. INV-7 reads `git log --name-status` over `plan_done/` and treats any
status other than `A` as a violation, naming the commit. INV-8 reads
`git log --numstat` over `decisions.md` and treats any commit that removed lines
as a violation, which is line granularity rather than bytes: an in-place edit
still reads as one line removed and one added, so it is caught either way. Both
pass `--no-renames`, so a move into the directory reads as the addition it is —
this is what keeps the S013 `project/` to `adocs/` rename legal — and a move out
reads as the deletion it is. Both still abstain with no history. Neither is in
`CHEAP_CHECKS`, so `--post-write` does not pay for them.

Each invariant gets a test, and each test gets a `testing.md` row. Red-first
applies: write the test, watch it fail against a deliberately broken fixture
repository, record what it printed, then implement.

## What is being built

A Claude Code plugin that installs and enforces a document-driven development
workflow in any repository. The workflow gives an agent durable, cross-session,
cross-tool memory of a project: what to do next, why past choices were made,
what has been audited, and what is verified.

Name: `moltke`
Distribution: git repository plus a plugin marketplace entry, installed on each dev machine.

Before implementing hooks, plugins, or skills, fetch the current Claude Code
documentation and verify the APIs. This spec was written on 2026-08-01 and the
plugin and hook surfaces change. Do not trust the shapes below over the live docs.

## Plugin layout

```
moltke/
  .claude-plugin/plugin.json
  AGENTS.md                       # live rules for this repo
  CLAUDE.md                       # @AGENTS.md
  README.md                       # layout, build, test, exact commands
  MANUAL.md                       # install, operate, known bugs
  .moltke.json                    # this repo is itself marked
  skills/
    init/SKILL.md
    step/SKILL.md
    audit/SKILL.md
  agents/
    adversarial_reviewer.md
  hooks/
    hooks.json
  bin/
    moltke.py                     # single entry point for all checks
  templates/
    AGENTS.md                     # shipped copy of the ruleset
    CLAUDE.md
    cursor_rules
    moltke.json
    adocs/
      status.md
      specs.md
      plan.md
      decisions.md
      testing.md
      worklog.md
    step_template.md
    audit_report_template.md
  tests/
  adocs/                        # this repo's own workflow state
```

## bin/moltke.py

One script, several modes. Every hook shells out to it. Keeping the logic in
one place means other tools (Codex, Cursor) can run the same checks manually,
which is the only enforcement available outside Claude Code.

| Mode | Called from | Behavior |
|---|---|---|
| `--session-start` | SessionStart hook | print `plan_current/` contents and the derived next step; flag `status.md` as stale if it disagrees |
| `--log-prompt` | UserPromptSubmit hook | append timestamp and verbatim prompt to `adocs/worklog.md` |
| `--pre-write PATH` | PreToolUse on Write and Edit | exit 2 if the path is under `plan_done/`, or is a step file outside the three plan directories |
| `--post-write` | PostToolUse | cheap invariant scan, non-blocking |
| `--stop` | Stop hook | exit 2 with an actionable message if source changed without a worklog recap, a stale `status.md`, a completed step lacking `testing.md` rows, or unchecked README and MANUAL |
| `--validate` | manual, any tool | run every invariant, report all violations, exit non-zero |
| `--scaffold` | `init` skill | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `adocs/` from templates; never overwrites an existing file |
| `--decline` | `init` skill | write `{"schema": 1, "enabled": false}`, durably; refuses to disable an already-enabled repository |
| `--audit OP ...` | `audit` skill | 2026-08-01 (S008): `new <type>` opens `adocs/audit/YYYY-MM-DD_<type>.md` from the template and never overwrites, taking a `.2`, `.3` sequence suffix on a same-day re-run (S020); `list` prints every finding with its status and what references it, exiting non-zero while an open finding has neither a step nor a decision. 2026-08-06 (S017): `new` also records a working-tree baseline in `.git/moltke_audit_baseline.json`, and `check` reconciles the run against it, printing expected and unexpected changes and exiting 1 on anything unexpected |
| `--step OP ...` | `step` skill | 2026-08-01 (S007): lifecycle operations `new <name> [--goal]`, `start <id>`, `block <parent> <name>`, `done <id> --stamp`, `status`. Each refuses rather than repairs, naming the missing condition; no transition may leave INV-1..INV-7 violated. 2026-08-06 (S021): `done` additionally runs the optional `test_command` suite gate and refuses on a non-zero exit |

Every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is
false (INV-11).

2026-08-01 (S005), verified against live hook docs: `--pre-write`'s PATH is
optional; hooks pass the path via stdin JSON (`tool_input.file_path`).
`--log-prompt` always exits 0 because UserPromptSubmit exit 2 erases the
user's prompt. `--session-start` emits `hookSpecificOutput.additionalContext`
JSON, the only channel that reaches the model. Stop has no documented block
cap anymore, so `--stop` imposes its own: after 3 consecutive blocks for the
same prompt it allows the stop with a warning (state in
`.git/moltke_stop_state.json`), preserving the DEC-006 no-deadlock property.
— Amended 2026-08-07 (S047, DEC-029): "the same prompt" was `prompt_id` alone,
which nothing establishes the Stop payload carries, and an absent key made the
counter global and persistent so the waiver became an off switch from the fourth
blocked turn onward.
`--stop`'s README/MANUAL gate is mechanical: a step file newly moved into
`plan_done/` must mention README and MANUAL in its `done:` stamp.

2026-08-06 (S030, DEC-025): `APPEND_ONLY_FILES` holds `decisions.md` alone.
Rewriting, trimming, or deleting `adocs/worklog.md` is no longer a violation:
nothing cites a worklog line by id, it is forensic and never a context source
(DEC-011), and enforcing it is what made a secret pasted into a prompt
unremovable. `decisions.md` keeps enforcement because `DEC-<nnn>` ids are cited
from code comments, commit messages, `specs.md`, and step files, so a rewritten
entry silently changes what every one of those citations means; the refusal now
says so. INV-7 and `plan_done/` are untouched.

2026-08-06 (S017, DEC-022): prevention gives way to reconciliation. `--audit new`
records a working-tree baseline in `.git/moltke_audit_baseline.json` — captured
before the report is written, so the report is part of the run's footprint and is
classified rather than invisible — as `{path: [porcelain status, sha256]}` over
`git status --porcelain -uall`. `-uall` because plain porcelain collapses a wholly
untracked directory into one entry, which would hide the report inside
`adocs/audit/`. The hash is what catches a file edited before the audit and edited
again during it, whose status never moves. `--audit check` then prints the
footprint split in two: this run's own report and new files under `tests/` are
expected, everything else — including a modified existing test, and a
pre-existing change reverted — is unexpected, exits 1, and says to review each
change with `git diff` before acting on any finding. Pre-existing dirt is in the
baseline, so it is never attributed to the run. Without git, or before `--audit
new` has run, `check` refuses and names what to run; ignored paths are outside
`git status` and so outside this check.

The fence widens to match: the reviewer may write under `adocs/audit/` and may
create new files under `tests/`, since a red-first regression test is evidence
while editing an existing test is a patch. `Bash` stays unconstrained by design
(DEC-022 rejected inspecting command strings as unparseable), so the fence is a
fast clear failure on the common path, never the guarantee.

2026-08-06 (S016): the reviewer write fence matches the scoped `agent_type`.
Observed live, by instrumenting the installed 0.2.0 hook to dump its PreToolUse
payload and spawning each agent through the plugin: a plugin subagent sends
`agent_type: "moltke:adversarial_reviewer"` plus an `agent_id`, a built-in
subagent sends `agent_type: "general-purpose"`, and the main thread sends neither
key. So bare equality never matched and the fence failed open (F02). The match is
now on the part after the last colon, which keeps working if the plugin is
installed under another name; the cost is that another plugin's agent named
`adversarial_reviewer` would also be fenced, chosen deliberately because that
blocks loudly while the alternative fails open silently. An absent `agent_type`
is the main thread and is never fenced. The fence covers `Write` and `Edit` only:
the reviewer also holds `Bash`, whose writes no PreToolUse matcher sees, which is
DEC-022's territory and S017's.

2026-08-06 (S015): `--stop`'s recap gate no longer reads worklog growth. Growth
cannot be the signal, because `UserPromptSubmit` appends the prompt before the
turn begins, so by the time `Stop` runs the worklog has always grown and the
comparison was always false (finding F01). The gate now asks whether a `## …`
heading containing `recap` follows the last heading ending in `prompt`. A heading
matching both reads as a recap, so a recap titled after prompt handling still
counts. Headings inside fenced blocks are guidance, not data. The gate abstains
when the repository has no `HEAD` commit: there is no history a recap would sit
alongside, and a fresh `--scaffold` is not work — the same abstain INV-7 and
INV-8 make. This removes `--stop`'s last dependence on the worklog's git
baseline, which DEC-025 is about to drop.

2026-08-06 (S014): `--log-prompt` creates `adocs/` before appending, so a marked
repository whose docs tree is missing still records the prompt. When the append
fails anyway it writes `.git/moltke_log_failure.json` (`since`, `count`,
`error`), and `--session-start` reports that once in `additionalContext` and then
removes it: `UserPromptSubmit` must exit 0, so stderr reaches nobody, and
`SessionStart` is the only channel that reaches the model. Reporting once rather
than until cleared keeps it self-healing — a failure that persists rewrites the
breadcrumb on the next prompt, one that is fixed goes quiet. Nothing is written
outside `.git/`, because an untracked file at the repo root reads as a source
change to `--stop`. Without a `.git` directory there is no breadcrumb and the
failure is stderr-only. Lost prompts are not recovered: the breadcrumb records
that logging failed, not what was said (finding F14).

2026-08-02 (S011): `README.md` and `MANUAL.md` exist, so the MANUAL half of the
surface guard is live: it was verified to bite by removing `--decline` and
`--audit list` from MANUAL and observing the failure name exactly those two.

2026-08-01 (S009): the surface guard (`surface_guard: "cli"`, DEC-010) is
`tests/test_s009_surface.py`, holding `tests/golden/cli_surface.txt`. It reads
argparse's actions rather than `--help` prose, so help wording can change but a
flag or `--step`/`--audit` operation cannot be added, renamed, or removed
silently. A separate check requires every flag and operation to appear in the
specs CLI table, and an operation counts only where its own mode is described,
so refreshing the golden alone never makes the suite green. Refresh, after
updating the docs, with `python3 tests/test_s009_surface.py --refresh`. The
same check runs against `MANUAL.md` and is skipped until that file exists in
S011; closing that gap is part of S011.

2026-08-07 (S045): `derived_next` reads plan order from `plan.md`'s list entries
only — a line beginning `1.`, `-`, or `*` — through the new `plan_order`. Reading
every id in document order meant a description paragraph decided the next step:
listing the 2026-08-07 findings, a sentence reading "ahead of the feature work
S028, S029, and S031" above a list starting at S034 made `--step status` write
`Next: S028`, with `--validate` green throughout, because INV-3's reverse
direction is satisfied by ids that do have files. Order lives in the list and
nowhere else (DEC-008), so the list is what the code reads. INV-3 still scans the
whole file in both directions: a prose id with no step file is a typo worth
reporting even though it no longer reorders anything.

2026-08-06 (S024): INV-3 gained its reverse direction. `derived_next` returns the
first id in `plan.md` order regardless of whether a file exists, so a mistyped id
became the next step forever — `--session-start` announced it every session and
`--step status` wrote it into `status.md`, so the two agreed and nothing looked
wrong (finding F11). An id listed in `plan.md` with no file in any of the three
plan directories is now a violation naming the id and both fixes. Ids are read
through `strip_guidance` like everything else, so the scaffolded plan's commented
example step is still not a phantom. `derived_next` itself is unchanged and still
returns the phantom: the reported residual is that `--session-start` announces it
while `--validate`, `--post-write`, and `--stop` all name it as a violation, so it
is loud rather than silent, but a resumed session sees the phantom first.

2026-08-06 (S023): the surface guard covers what a plugin user touches, not only
argparse. The golden gained three lines — the declared skills, the declared hook
events, and `MARKER_KEYS`, the `.moltke.json` keys `check_marker` recognises — so
adding, renaming, or removing any of them fails it, and the specs-and-MANUAL
cross-check applies to each exactly as it does to flags. A skill counts as
documented only where it is named as a component, `/moltke:<name>` or in
backticks, since "step" and "audit" are words this documentation uses constantly.
Before this, `SKILLS` was hardcoded in `tests/test_s010_plugin.py` so a fourth
skill was invisible, and the hook assertion was satisfied by any one surviving
event, so deleting `Stop` outright left the suite green — verified before the fix
(finding F10). Both are now derived from the declarations in `tests/surface.py`,
which is the single home for them. `MARKER_KEYS` is pinned to reality by a test
that gives every declared key an invalid value and requires `check_marker` to
name it, so the list cannot become decorative; an undeclared key stays ignored
rather than rejected, so no existing marker breaks.

2026-08-06 (S022, DEC-024): `tests/test_s022_secrets.py` fails when a prefixed
key shape or a PEM private-key header appears in `adocs/worklog.md`, satisfying
AGENTS.md section 6's requirement that secret-leak checks run inside the normal
suite. Prompts are written verbatim, so the worklog is a secret sink in a tracked
file that DEC-002 makes public here (finding F08). Detection, not redaction:
DEC-024 rejected redacting at write time because it contradicts the verbatim
guarantee and a false positive would destroy forensic content silently. Fixed
prefixes and PEM headers only — no entropy or bare-hex rule, which would fire on
the commit sha in every recap. Non-vacuous by construction: each shape is first
asserted to match its own synthetic example, and the scan is asserted to report a
planted one at the right line, before either is pointed at the real file. S030
already removed the worse half of F08: the worklog left INV-8, so cleaning a leak
is an ordinary edit rather than an invariant violation. Two limits stand: the
check lives in moltke's own suite and does not travel to repositories that install
the plugin, which is S031, and it scans the worklog only.

2026-08-06 (S021, DEC-023): `.moltke.json` gains an optional `test_command`
string, and `--step done` runs it after every other gate and before it touches
anything, refusing on a non-zero exit with the command, the exit code, and the
last 20 lines of combined output. It runs with `shell=True` from the repository
root, under a 600 second timeout; a timeout or a command that cannot start is a
refusal, not a pass. Absent, behaviour is exactly as before and `--step done`
says out loud that nothing ran the suite — AGENTS.md requires a green suite at
completion and until this key existed nothing enforced it, while MANUAL disclosed
only the weaker README/MANUAL mechanical-gate problem (finding F07). A
`test_command` that is not a non-empty string is a marker violation, because
gating nothing silently is the defect this key removes. Schema stays 1, so no
existing marker migrates. This repository sets it to
`python3 -m unittest discover -s tests`.

2026-08-06 (S020): `--audit new` allows a same-day re-run. Closure requires a
re-run and the filename came from today's date, so a finding fixed on the day it
was reported had no compliant way to close — the tool's own advice was to wait a
day or invent a type name, which corrupts the stem that INV-10 keys on (finding
F09). Re-runs take a sequence suffix, `YYYY-MM-DD_<type>.2.md`, `.3.md`, and an
existing report is still never overwritten. INV-10's stem check becomes an exact
`<stem>-F<nn>` match rather than `startswith`, because the suffix makes the first
report's stem a prefix of the re-run's and a re-run's finding id would otherwise
sit unnoticed inside the first report.

2026-08-06 (S019): the rule below was stated universally and had one exception
until now — `finding_references` read `decisions.md` raw, so a finding id inside
a fenced example discharged a real open finding, and the scaffolded
`decisions.md` ships exactly such an example (finding F05). It reads through
`strip_guidance` like everything else. That makes the sentence below true rather
than aspirational; it is the fifth time this defect appeared.

2026-08-01 (S008): **template guidance is never data.** Every scanner reads
its input through `strip_guidance`, which drops fenced blocks and HTML
comments, so a commented example step is not planned, an example finding is
not open, and an example `DEC-001` does not consume the id. This rule exists
because the same defect appeared four separate times: commented plan steps,
example findings, the `paused_by` placeholder, and a scaffolded project whose
first real decision collided with the template's own example.

2026-08-01 (S008): INV-10 additionally requires a finding id to carry its own
report's name, so ids cannot drift between reports when an audit is re-run.
The reviewer's write fence is enforced in `--pre-write` using the PreToolUse
`agent_type` field: subagent frontmatter has no path-level restriction, so the
hook is the only place the limit can be real. — Superseded 2026-08-06 (S017,
DEC-022): the last sentence was wrong. The hook only sees the tools its matcher
names, and the reviewer also holds `Bash`, so the fence was never the limit; see
the S017 note below.

2026-08-01 (S007): unfilled template placeholders (`<!-- ... -->`) in a step
field read as empty everywhere, so a hand-copied `step_template.md` cannot
silently look paused. INV-4 counts `blocks:` declarations only from open steps:
a completed child's `blocks` field is history, not a live block.

2026-08-01 (S006): step ids are read from `plan.md` with HTML comments and
fenced blocks stripped, so commented-out example steps are not the plan. Found
by scaffolding a real repository: the template's example line produced a
phantom next step, a false stale-`status.md` report, and a Stop block on the
first turn.

Language: Python, standard library only. It runs on every prompt, so startup
cost matters and dependencies are unacceptable.

## Skills

**`init`.** Detects a missing or disabled marker, asks once whether to set the
workflow up, and either scaffolds from `templates/` or writes
`{"enabled": false}` and never asks again. Scaffolding writes `AGENTS.md`,
`CLAUDE.md`, the Cursor pointer, `.moltke.json`, and a populated `adocs/`.
Acceptance: running it twice is idempotent; declining is durable across
sessions; a repository with an existing `AGENTS.md` is never overwritten
without asking.

**`step`.** Manages the lifecycle: create a step, promote to current, pause a
parent and promote a blocking child, complete a step, regenerate `status.md`
from the filesystem. Acceptance: every transition leaves invariants 1 to 7
satisfied; completion is refused when the gate conditions are unmet, with the
specific missing condition named.

**`audit`.** Runs an audit through the `adversarial_reviewer` subagent, writes
a dated report with per-finding ids and severities, then proposes plan steps
carrying `closes:` links. Acceptance: the report is written before any fix;
findings map one-to-one to steps or to decisions with a stated reason;
re-running the audit is what moves a finding to `closed`.

## Subagent and hooks

`adversarial_reviewer` runs with read tools plus write access limited to
`adocs/audit/`. It cannot edit source. This is deliberate: a reviewer that
can fix what it finds stops producing evidence and starts producing patches.

Hooks in `hooks/hooks.json`, all delegating to `moltke.py`: `SessionStart`,
`UserPromptSubmit`, `PreToolUse` matching Write and Edit, `PostToolUse`,
`Stop`. Verify event names and the JSON schema against current documentation
before writing the file.

## Non-goals

- Enforcement outside Claude Code. Codex and Cursor read the rules and can ignore them. `--validate` is the only lever, invoked manually.
- Any project-specific content in templates. See DEC-002.
- Migrating existing repositories automatically. `init` scaffolds fresh; adopting an in-flight project is a manual exercise for now.

## Open items

- Confirm DEC-002 (public repository) before the first push. Resolves when Max pushes (DEC-014).
- Decide whether `status.md` earns its place after a few weeks of real use, or whether `plan_current/` plus the derived next step is sufficient on its own.
