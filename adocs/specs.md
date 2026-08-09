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
- INV-3  every step file in `plan_todo/` and `plan_current/` is a list entry in `plan.md`, and every id `plan.md` lists has a step file in one of the three directories. An id named only in the description is prose: neither listed nor a phantom. 2026-08-06 (S024): the second half is new; the invariant was one-directional before. 2026-08-07 (S048): "appears in" became "is a list entry in", so this and `derived_next` share one definition.
- INV-4  no step moves to `plan_done/` while another step names it in `blocks:`.
- INV-5  no step reaches `plan_done/` without a `done:` stamp and at least one `testing.md` row referencing its id.
- INV-6  step ids are unique across all three plan directories.
- INV-7  a file under `plan_done/` never changes or disappears after the commit that added it. 2026-08-06 (S018, F12): the original wording, "`plan_done/` is byte-identical to its state at session start", is superseded — it promised a session-scoped guarantee the code never implemented, and the 2026-08-01 amendment below redefined it without saying so.
- INV-8  no line `decisions.md` has ever held is removed or reordered. Inserting between entries passes; the ordering of the log is a convention, not an enforced property. 2026-08-06 (S030, DEC-025): narrowed from "`worklog.md` and `decisions.md`", which is superseded. The worklog is append-only by convention and no longer checked. 2026-08-07 (S054, DEC-030): the earlier wording, "grows only by appending; earlier bytes are unchanged", is superseded — it described an aspiration, not the check. The threat model is accident and drift, not a hostile author.
- INV-9  every `decisions.md` entry has a unique `DEC-<nnn>` id.
- INV-10 every audit finding is `open`, `planned`, `closed`, or `accepted`, and no report has `open` findings without a step or decision referencing them.
- INV-13 `plan.md`, `decisions.md`, `worklog.md`, and every audit report have an even number of code-fence markers. 2026-08-07 (S033): added, because an unclosed fence makes content invisible to every scanner that reads the file.
- INV-14 no audit report states a finding under its own name that `strip_guidance` then removes. 2026-08-08 (S049, DEC-033): added, because parity catches one unclosed fence and not two — two are an even count that pairs as one closed fence and deletes the finding between them. 2026-08-08 (S075): comments come out before the comparison, so a heading inside one is guidance like any other commented content rather than a finding a fence swallowed — the message named a cause that was not present and a remedy that could not be followed.
- INV-15 `worklog.md` holds nothing shaped like a credential: prefixed key shapes and PEM private-key headers. 2026-08-08 (S031, DEC-032, DEC-024): added, because prompt logging writes verbatim into a tracked file in every repository moltke is installed into, and the tool doing the writing is the one that should say so. Detected, never redacted, and never printed beyond the first 8 characters.
- INV-16 `specs.md` never states a prime directive that `strip_guidance` then removes. 2026-08-08 (S063): added, because INV-13's parity cannot see an even marker count and a written-but-unreadable directive reads as unwritten to every check, including the planning nudge. 2026-08-08 (S078): it compares the section against its stripped form rather than testing both sides for emptiness, so a directive fenced beside other prose is reported too — the section is one sentence by design, and anything a fence removes from it is content no check can read.

Properties of the checker itself:

- INV-11 every mode exits 0 immediately when `.moltke.json` is absent or `enabled` is false. 2026-08-01 (S006, DEC-017): except the setup modes `--scaffold` and `--decline`, which run before the gate because they exist to create the marker; both still leave a declined repository untouched.
- INV-12 every blocking exit carries a message stating exactly what to do to unblock (DEC-006: a `Stop` hook has a cap on consecutive blocks; an unactionable message deadlocks the session). 2026-08-07 (DEC-031): the cap needs somewhere to keep its count, so it exists wherever git does — a plain clone, a linked worktree, a submodule — and not in a repository with no git at all, where every `Stop` blocks until the problem is fixed. Accepted, not planned. 2026-08-08 (S080, DEC-039): the qualifier widens from a repository with no git to anywhere moltke cannot write its state beside the git directory — an unwritable `.git` is the same accepted gap, and the message now names the missing cap instead of leaving it a mystery.

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

2026-08-09 (S100): the Parked block is carried through with its blank lines. S094 carried
it to the end of the file and still kept only non-blank lines, while `adocs/specs.md` and
`skills/step/SKILL.md` both say "verbatim": paragraphs merged and a heading written below
the list lost its separation, at every step transition, on a command that reports success
(finding 2026-08-09_adversarial-F04). Only trailing blank lines are trimmed, so keeping them
cannot grow the file a line per transition; regeneration stays idempotent and has a test
asserting a second and third run are byte-identical. The documented word and the implemented
one now agree.

2026-08-09 (S099): `--goal` and `--stamp` are refused when they contain a line break,
before anything is written. S095 gave `parse_step_file` a rule for multi-line values and no
writer honoured the other half of it: `write_step`, `append_to_plan` and `with_field` each
interpolate the value into one f-string, so a newline landed flush left — the one shape the
parser is documented to drop (finding 2026-08-09_adversarial-F03). `--goal` with a newline
put a list entry into `plan.md` that nobody typed and that `--validate` then reported as
INV-3; `--stamp` with the README and MANUAL mention on its second line passed the gate that
reads the string, wrote a file that reads back without it, left `--validate` green, and
blocked every Stop for the rest of the turn with a remedy that cannot be followed — the file
is under `plan_done/`, which `--pre-write` refuses, and editing it from Bash turns the block
into INV-7. Refused rather than reflowed, because a stamp is evidence and silently rewriting
it is the same class of quiet transformation the truncation was. The tests drive both
operands through the CLI and read the written file back through `parse_step_file`; that
round trip is what the S095 tests skipped by hand-writing their fixtures, which is why the
defect survived that step.

2026-08-09 (S098): INV-1's pause rule is "the pause resolves" rather than "the pauser
exists", and `--step unpause` clears exactly what INV-1 reports. S090 closed the phantom
pauser and left the neighbouring case: a step whose `paused_by` names itself, or a ring of
steps pausing each other, satisfies that rule because every pauser exists, and is just as
stuck — none of them counts as active so INV-1 and INV-2 report nothing, `--step done` sends
you to the pauser and `--step unpause` sends you back to `--step done`, the two commands
naming each other (finding 2026-08-09_adversarial-F02). Reachable by a one-token slip:
AGENTS.md §4 says to set `paused_by: <child_id>` on the parent, and the file being edited is
the parent. A pauser in `plan_done/` terminates the walk instead of continuing it, which is
S070's stale pause and is unchanged. `unresolvable_pauses` is shared by the invariant and by
`--step unpause`, so the remedy the violation names is the remedy that works rather than a
second description of it. DEC-040 is kept, not repealed: a pause resolving to live work is
still refused.

2026-08-09 (S097): `--step new` and `--step block` refuse when the next id would pass
S999, before anything touches the filesystem. `next_step_id` had no upper bound while
`STEP_FILE_RE` and `PLAN_ENTRY_RE` both require exactly three digits, so at the ceiling the
allocator produced an id nothing in the tool can read: `S1000_x.md` on disk, `S1000` listed
in `plan.md`, and `plan_steps`, `plan_order`, `derived_next`, `--roadmap`, `--session-start`
and every invariant blind to it at once, with `--validate` green and no CLI path back
(finding 2026-08-09_adversarial-F01). INV-3 could not report it in either direction: the
file is not a step file and the entry is not a list entry. Two triggers, both real — any
`S999` token in `plan.md` prose, which the shipped plan template explicitly invites, and the
id space genuinely running out, which this repository is 900 steps from. This is
2026-08-08_adversarial.4-F01 in its other half: S088 validated the step *name* in the same
filename and left the *id* unchecked. Widening the id space to four digits stays a decision
rather than a rename — it would move `STEP_FILE_RE`, `PLAN_ENTRY_RE`, `pauser_id`,
`inv_4_done_not_blocked` and `next_step_id` together — and the refusal names where the
ceiling came from so a prose token can be told from a real step.

2026-08-09 (S095): a step field folds its indented continuation lines into its value.
`parse_step_file` matched `^([a-z_]+):\s*(.*)$` once per line, and a continuation line
matches nothing, so every field was silently truncated to its first line. Found live during
S059: the Stop stamp gate reported the README and MANUAL check missing from a stamp that
recorded it two lines down, and the gate was right about what it could see. `goal:`,
`accepts:`, `touches:` and `excludes:` span lines throughout the plan directories, so every
reader of those had been seeing the opening line alone. A flush-left `word:` starts a new
field and a blank line ends the current one; only an indented non-empty line continues it.
`with_field` drops the lines a replaced value spanned, because leaving them would fold the
old text straight back in — the same silent defect in a new place. The single-line stamp
convention every `plan_done/` file follows is unchanged; this is about what happens when a
field does span lines, which until now was quiet data loss.

2026-08-09 (S094): `--step status` carries everything below `- Parked:` to the end of
the file through a regeneration, verbatim and whatever its indentation. The collector kept
only lines beginning with two spaces or a tab and stopped at the first that did not, so a
Parked list written flush left — ordinary markdown, and what the shipped template's bare
`- Parked:` invited — was deleted by a command that runs at every step transition and
reports success (finding 2026-08-08_adversarial.4-F07). Reading to the end of the file is
safe because Parked is the last block `step_status` writes, so nothing derived follows it,
and keeping lines verbatim means the shape written is the shape read back. The template now
carries a Parked entry, so the block is visible rather than inferred.

2026-08-09 (S093): INV-8's high-water-mark violation prints the git blob spec, not the
root-relative path. S081 threaded the top-level prefix through every reader of
`decisions.md` and missed this one message, so below the git top level the remedy for the
hardest INV-8 violation answered `fatal: path 'packages/foo/adocs/decisions.md' exists,
but not 'adocs/decisions.md'` (finding 2026-08-08_adversarial.4-F06). INV-12 calls a
remedy actionable, and this one could not run. The deletion message in the same check was
already correct, which is what made the gap easy to miss.

2026-08-09 (S092): `git_prefix` is computed once per root and cached. It shells out
to `git rev-parse --show-prefix`, and `from_git_path` and `to_git_path` call it once per
path, so INV-7 and INV-8 walking every completed step and every history line spawned 257
processes for one `run_checks` over this repository — on every prompt, through the Stop
and post-write hooks (finding 2026-08-08_adversarial.4-F05). Measured here: `--validate`
9.54s to 0.72s, `--stop` 9.79s to 0.78s. The answer cannot change while a run is in
flight, and the key is the root, so a process checking two roots still asks once for
each. What S081 added the prefix for is unchanged.

2026-08-09 (S091): `--scaffold` and `--decline` guard their own writes and refuse
with exit 1 instead of raising. Both are dispatched before `main`'s backstop and have
to be — that backstop runs after the marker gate they exist to create — so an
unwritable directory reached the user as a Python traceback, which MANUAL has claimed
no mode produces since 0.6.0 (finding 2026-08-08_adversarial.4-F04). `--scaffold` also
rolls back: the marker is the first entry in `SCAFFOLD_MAP`, so a failure partway
through left an enabled `.moltke.json` over a tree that was never built, with every
hook live against nothing. Only files the failing run created are removed — scaffolding
never overwrites, so nothing of the user's is at stake — and what could not be removed
is named in the refusal.

2026-08-09 (S090, DEC-040): INV-1 reports a `paused_by` naming a step that is in no
plan directory, and `--step unpause <id>` is the command that clears it. A pause is
what takes a step out of the active count, so nothing checking that the pauser
exists meant a step could be parked behind work that was never created: every check
passed, `--roadmap` drew it as paused by a phantom, `--step done` on the parent
refused and sent you to a step no operation could reach, and hand-editing was the
only way out — the prime directive says state is derivable from tracked files, and
here the files said something untrue (finding 2026-08-08_adversarial.4-F03). INV-3
already reports the same shape for an id `plan.md` lists with no file. `unpause` is
deliberately narrow: it refuses a pause naming a step that exists, because a
general unpause would let a step walk out of the accounting INV-1 keeps. S070's
stale-pause path in `--step done`, where the pauser is already in `plan_done/`,
keeps its behaviour and is unchanged.

2026-08-09 (S089): `--step done` and `--step start` refuse when the destination is
already carried by a file with that id, before anything is written and before the
suite gate spends its wall clock. The completion write is a plain `write_text`
into `plan_done/`, so with the same id in `plan_current/` and `plan_done/` — INV-6,
which `--validate` reports rather than prevents — the finished step was overwritten
by the one still in progress, and its `done:` stamp went with it: history destroyed
by the command whose own success message calls that directory immutable (finding
2026-08-08_adversarial.4-F02). `--step start`'s `path.rename` has the same shape,
silently on POSIX; `locate_step` searches `plan_todo/` first, so a duplicate id is
read from there and renamed onto the copy already current. Both refusals name the
duplicate and INV-6 and stop: ids are never reused (DEC-008), so one of the two
files is misnumbered, and deciding which is not something the command can do.

2026-08-09 (S088): `--step new` and `--step block` refuse a short name that is not
`[A-Za-z0-9_]+`, before either touches the filesystem. The name went unchecked
into `f"{step_id}_{name}.md"` while `STEP_FILE_RE` requires that character set, so
`--step new fix-parser` filed `S004_fix-parser.md` and listed `S004` in `plan.md`:
a step every scanner keyed on the pattern skips, with `--validate` green over a
plan that names an id no visible file carries — the listed-but-absent half of
INV-3, produced by the tool whose job is to keep those two in step. A separator
escaped the plan directory outright, `S004_../../../escaped.md` (finding
2026-08-08_adversarial.4-F01). The check sits in `mode_step` rather than in either
function because both write the plan entry before the step file (S088 keeps S083's
order), so refusing halfway would leave `plan.md` naming a step that does not
exist. `--audit new` has refused its type this way since S040 and is the model
copied. The name is indexed inside the existing try, so a missing argument still
prints usage rather than raising.

2026-08-08 (S086, S087): `--roadmap` handles its own read failure and exits 0,
which is what specs and both exit tables already said and what a mode AGENTS.md
tells every agent to run at the end of a unit of work has to do; it was
dispatched inside `main`'s try and returned the backstop's 2, the same defect
`.2-F10` reported for `--audit` (finding 2026-08-08_adversarial.3-F07).

Nested hook payload fields are read through `payload_str`, which returns "" for
anything that is not a string. Only the top level was checked and every consumer
assumed the rest, so a `tool_input` that is a string, or an `agent_type` that is
a list, killed `--pre-write` — and a `PreToolUse` hook that dies exits 1, which
is non-blocking, so the write it was judging proceeded: the reviewer fence and
the `plan_done/` refusal failing open, the direction S016 named as wrong. A
prompt of the wrong type is coerced rather than dropped, because logging must
never lose what the user typed. Whether Claude Code sends these shapes is not
established, and the fence does not depend on it (finding
2026-08-08_adversarial.3-F08).

2026-08-08 (S085): `adocs/testing.md` is read through `read_stripped` by INV-5
and by `--step done`, and joins `stripped_files` and therefore INV-13's scan. It
was the last scanner input read raw, so a row inside a code fence — guidance by
the rule this file states as universal — counted as evidence and completed a step
(finding 2026-08-08_adversarial.3-F06). Adding the reader without adding the file
to the guarded set failed S072's functional guard, which is that guard doing its
job three steps after it was built.

2026-08-08 (S084): INV-7 names `git mv` for a rename inside `plan_done/`, which
undoes it, rather than `git checkout` on the new path, which restores it from an
index that already holds the rename and therefore changes nothing. S071 made this
message safe to paste and left it a no-op, and following it together with the
deletion message wrote the old name back beside the new one — an INV-6 duplicate
id, a repository further from green than before (finding
2026-08-08_adversarial.3-F05). A rename now reports once, as a rename, and the
printed command is run by a test that asserts the tree ends green.

2026-08-08 (S083): `--step new` and `--step block` write the plan entry first
and the step file second, so a failure leaves nothing behind. Written the other
way round, a failing append to `plan.md` left a step file no list entry names,
which is INV-3, and for `block` an unpaused parent as well — the half-apply class
S062 and S070 fixed for `--step done` and left in its two siblings (finding
2026-08-08_adversarial.3-F04). The order is chosen rather than arbitrary: of the
two failure directions, a listed id with no file is the recoverable one, since
INV-3 names it and `--step new` writes the file, while a file no plan lists is a
violation with no command to clear it.

2026-08-08 (S082): `--step block` refuses when the parent is already paused. It
asked only that the parent was in `plan_current/` and then overwrote its
`paused_by`, so a second blocking child reported success while taking the
repository from all checks pass to an INV-1 violation: the first child's pause
vanished from the file, the parent unpaused itself, and both children counted as
active (finding 2026-08-08_adversarial.3-F03). A step is blocked by one child at
a time; blocking that child instead is how work discovered inside blocking work
is recorded, and the refusal says so.

2026-08-08 (S081): the marked root and the git top level are allowed to differ,
and every git-derived check translates between them through one `git_prefix`.
Every git call is `git -C <marked root>`, but porcelain, log and show all speak
in paths relative to the top level, and nothing checked the two agreed. A project
vendored into a monorepo — or any project directory under an ancestor that
happens to be a git repository — therefore had INV-7 calling a present file gone
with a remedy that could not run, INV-8 abstaining on real tampering because
`HEAD:adocs/decisions.md` does not resolve from the top level, `--audit check`
listing its own report as unexpected, and both `Stop` gates reading every path
wrongly (finding 2026-08-08_adversarial.3-F02). `from_git_path` returns `None`
for a sibling package's file, which is git's business and not ours;
`to_git_path` builds the blob spec `show` and `cat-file` need. The one place the
prefix stays visible is the `git show <sha>:<path>` half of a printed remedy,
because that path resolves from the top level whatever the working directory —
the file named and the redirection target are the marked root's, and a test runs
the printed command to prove the pairing restores the file.

2026-08-08 (S080, DEC-039): `mode_stop` prints before it persists, and nothing
in it raises. The retry state write was the one unguarded write left after S067
guarded every read, so an unwritable `.git` escaped to `main`'s backstop — which
returns before the problems are printed and before the cap is consulted. Eight
consecutive stops read `2 2 2 2 2 2 2 2` against `2 2 2 0 0` for a writable
`.git`, and the message called a write a read and named `--validate`, which
reports all checks pass on that tree (finding 2026-08-08_adversarial.3-F01). It
was the third wedge found in this function and the second introduced while fixing
the first, which is why DEC-039 states a rule for it rather than moving the guard
again. The missing cap is the accepted half: DEC-031 weighed the same trade for a
repository with no git, so the property is scoped to wherever the state can be
written, and the message says so.

2026-08-08 (S078): INV-16 compares the prime-directive section against its
stripped form, which is what this file already claimed it did. It returned clean
as soon as `prime_directive` was non-empty, so a section holding a lead-in
sentence and the rule itself inside a fence passed: the directive unreadable,
nothing reporting it, and `prime_directive` answering with the lead-in (finding
2026-08-08_adversarial.2-F12). `hides_content` holds the comparison INV-14 and
INV-16 both make, which also keeps it inside the short list of lines allowed to
call `strip_guidance` — the S072 guard caught the first attempt, which is the
guard working.

2026-08-08 (S077): `--audit check` and the `Stop` gates share one definition of
"newly here". `_is_new_file` kept the pre-S050 predicate while `_arrives_here`
learned that the index half decides, so `AM` — a red-first regression test staged
and then refined, which is how one is actually written — was reported as
contamination the reviewer had to justify, when a new file under `tests/` is
exactly what the fence permits (finding 2026-08-08_adversarial.2-F11). An edit to
a test that already existed is still unexpected: the fence allows new files, not
patches to old ones.

2026-08-08 (S076): `--audit` refuses with exit 1 on stderr like `--step` does,
instead of returning the `main` backstop's exit 2 — which `README.md`'s table
assigns to the three hook modes only — and its message says whether the failure
was a read or a write. A failed `--audit new` was reported as "could not read the
repository" with `--validate` named as the remedy, which had nothing to do with
it, and the exit table stopped being traceable to the code that produces it,
which §7 requires of every doc claim (finding 2026-08-08_adversarial.2-F10).

2026-08-08 (S075): INV-14 strips comments before comparing, so what it reports
is always something a fence can hide. `strip_guidance` removes HTML comments as
well as fences, so a draft finding commented out — which the shipped template
invites, its own append marker being a comment — was reported as swallowed by a
code fence in a report with no fence markers at all, with a remedy that could not
be applied, repeated to `--stop` and `--post-write` as a blocking problem
(finding 2026-08-08_adversarial.2-F09).

2026-08-08 (S071): INV-7's working-tree half reads porcelain through
`porcelain_paths`, like both `Stop` gates and `worktree_state` already did. It
sliced the line instead, so a rename inside `plan_done/` produced a violation
naming both halves and a remedy that a shell reads as a redirection —
`git checkout -- old > new` truncates the renamed file, which is the only
remaining content of that step. The one invariant whose subject is immutable
history printed a command that destroys a file in it, and repeated it to
`--stop` as the actionable instruction INV-12 requires (finding
2026-08-08_adversarial.2-F05). The violation now names the file that exists and
says what it was renamed from.

2026-08-08 (S070): `--step done` pre-flights every file it is about to write —
the step file and any paused parent — and refuses before touching anything if
one is not writable. S062 moved the write and the unlink ahead of the point of
no return and left the parent unpause after it; that unpause is a different
file and can fail on its own, and when it did the child was already in
`plan_done/`, leaving a parent paused by a completed step that neither
`--step done` nor `--step start` could clear (finding
2026-08-08_adversarial.2-F04). A pause naming a step already in `plan_done/` is
now treated as stale and reported rather than refused, so that state is
recoverable however it is reached — including by the `Bash` writes no fence
sees. If the unpause still fails after the pre-flight, which is a race rather
than a mistake, the message says which command clears it.

2026-08-08 (S069): the `Stop` stamp gate judges step files, matching
`STEP_FILE_RE` like `plan_steps` does. It tested the porcelain status and the
path prefix alone, so anything arriving under `plan_done/` was asked for a
completion stamp — including `--scaffold`'s own `.gitkeep`. In a project with
history adopting moltke, which is what `--scaffold` is for, that meant every
`Stop` blocked from the moment it was scaffolded, staging did not clear it, and
`--validate` said all checks pass throughout (finding
2026-08-08_adversarial.2-F03). This was the only reader of `plan_done/` without
that filter, which is why INV-5 and INV-6 had nothing to say about the same file.

2026-08-08 (S068): `--session-start` prints its JSON envelope on every path,
with a read failure carried inside `additionalContext` rather than on stderr.
The whole payload was built before the single print, so one unreadable path lost
all of it and the hook exited 0 with empty stdout — the one combination that
cannot be seen, because a zero-exit hook's stderr reaches nobody, which is why
S014 put the prompt-failure breadcrumb on this channel at all. A session with
that problem was exactly the session that would not hear about it (finding
2026-08-08_adversarial.2-F02). `session_context_lines` builds the payload and
`mode_session_start` owns the envelope, so the mode's output contract is kept by
the mode rather than by a backstop that cannot know what it is.

2026-08-08 (S067): `--stop` reports and counts on every path. S060 removed the
traceback and put `main`'s backstop behind it, which returns before the retry
counter `mode_stop` writes at the end — so an `OSError` from `status_disagreements`,
the porcelain gates, or `stop_turn_key` dropped every problem already collected
and blocked forever, the one thing INV-12 and DEC-006 say `--stop` may never do.
Five stops on a broken symlink named like a step file read `2 2 2 2 2` where the
cap should waive at four (finding 2026-08-08_adversarial.2-F01). Each section now
catches its own failure and turns it into a problem, which is what this function
already knows how to report, so the cap and the waiver run in every case.

Every git call goes through one `_git_run`, which returns `None` when there is no
git to run. `_git_lines` was made tolerant of a missing binary and the three
direct `subprocess.run` sites were not, so with git off `PATH` the documented
"no git, the check abstains" became INV-7 and INV-8 reporting that they could not
read the repository — the recurring shape again, a rule applied in one place and
not its twins.

2026-08-08 (S064): every repository file moltke reads goes through `read_file`,
which decodes UTF-8 and replaces what it cannot. Thirteen readers decoded
strictly and six replaced, and INV-14's two halves disagreed about the same file
— S049 added `hidden_findings` beside `report_findings` and gave only the new one
the tolerant read. One latin-1 byte in a pasted terminal capture then turned
`--validate`, `--post-write`, `--stop`, `--session-start`, `--step`, and
`--audit list` into tracebacks, and `--session-start` producing no JSON also
silences the channel S014 depends on (finding 2026-08-08_adversarial-F05).
Replacing rather than raising is the deliberate half: moltke reads files it did
not write and must keep reporting on them, and a mojibake character in a step
file is cosmetic where a checker that cannot start is not.

2026-08-08 (S063): INV-13 scans `stripped_files`, one list derived from the
readers instead of written beside them, so `adocs/specs.md` — which S028 made a
`strip_guidance` consumer through `prime_directive` — is guarded like the rest.
Every whole-file read goes through `read_stripped`, which is what keeps the list
and the scanners from disagreeing again. — Amended 2026-08-08 (S072): the guard
described here looked for `strip_guidance` beside `read_text`, and S064 then
banned `read_text` everywhere, so the mandated way to write a new scanner —
`strip_guidance(read_file(path))` — passed it. The guard was vacuous by
construction, which is the shape it existed to catch, applied to itself. It now
names the three lines allowed to call `strip_guidance` at all, and a second test
runs the modes with `read_stripped` recorded and asserts every file it was
pointed at is one INV-13 guards (finding 2026-08-08_adversarial.2-F06).

INV-16 covers the half parity cannot reach. Two example fences with their closers
removed are an even count, and one closed fence around the directive is the same
bytes — the ambiguity DEC-033 recorded — so this compares what the file states
against what survives stripping, exactly as INV-14 does for a finding heading.
The planning nudge stays quiet in that case on purpose: asking for a directive
that is already on disk sends the user to rewrite it rather than to close the
fence around it (finding 2026-08-08_adversarial-F04).

2026-08-08 (S062): `--step done` writes nothing until the move is certain. It
stamped the step file, unpaused the parent, and renamed last — and the rename is
the only one of the three that can fail, so the refusal S052 added arrived after
two mutations were on disk: a transition that refused and repaired half of
itself, taking a repository from `all checks pass` to an INV-1 violation while
reporting that it had declined (finding 2026-08-08_adversarial-F03). The stamped
content now goes straight to `plan_done/`, so the first action is the one that
can fail; the source is unlinked only once the destination exists, and a failure
there undoes the copy; the parent is unpaused after both. `set_field` split into
a pure `with_field` and a write, which is what makes that ordering possible.
`adocs/specs.md`'s own line — no transition may leave INV-1..INV-7 violated —
is the contract this restores.

2026-08-08 (S061): the `Stop` turn key folds in the prompt-log failure
breadcrumb, so it keeps moving on the one path where the worklog cannot. S047
made the key the worklog's prompt-heading count because `UserPromptSubmit`
advances it once per turn — true only while the append succeeds, and
`--log-prompt` swallows an `OSError` by contract, since blocking there erases the
prompt. A worklog that cannot be written therefore froze the clock, every turn
read as a retry of the same one, and from the fourth the waiver switched
enforcement off and left it off: the `.2-F01` failure, reached by a different
route (finding 2026-08-08_adversarial-F02). The breadcrumb S014 already writes
for that exact failure carries `since` and `count`, both of which advance on a
failing turn, so it is what the key uses. What this still cannot distinguish is a
turn in which no prompt was logged at all and nothing failed — there is no event
to count — and that case is a retry as far as the cap is concerned, which is what
it was before.

2026-08-08 (S060): no mode ends in a traceback. Every invariant runs through one
`run_checks`, which turns an `OSError` into a violation naming the check, and
`main` carries a backstop for everything else a broken tree reaches — status
regeneration, the plan reader, the porcelain gates — reporting and exiting 2,
or 0 for `--log-prompt` and `--session-start`, which must never block. Three call
sites ran the invariant loop and none handled a read failure, so a directory
where a step file belongs killed `--validate`, `--post-write`, and `--stop`
alike. From a `Stop` hook that is the worst case there is: exit 1 is
non-blocking, so the turn ends with every gate off and nothing printed, losing
the problems already collected in the same call (finding
2026-08-08_adversarial-F01).

The stamp gate skips an entry that is not a file on disk. `AD` and `RD` say the
index has the path and the worktree does not, and `RD` is what following the
gate's own instruction produces: it blocks, `--pre-write` refuses to edit the
file it names, so `mv` back is the only compliant way out. Nothing arrived, so
there is nothing to stamp; the tree is still reported, by INV-7. `--stop` reads
porcelain with `-uall`, as `worktree_state` has since S036 and for the same
reason — plain porcelain collapses a wholly untracked directory into one entry,
so `?? adocs/plan_done/` reached the gate as a path that is a directory. That
also makes the gate see individual arrivals before the first commit, where every
file is new, so it abstains there exactly as the recap gate already did.

2026-08-08 (S031, DEC-032): the secret shapes moved from
`tests/test_s022_secrets.py` into `bin/moltke.py` and run as INV-15, so
`--validate` reports them and `--stop` refuses on them in every marked
repository. They protected moltke's own worklog before and nothing else: a
repository that installs the plugin runs moltke's hooks, not moltke's suite, so
it inherited verbatim prompt logging into a tracked file with no check at all.
The suite test imports the shipped shapes rather than keeping a copy, so the
detector has one definition and its non-vacuity guard — every pattern asserted
against its own example before anything is scanned — covers the version that
ships. Scope is unchanged from DEC-024: `worklog.md` only, prefixed shapes and
PEM headers only, no entropy or bare-hex rule, because every recap carries a
commit sha. A hit names the shape, the line, and the first 8 characters, never
the value. Not a cheap check: it reads the unbounded worklog, so `--post-write`
skips it exactly as it skips INV-13.

2026-08-08 (S029): `--scaffold`'s `kept` lines report, file by file, whether
`AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/moltke.mdc` still match the
installed plugin's templates, and a closing line names every file that drifted.
Reported, never acted on: the ruleset may carry house rules, and an automatic
refresh would erase them. Nothing under `adocs/` and not `.moltke.json` is
compared — both become the project's own content the moment it is used, so
comparing them would report drift on every repository that works. This is what a
fresh clone cannot already know: repository state travels in git, and only the
plugin install is per-machine. The `init` skill's already-enabled branch becomes
that verification path — `--validate`, then `--session-start` to read back the
stack and the derived next step, then `--scaffold` for the drift report — and a
refresh of a drifted file is offered as a question, applied only on an explicit
yes. No new CLI operation, so no surface change: the drift belongs where the
kept-file decision is already made.

2026-08-08 (S028): `--session-start` reports the planning phase as pending while
`adocs/specs.md` has no prime directive or `adocs/plan.md` lists no steps, naming
only the file that is unfilled. `--scaffold` writes both with their content as a
comment, because they are the two things the workflow cannot write for the user,
and nothing said so: every check reported green on a repository that had adopted
the workflow and never used it. The prime directive is read through
`strip_guidance`, so the template's own comment and a fenced example are guidance
rather than an answer. It is a nudge in `additionalContext` on an exit 0 and
never a refusal — blocking a turn on a file only a human can fill is the deadlock
DEC-006 and INV-12 exist to prevent — and it disappears when both are filled. The
`init` skill's post-scaffold sequence is the other half: it elicits the directive
and the invariants, discusses the order before writing it, creates every step
with `--step new` rather than by copying the template, records the session's
choices as `DEC` entries, regenerates `status.md`, and ends in a commit.

2026-08-08 (S056): `--audit check` reads the worklog append rather than only
testing its shape. `--log-prompt` writes a `## <stamp> prompt` heading and the
prompt quoted line by line, so an appended region containing anything else — a
recap heading, unquoted prose — is unexpected and exits 1, while a genuine hook
append stays expected and is named in the listing instead of passing unmentioned.
S036 exempted the file by shape because a gate that is wrong on every audit
spanning a prompt is one people wave through; the blind spot it left was in the
one file where an append changes another gate's answer, since a recap heading
discharges the `Stop` recap gate for the surrounding turn, and `Bash` reaches it
even though the write fence does not (finding 2026-08-07_adversarial.2-F09).
Quoting is what makes the corroboration safe: a prompt that itself contains a
recap heading or a fence arrives with every line prefixed `> `. What is unchanged
is that `Stop` cannot tell who appended a recap and still accepts one in the
moment: the fabricated heading silences that gate for the turn, and `--audit
check` is where it surfaces. That is DEC-022's prevention-to-detection trade
applied to this file rather than an exception to it.

2026-08-08 (S055): INV-13 and `strip_guidance` share one `fence_markers`, which
removes HTML comments and then finds the line-anchored markers. The invariant
counted markers in the raw file while the stripper removed comments first, so a
marker inside a comment was counted by the check and not by the thing the check
exists to protect: `--stop` blocked under a message that was false for that file,
and closing the fence as instructed would have unbalanced a pairing that was
already correct. It failed the other way too — a commented marker plus a genuinely
unclosed one is an even raw count, so a real imbalance went unreported (finding
2026-08-07_adversarial.2-F08). Both directions are gone because there is one
definition of what a marker is rather than two.

2026-08-08 (S052): `--step` refuses, naming `--scaffold`, in a marked repository
whose `adocs/` does not exist, instead of raising `FileNotFoundError` out of
`step_status`, `step_start`, and `step_done`. `mode_step` caught `IndexError`
alone, so a missing directory surfaced as a traceback and exit 1 — neither of the
two things `README.md` says exit 1 means. The directory is not created
implicitly: a repository that was never scaffolded says so rather than being
half-built by a status write, which is also why `--scaffold` is the remedy named.
An `OSError` from any operation becomes a refusal too, for the partially
scaffolded tree where `adocs/` exists and a plan directory inside it does not.
The steering was the other half: with no `adocs/` all four derived fields
disagree, so `--session-start` and `--stop` both told the agent to run
`--step status`, the one command that could not work there (finding
2026-08-07_adversarial.2-F05). Both now name `--scaffold` first when the
directory is missing, through one `_stale_remedy`, and are unchanged otherwise.

2026-08-08 (S050): both `--stop` gates read `git status --porcelain` through one
`porcelain_paths`, which splits a rename line on ` -> ` — the same rule
`worktree_state` already used. A staged rename is one line, `R  old -> new`:
`line[3:]` gave the old path, and `R ` was in neither `("??", "A ")`, so the
README/MANUAL stamp gate saw nothing when a completed step reached `plan_done/`
by `git mv`, the move AGENTS.md section 4 names, or by `mv` followed by the
`git add -A` every commit passes through. Arrival is now judged on the index half
of the code — `A`, `R`, or `C`, plus untracked — so `AM` and `RM` count too. The
recap gate judges a rename by both sides rather than the destination alone,
because a file promoted out of `adocs/` adds a source file and one moved into
`adocs/` removes one; a rename that stays inside `adocs/` is exempt as before
(finding 2026-08-07_adversarial.2-F03). The stamp gate had no test at all until
this step: it was the only survivor of the seventeen mutations that finding ran.

2026-08-08 (S049, DEC-033): INV-14 compares the finding headings an audit report
states in its raw text against the ones that survive `strip_guidance`. S033 fixed
the pairing and reported an odd marker count as INV-13; two unclosed fences are an
even count, pair as one closed fence, and delete the finding between them, which
is what a reviewer produces by pasting two transcripts and closing neither. The
J2 case of 2026-08-07_adversarial-F02 still gave `--validate` exit 0 with the open
finding absent from `--audit list` entirely (re-measured as .2-F04). Comparing
headings needs no ruling on what the markers meant: either way the report names a
finding nothing can read. `--audit list` prints it as `hidden` rather than
omitting it, and INV-14 is a cheap check, so `--post-write` reports it when the
report is saved — INV-13 stays out of `--post-write` because it reads the
unbounded worklog.

Scoped to the report's own stem, which is the whole of what makes it decidable: a
foreign id is quotable evidence, and every re-run's verdict section is nothing but
quoted headings. For the same reason `--audit new` no longer substitutes the real
stem into the template's fenced example, which now reads `<report>-F01`; guidance
written under this report's own name is byte-identical to a swallowed finding.

What INV-14 cannot see, stated rather than implied: hidden content that is not a
finding heading — a `Status:` line, a whole Impact section, the text discharging a
finding; a hidden heading carrying another report's stem; and hidden content in
`plan.md`, `decisions.md`, `worklog.md`, or anywhere outside `adocs/audit/`, where
INV-13's parity is still the only guard. The ambiguity S033 recorded is unchanged
underneath: this detects the one consequence that matters instead of resolving it.

2026-08-07 (S048): INV-3 and `plan_order` now share one definition of "listed in
`plan.md`" — a list entry. S045 narrowed `plan_order` and left INV-3 matching any
mention, so the two disagreed and a step file named only in the description
satisfied the invariant while being invisible to `derived_next`: `--validate` said
all checks pass, `status.md` said there were no steps left, and `--session-start`
printed no derived-next line at all (finding 2026-08-07_adversarial.2-F02). That
is the prime directive failing, so it is worth naming: a fix for one
prime-directive defect introduced another. Prose ids are now neither listed nor
phantoms, in either direction, which is what makes the two agree. INV-3's reverse
message also drops the claim that a phantom "is the derived next step", which
S045 had made false.

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
and this reads it whole. — Amended 2026-08-08 (S049, DEC-033): "that case is
reported" was true of an odd marker count only, and two unclosed fences are an
even one, so in an audit report the case was neither reported nor guessed but
silently lost. INV-14 covers it there by comparing headings rather than counting
markers, and does run in `--post-write`. The ambiguity itself is unchanged, and
outside `adocs/audit/` INV-13's parity is still the only guard.

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
| `--roadmap` | — | 2026-08-08 (S079, DEC-038): print where the plan is as one timeline strip, derived from `plan.md` order and the three plan directories. Never reads `status.md`, so it cannot report what the repository does not say. Exit 0 always |
| `--scaffold` | `init` skill | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `adocs/` from templates; never overwrites an existing file |
| `--decline` | `init` skill | write `{"schema": 1, "enabled": false}`, durably; refuses to disable an already-enabled repository |
| `--audit OP ...` | `audit` skill | 2026-08-01 (S008): `new <type>` opens `adocs/audit/YYYY-MM-DD_<type>.md` from the template and never overwrites, taking a `.2`, `.3` sequence suffix on a same-day re-run (S020); `list` prints every finding with its status and what references it, exiting non-zero while an open finding has neither a step nor a decision. 2026-08-06 (S017): `new` also records a working-tree baseline in `.git/moltke_audit_baseline.json`, and `check` reconciles the run against it, printing expected and unexpected changes and exiting 1 on anything unexpected |
| `--step OP ...` | `step` skill | 2026-08-01 (S007): lifecycle operations `new <name> [--goal]`, `start <id>`, `block <parent> <name>`, `done <id> --stamp`, `status`. Each refuses rather than repairs, naming the missing condition; no transition may leave INV-1..INV-7 violated. 2026-08-06 (S021): `done` additionally runs the optional `test_command` suite gate and refuses on a non-zero exit. 2026-08-09 (S090, DEC-040): `unpause <id>` clears a `paused_by` naming a step that is in no plan directory, and refuses one that names a step that exists |

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

None open. Both items that stood here are settled, 2026-08-07:

- DEC-002, confirm the public repository before the first push: resolved. `master`
  is pushed to `origin` and `https://github.com/macsimbodnar/moltke` loads
  unauthenticated, verified during S026. DEC-002 stands as the record.
- Whether `status.md` earns its place: it does, and it stays (Max, 2026-08-07). It
  is the one file a human opens to see where things are without running anything,
  and it holds the Parked list, which nothing else does. The cost is accepted: it
  is a second copy of derivable facts, kept honest by regeneration at every step
  transition and by the staleness check S039 widened to all four derived fields.
  Dropping it was considered and rejected — `--session-start` prints the same
  facts, but only to an agent, and the Parked list would need a new home.
