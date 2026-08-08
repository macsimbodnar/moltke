# moltke manual

Install, operate, known issues. For working on moltke itself, see
[README.md](README.md).

## What it does

moltke keeps a project's memory in tracked files and refuses to let it drift:

- `adocs/status.md` where we are, regenerated from the filesystem
- `adocs/specs.md` the prime directive and the numbered invariants
- `adocs/plan.md` plus `plan_todo/`, `plan_current/`, `plan_done/`
- `adocs/decisions.md` why things are the way they are, with rejected options
- `adocs/testing.md` acceptance criteria and their covering tests
- `adocs/audit/` findings, as evidence, before any fix

Enforcement is blocking, and only in repositories that opt in. A repository
without `.moltke.json` feels nothing at all.

## Install

Once per machine. From the hosted repository:

```
claude plugin marketplace add https://github.com/macsimbodnar/moltke
claude plugin install moltke@moltke
```

Or from a local checkout, which is what you want while developing moltke itself:

```
claude plugin marketplace add /path/to/moltke
claude plugin install moltke@moltke
```

Either form also works from inside Claude Code, with `/plugin marketplace add`
and `/plugin install`, followed by `/reload-plugins` to activate it in the
current session.

`moltke@moltke` is `plugin@marketplace`: this repository is a single-plugin
marketplace, and both are named moltke.

Updates arrive only when `version` in `.claude-plugin/plugin.json` is bumped.
That is deliberate: plugin hooks run shell commands on every machine where the
plugin is installed, so an update should be a decision, not a side effect of a
push.

## Set up a repository

In the repository you want to use it in:

```
/moltke:init
```

It asks once. Yes scaffolds `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/moltke.mdc`,
`.moltke.json`, and a populated `adocs/`. No records the refusal durably and
never asks again. Nothing existing is ever overwritten: a repository that
already has an `AGENTS.md` keeps it, and moltke reports what it left alone.

On a machine where the repository already uses moltke — a fresh clone, a
colleague joining — `/moltke:init` verifies instead of scaffolding: `--validate`,
then the session context to show where the project actually is, then `--scaffold`
for its drift report. Repository state travels in git; only the plugin install is
per-machine, so the one thing worth checking is whether `AGENTS.md`, `CLAUDE.md`,
and `.cursor/rules/moltke.mdc` still match the templates of the plugin you have
installed. Drift is reported file by file and never fixed for you: those files
may carry house rules on purpose. A refresh happens only if you say yes to one,
and never touches `adocs/` or `.moltke.json`.

The same turn continues into a planning phase: the prime directive and the
invariants into `adocs/specs.md`, an ordered first plan into `adocs/plan.md` with
one `--step new` per step, the session's choices into `adocs/decisions.md`, and a
commit. Those two files are what moltke cannot write for you, and until they are
filled every session says the planning phase is pending, naming the file that is
still empty. It is a note in the session context, never a refusal: a gate on a
file only you can write would be a deadlock.

`.moltke.json` controls everything:

```json
{
  "schema": 1,
  "enabled": true,
  "plan_active_max": 1,
  "plan_stack_max": 3,
  "surface_guard": "cli",
  "test_command": "python3 -m unittest discover -s tests"
}
```

`enabled: false` disables every check, permanently, until the file is deleted.
`plan_active_max` is how many steps may be in progress at once, `plan_stack_max`
how deep the paused stack may go. `surface_guard` is `cli`, `api`, `both`, or
`none`, and `none` is only valid alongside a decision entry saying why the
project has no checkable surface.

`test_command` is optional and is the only key that makes the "green suite at
completion" rule real: `--step done` runs it from the repository root with a
shell, under a 600 second timeout, and refuses on a non-zero exit with the last
20 lines of output. Leave it out and nothing runs your suite — `--step done` says
so each time rather than letting the silence read as a pass. It must be a
non-empty string if present; a blank one, or a list, or a number, is a marker
violation, because a gate that silently checks nothing is worse than no gate. Any
marker violation now refuses every `--step` operation outright, so a typo in this
key stops the plan moving rather than quietly ungating it. The command runs with
your shell and your privileges, so treat the marker as executable content: do not
set it to something you would not run by hand.

## Daily use

Nothing to remember. Hooks fire on their own:

- session start prints the current stack and the next step, and names any field
  where `status.md` disagrees with the filesystem — Last done, In progress, Next,
  or Blocked. The `Updated:` line and the Parked block are yours; nothing
  compares them
- every prompt is appended verbatim to `adocs/worklog.md`, which is history you
  may correct or trim: only `adocs/decisions.md` is enforced append-only
- writes into completed history are refused
- the turn will not end with a stale `status.md`, an invariant violation, or
  source changes with no worklog recap

Drive the plan with `/moltke:step`, audit with `/moltke:audit`. Both refuse
rather than repair, and name the condition that is missing.

## Reference: every mode

Skills call `bin/moltke.py`. You can run it by hand, and other tools (Codex,
Cursor) must, since hooks exist only in Claude Code.

| Command | What it does |
|---|---|
| `--validate` | run every invariant, print all violations, exit 1 if any |
| `--scaffold` | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `adocs/` from templates; never overwrites an existing file, and reports for each kept ruleset file whether it still matches the installed template |
| `--decline` | record that this repository declines the workflow, durably; refuses to disable an already-enabled repository |
| `--step new <name>` | allocate the next step id, write the step file, list it in `plan.md` |
| `--step start <id>` | move a step from `plan_todo/` to `plan_current/` |
| `--step block <parent> <name>` | create a blocking child in `plan_current/` and pause its parent |
| `--step done <id>` | complete a step and move it to `plan_done/`, refusing if anything is missing. Runs the `test_command` suite gate when the marker sets one, and refuses on a non-zero exit |
| `--step status` | regenerate `status.md` from the filesystem, keeping the Parked list |
| `--audit new <type>` | open `adocs/audit/YYYY-MM-DD_<type>.md`; never overwrites a report — a same-day re-run becomes `YYYY-MM-DD_<type>.2.md`, and its findings are numbered from that name. The type must match `[A-Za-z0-9_-]+`, so it stays a filename and cannot collide with that `.2` suffix. Also records a working-tree baseline for `--audit check` |
| `--audit list` | every finding, its status, and what references it; exits 1 while an open finding has neither a step nor a decision, or while a report names a finding a code fence hides, which lists as `hidden` (INV-14) |
| `--audit check` | reconcile what the run changed against that baseline: the report and new files under `tests/` are expected, anything else exits 1. Run it after the reviewer returns, before acting on a finding |
| `--session-start` | SessionStart hook: emit the stack and derived next step as context |
| `--log-prompt` | UserPromptSubmit hook: append the prompt to the worklog. Never blocks, because blocking here would erase your prompt |
| `--pre-write` | PreToolUse hook for Write and Edit: refuse writes into `plan_done/`, step files outside the plan directories, and reviewer writes other than `adocs/audit/` or a new file under `tests/` |
| `--post-write` | PostToolUse hook: cheap invariant scan, surfaced but non-blocking |
| `--stop` | Stop hook: refuse to end a turn on violations, a stale `status.md`, or unrecapped source changes |

`--step new` takes `--goal TEXT`; `--step done` takes `--stamp TEXT` and
requires it. Every mode exits 0 immediately in a repository with no marker, or
one whose marker says `enabled: false` — except `--scaffold` and `--decline`,
which exist to create that marker.

Every `--step` operation refuses, naming `--scaffold`, in a marked repository
that has no `adocs/` yet, and the hooks name `--scaffold` there too rather than
`--step status`. It will not create the directory for you: a repository that was
never scaffolded should say so rather than end up half-built by a status write.

Exit codes and streams:

| Exit | Meaning | Stream |
|---|---|---|
| `0` | clean, or a hook with nothing to say | stdout, when there is output |
| `1` | findings — invariant violations, audit bookkeeping, `--audit check` | stdout |
| `1` | refusals — a command declining to proceed, and why | stderr |
| `2` | a blocked action, with what to do about it | stderr |

Exit `1` means two different things and they arrive on different streams:
`--validate`, `--audit list`, and `--audit check` print findings to stdout, while
every refusal — `--step` transitions, `--audit new` on an existing report, an
unknown operation, a failing `test_command` — goes to stderr. **If you script
this, capture both**, or you will get an exit code with no message. That matters
most outside Claude Code, where `--validate` is the only lever you have.

Two more details for anyone parsing output. `--post-write` returns `2` but is
non-blocking by contract: the tool it follows has already run, and the exit code
only surfaces the text. And stderr is not exclusively for failures — `--audit new`
outside a git worktree warns there that `--audit check` will not be able to
reconcile the run, while still exiting `0`.

## Known issues

<!-- historical -->
**Upgrading past 0.1.0 does not rename an existing `project/`.** The workflow
directory was `project/` up to 0.1.0 and is `adocs/` from 0.2.0 (DEC-021). There
is no migration mode: at the time of the rename no repository other than moltke
itself had the plugin installed. A repository scaffolded by 0.1.0 keeps its
`project/`, and 0.2.0 will not see it — every check reports the tree as missing
until the directory is renamed by hand with `git mv project adocs`.
<!-- /historical -->

**Hooks keep running the installed copy, not your checkout.** Hook commands
resolve `${CLAUDE_PLUGIN_ROOT}` to the plugin cache, pinned at the installed
`version`. Editing `bin/moltke.py` in a checkout changes nothing until the
version is bumped and the plugin reinstalled, so during an upgrade the hooks
enforce the previous release's rules against the previous release's paths.

**The plugin ships moltke's own project state.** The repository root is also
the plugin root, so `adocs/`, `tests/`, `AGENTS.md`, and `CLAUDE.md` are
copied into every install's cache. They are inert. `claude plugin validate
--strict` warns that the root `CLAUDE.md` is not loaded as project context; the
warning is accurate and harmless. Recorded as DEC-020, with a `plugin/`
subdirectory move as the escape hatch if it ever matters.

**The README and MANUAL gate is mechanical.** `--step done` and the Stop hook
require the completion stamp to mention README and MANUAL. They cannot tell
whether you actually looked. The check enforces that the question was asked,
not that it was answered honestly. It sees the step arrive in `plan_done/`
however you moved it — `git mv`, a plain `mv`, or `mv` then `git add -A`; up to
and including 0.4.0 a staged rename walked past it, and past the recap gate for
a file moved out of `adocs/`, because both read the old path. The same used to be true of the green-suite
requirement — nothing ran a suite at all — which is what `test_command` fixes;
without that key set, completion is still trusted rather than checked.

**The reviewer's write fence covers `Write` and `Edit`, not `Bash`.** The
PreToolUse hook confines `adversarial_reviewer` to `adocs/audit/` by matching
`agent_type`. Until 0.3.0 it compared against the bare name while Claude Code
sends the scoped one, so it never matched and opened silently; the value was
observed directly on 2026-08-06 — a plugin subagent sends
`moltke:adversarial_reviewer`, the main thread sends no `agent_type` at all — and
the match now reads the part after the last colon (finding F02, fixed in step
S016).

Three limits remain by design. The reviewer also holds `Bash`, whose writes no
PreToolUse matcher sees, so mutation during an audit is possible and is treated
as legitimate (DEC-022): `--audit check` reports what a run actually changed
rather than trying to prevent it. Because the match is by suffix, another plugin
shipping an agent named `adversarial_reviewer` would be fenced too — the
deliberate direction of failure, since a wrong block says so out loud while a
wrong pass is what F02 was. And the fence permits new files under `tests/`,
because a red-first regression test is evidence; editing a test that already
exists is a patch and stays blocked.

Paths are resolved before any of that is decided, so `tests/../bin/moltke.py` is
judged as `bin/moltke.py`. Before 0.4.0 only absolute paths were resolved, and a
relative one merely had to start with an allowed directory. A path that resolves
outside the repository is not policed at all: moltke governs the repository it is
marked in, and the fence was never the guarantee.

**`--audit check` reads the working tree and the commits.** `--audit new` records
two things: a `git status --porcelain -uall` snapshot with a content hash per
changed file, and the `HEAD` sha. The check compares both, so a file the run
patched shows up whether it was left dirty or committed. Before 0.4.0 only the
snapshot was compared, and a clean tracked file that the run patched **and
committed** appeared in neither side — the check printed "no change since
`--audit new`" for a run that had rewritten source.

Consequences worth knowing. A change to a `.gitignore`d path is invisible, because
git does not report those. Pre-existing dirt in your tree, and commits made before
the run, are in the baseline and are never blamed on the audit. A commit that
touches only the report and new files under `tests/` is expected; anything else in
it is not.

`adocs/worklog.md` is expected too, but only while it has merely grown — the
baseline records its length and hash, and the check confirms the file still starts
with those bytes. Every prompt appends to it through the hook, so before 0.4.0 any
audit that spanned a prompt reported a change the tool itself had made. A worklog
that was truncated or rewritten during a run is still reported, because an append
is what the hook does and a rewrite is not.

The append itself is read, not just its shape: `--log-prompt` writes a
`## <stamp> prompt` heading and the prompt quoted line by line, so anything else
in the appended region — a recap heading, unquoted prose — is listed as
unexpected and exits 1. That matters because an appended recap heading turns off
the `Stop` recap gate for the surrounding turn, and it is reachable from `Bash`,
which the reviewer holds and no write fence sees. A genuine hook append is still
expected, and is now named in the listing rather than passing unmentioned. If the baseline `HEAD` is no longer reachable, that is reported rather
than skipped, because history was rewritten under the run. Without git, or before
`--audit new` has run, the check refuses instead of passing quietly.

**An unclosed code fence is a violation, not a formatting nit.** Every check that
reads `plan.md`, `decisions.md`, `worklog.md`, or an audit report strips fenced
blocks first, so that a template's worked example is not mistaken for a real
decision or a real finding. That means an unclosed fence hides whatever follows
it from those checks.

Markers have to open a line, so a fence pasted into a prompt — which the worklog
stores as `> ``` ` — is text, and a trailing unpaired marker is text rather than
swallowing the rest of the file. A marker inside an HTML comment is not a marker
either, since comments come out before anything looks for fences — so prose about
fences, which this file and the specs are full of, can show one. An odd number of
markers is an INV-13 violation naming the file. Close the fence and it clears.

Two unclosed fences are a different problem: they are an even count, they pair as
one closed fence, and nothing distinguishes them from one — templates do put
headings inside fences on purpose. That shape is what you produce by pasting two
transcripts and closing neither, and up to and including 0.4.0 it deleted the
finding between them silently. An audit report that states a finding under its own
name which no check can then read is now an INV-14 violation naming that finding, and
`--audit list` prints it as `hidden` instead of leaving it out. `--post-write`
reports it too, so it surfaces when you save the report. Close the evidence blocks
around the heading and it clears.

INV-14 sees hidden finding headings, in `adocs/audit/` only. It does not see other
hidden content — a `Status:` line, an Impact section, anything in `plan.md`,
`decisions.md`, or `worklog.md` — where an even count of unclosed fences still
hides text and INV-13's parity is the only guard. A heading quoting another
report's finding is evidence, not a finding of yours, so quoting stays quiet. For
the same reason a fresh report's example finding now reads `### <report>-F01`
rather than carrying the report's real name.

**Immutability checks need git, and read history as well as HEAD.** INV-7
(`plan_done/` unchanged) and INV-8 (`adocs/decisions.md` append-only) compare the
working tree against `git HEAD`, which covers changes you have not committed, and
also walk `git log`, which covers changes you have. Committing tampering
therefore does not hide it: the violation names the commit that did it. In a
repository with no history, or for a file not yet committed, there is no baseline
and the check abstains rather than guessing.

What this cannot do is unwrite history, and it does not try. Both checks compare
what the file says **now** against a version from history — for a `plan_done/`
file, the one at the commit that added it; for `decisions.md`, the most recent
version that had not already lost something. So the way back to green is the one
the message tells you: restore that content in a new commit, and the violation
clears. Leave it rewritten and it keeps reporting. Nothing is ever reverted for
you, and git history stays intact as the record.

For `decisions.md` the comparison is by line, not by byte: every line the file
has ever held must still be there, in that order. Removing a line, rewriting one
in place, moving one to the end, and reordering entries are all caught. Appending
is free — and so is **inserting between existing entries**, because an insertion
removes and reorders nothing. That is deliberate (DEC-030): these checks exist to
catch an agent accidentally clobbering history, not to make forgery impossible for
someone with a shell. The ordering of the log is a convention, and a careless
edit can break it without the tool noticing.

Three further limits. A file created and deleted inside the same commit leaves
nothing to detect. `Bash` writes reach `plan_done/` without meeting the
PreToolUse fence, so the history check is what notices afterwards. And a `plan_done/`
file is compared byte for byte, so reformatting one — even a trailing newline —
counts as tampering until it is put back.

**Prompts are recorded verbatim, so a pasted secret is written to disk.** Every
`UserPromptSubmit` appends your prompt to `adocs/worklog.md`, which is tracked and
committed. Paste an API key, a token, or a customer identifier into a prompt and
it is in the repository — and if that repository is public, it is public. This is
true of every repository moltke is installed into.

Two things make it survivable. The worklog is append-only by convention only, not
enforced, so cleaning it is an ordinary edit and commit — no invariant to work
around and no decision entry needed to authorise it. And the suite fails on
prefixed key shapes and PEM private-key headers appearing in the worklog:
AWS, GitHub, Anthropic, OpenAI, Slack, Google, Stripe, npm, JWTs. Detection, not
redaction: redacting at write time would contradict the verbatim guarantee, and a
false positive would silently destroy the record of what was actually said.

If a real secret lands there, order matters. **Rotate the credential first** —
it is already committed, and possibly pushed, so treat it as compromised no
matter what you do to the file next. Then edit the worklog and commit. Do not
rewrite git history: the agent is barred from it, and the old value stays
recoverable from any existing clone or fork regardless, which is why rotation is
the fix and the file edit is only tidying.

The check has limits worth knowing. It scans `adocs/worklog.md` only, not the rest
of `adocs/`. It uses fixed prefixes and PEM headers, with no entropy or bare-hex
rule, because the worklog carries a commit sha in every recap and would otherwise
be red every turn — an unprefixed password or a bare high-entropy string is not
caught. And it runs in moltke's own suite: a repository that installs moltke does
not inherit it, so wire an equivalent check into your own suite.

**The recap gate reads headings, not sizes.** `Stop` refuses when source changed
and no `## …recap…` heading follows the last `## … prompt` heading in the
worklog. It does not measure growth, because `UserPromptSubmit` appends the
prompt before the turn starts, so growth is always present by then (finding F01,
fixed in step S015). Two consequences worth knowing. A recap written for an
earlier turn does not discharge a later one, so an uncommitted change carried
across a question-only turn is asked about again — committing it satisfies the
gate just as a recap does, and the message says so. And the gate abstains in a
repository with no commit yet, so a fresh `--scaffold` never blocks.

**A repository with no git has no Stop cap.** The counter lives beside the git
directory, so in a marked repository that was never `git init`ed there is nowhere
to keep it and the waiver below never fires: every `Stop` refuses until you fix
what it names. The refusals are correct and actionable, there is simply no escape
hatch behind them. `git init` fixes it permanently, and deleting `.moltke.json`
turns everything off. This is accepted rather than planned (DEC-031): a
repository without git already gets no immutability checks, no `--audit check`,
and no prompt-failure breadcrumb, and the alternative was keeping moltke state
outside your project.

**Otherwise the Stop hook can never wedge a session, and never goes quiet either.** If it
blocks three times on the same problems inside one turn, the fourth attempt is
allowed with a warning — otherwise an unfixable refusal would trap you. That
count is per turn and per problem set: a new turn starts over, and fixing one
thing and hitting a different one starts over too, so partial progress does not
spend attempts. The waived turn still prints everything that was wrong. Before
0.4.0 the count keyed on a payload field that may not exist, and when it was
missing the counter was global and stored on disk, so from the fourth blocked
turn onward every Stop check was skipped — and stayed skipped across sessions.

"Source" means everything except two directories: `adocs/`, which is the
workflow's own state, and `.claude/`, which is your local tooling config. Both
are matched with their trailing separator. Before 0.4.0 the second was a bare
`.claude` prefix, which also exempted `.claude-plugin/plugin.json` — the manifest
whose `version` decides what every installed copy of moltke runs, so a release
could be cut with no recap of it — along with `.clauderc` or any other `.claude*`
file at the repository root.

**A prompt can still be lost, but never quietly.** `--log-prompt` creates
`adocs/` before appending, so a missing docs tree no longer discards prompts
(finding F14, fixed in step S014). If the append fails for any other reason —
unwritable path, `adocs/worklog.md` occupied by something that is not a file —
the prompt itself is gone and is not recovered. What the fix guarantees is that
you hear about it: the next `SessionStart` reports how many prompts were dropped,
since when, and the error, then stops repeating it. Outside a git repository
there is no breadcrumb to leave, so the failure only reaches stderr, which a
zero-exit `UserPromptSubmit` hook does not surface.

**Linked worktrees and submodules work.** moltke keeps three small state files
next to your git data — the prompt-failure breadcrumb, the `Stop` block counter
that guarantees a session can never be wedged, and the `--audit new` baseline.
It finds that location by asking git, so a linked worktree created with
`git worktree add` and a repository used as a submodule get all three, each
scoped to that worktree. Before 0.4.0 they were located by assuming `.git` is a
directory, which it is not in either case: all three vanished at once, with no
diagnostic and with `--validate` still reporting all checks pass.
