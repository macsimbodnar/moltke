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

Once per Claude config root — which is once per machine only if you run one
Claude. The CLI reads `~/.claude`; other clients, the desktop app among them,
set `CLAUDE_CONFIG_DIR` to a root of their own. Each root has its own plugin
registry, so installing in one does nothing for the others, and the miss is
silent: a root without moltke gets no hooks, no skills, and no reviewer agent,
while `~/.claude/CLAUDE.md` still loads and the session looks configured.

What a session is reading, and what that root has:

```
echo $CLAUDE_CONFIG_DIR
CLAUDE_CONFIG_DIR=<root> claude plugin list
```

Prefixing the install commands below with `CLAUDE_CONFIG_DIR=<root>` installs
into that root instead of the default one.

From the hosted repository:

```
claude plugin marketplace add https://github.com/macsimbodnar/moltke
claude plugin install moltke@moltke
```

Or from a local checkout, which is what you want while developing moltke itself:

```
claude plugin marketplace add /path/to/moltke
claude plugin install moltke@moltke
```

The local form copies the checkout into that root's plugin cache rather than
referencing it in place, and the copy takes untracked files too — including
`.moltke.local.md`, so keep naming local credentials by reference and never by
value. Because it is a copy, editing the checkout does not change what the
hooks run:

```
claude plugin update moltke@moltke
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
`plan_active_max` is how many steps one author may have in progress at once (per-author since 0.11.0, DEC-045), `plan_stack_max`
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
  compares them. Everything below `- Parked:` to the end of the file is carried
  through a regeneration verbatim, whatever its indentation, so that block is
  where anything worth remembering that no other file holds belongs
- a monitor armed as a watcher that cannot end itself is refused at arm time
  (INV-17): persistent monitors must be the `--watch` primitive or carry
  `MOLTKE_UNBOUNDED_OK`
- `adocs/decisions.md` may be compacted freely, ids stable (INV-8 retired in
  0.9.0, DEC-042). Prompt logging and the worklog were removed in 0.11.0
  (DEC-046): forensic history is git
- writes into completed history are refused
- the turn will not end with a stale `status.md`, an invariant violation, a
  crashed watcher, or a watch outcome nobody acted on

Project-wide rule changes have their own surface too: the `## Project rules`
section at the end of the scaffolded `AGENTS.md`. Rules there override the base
ruleset for that repository and travel in git. Precedence, most specific wins:
`.moltke.local.md` (machine) > `## Project rules` (project) > base ruleset.

Every session also carries `.moltke.local.md`: machine-local instructions —
tool paths, per-platform directives — that moltke creates at the marked root
when absent, keeps out of git via `.git/info/exclude`, and injects into the
session context. Edit it freely and keep it small; its content is paid for in
every session. What a teammate's machine also needs does not belong there.

Drive the plan with `/moltke:step`, audit with `/moltke:audit`. Both refuse
rather than repair, and name the condition that is missing.

## Teams

moltke is built for a team on branch-per-member, with a shared branch possible.
The plan is common: anyone picks the derived next step, and `--step start`
claims it (`author:` from `git config user.name`); `plan_active_max` counts per
author, so a merge of two branches each carrying its owner's active step is
green.

What merges how: the scaffolded `.gitattributes` union-merges `adocs/testing.md`
(append-only rows, both sides kept) and `adocs/status.md` — status is derived,
so after any merge run `bin/moltke.py --step status` and commit the
regeneration. `adocs/plan.md` is left to merge honestly: its order is a human
decision, and a conflict there is a real question, not noise. Step-id
collisions — two branches minting the same `S<nnn>` before merging — are caught
by INV-6 at `--validate`; the remedy is renaming one file and fixing its
`plan.md` line, and short-lived branches make it rare.

Outside Claude Code nothing enforces the rules; a cheap backstop every teammate
can wire once per clone:

```
printf '%s\n' '#!/bin/sh' 'exec python3 bin/moltke.py --validate' > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

`git commit --no-verify` is the documented escape for a deliberate red commit.
Platforms: macOS and Linux. Windows is unsupported — `hooks.json` invokes
`python3` directly.

## Review model

Three tiers. After each completed step the agent runs a fast check — one small
subagent over that step's diff, top problems only, no report file; trivial
findings are fixed on the spot, real ones become steps. When a change carries
risk (security-adjacent, public surface, a long stretch unaudited) the agent
proposes a full adversarial audit and you accept or postpone; a postponed
proposal waits as one line in `status.md`'s Parked block. And `/moltke:audit`
runs the full machinery whenever you ask, unchanged: clean-context reviewer,
report before fixes, every finding landing in a step or a decision. A finding
closes on a re-run that no longer reports it, or by a recorded decision — the
loop ends when you say it ends.

## Watching long runs

For overnight or detached work — a tuning run, a long benchmark — never arm a
`tail -f | grep` watcher: it cannot exit (matching is not exiting), and a
persistent one leaks until someone notices an idle machine. Arm the primitive
instead:

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --watch run.log 'RUN-(DONE|FAILED)' --ceiling 8h --pid 12345
```

It polls the log (default every 30s) and terminates by itself on every path:

| Exit | Meaning |
|---|---|
| `0` | marker matched; the matched line is printed |
| `4` | `--fail-re` matched |
| `3` | `--pid` died without a marker (the log is scanned one final time first) |
| `124` | `--ceiling` reached — required, at least 2x the expected run time |

The whole file is scanned each poll, so a marker written before arming is
still caught. That costs one full read plus one regex pass per interval, so a
log measured in gigabytes wants a wider `--interval` than the 30s default. The
ceiling bounds the scan itself, not only the wait between scans: a caller regex
that backtracks catastrophically, or a read that will not finish, exits `124`
and is recorded as a ceiling like any other, never as a quiet no-match. Each
watch registers itself in `moltke_watch/` inside the git directory git
reports — `.git/moltke_watch/` in a plain clone, per-worktree in a linked
worktree or a submodule, never nowhere — and writes
its outcome there on exit — including being killed — so a session that died
overnight can find the result the next morning: session start reports it, and
the turn refuses to end until someone acts on it. After acting on a result,
delete the record file to acknowledge it. Durations take `s`/`m`/`h`/`d`
suffixes. Rules and the no-plugin fallback loop: AGENTS.md §12.

In Claude Code, arm it through a persistent monitor: the harness caps bounded
monitors at one hour, so `persistent: true` plus `--ceiling` is the intended
overnight form — the ceiling is the real timeout, and the process ends itself.
The PreToolUse lint enforces exactly this (INV-17): a persistent monitor that
is not the primitive is refused at arm time, unless its command carries
`MOLTKE_UNBOUNDED_OK` — the deliberate escape for genuinely unbounded streams
such as a dev-server error tail. The primitive has to be the command that runs:
mentioning `--watch` in a trailing comment, or echoing it before a
hand-composed follow, is refused exactly like the bare leak. A single-match follow
(`tail -f log | grep -m1 DONE`) is refused always: it looks like a fix and
hangs by construction.

## Reference: every mode

Skills call `bin/moltke.py`. You can run it by hand, and other tools (Codex,
Cursor) must, since hooks exist only in Claude Code.

| Command | What it does |
|---|---|
| `--version` | print the moltke version and where it runs from. Hooks execute the installed plugin cache, not your checkout, so when behaviour looks stale this is the first question |
| `--validate` | run every invariant, print all violations, exit 1 if any |
| `--roadmap` | print where the plan is: one timeline strip, the done/left split, and the step in progress or the derived next one. Derived from `plan.md` and the plan directories, never from `status.md` |
| `--scaffold` | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `adocs/` from templates; never overwrites an existing file, and reports for each kept ruleset file whether it still matches the installed template |
| `--decline` | record that this repository declines the workflow, durably; refuses to disable an already-enabled repository |
| `--step new <name>` | allocate the next step id, write the step file, list it in `plan.md`. The name must match `[A-Za-z0-9_]+`, because it becomes the second half of `S000_<name>.md` and every invariant check reads that pattern; a hyphen or a dot would file a step no check can see |
| `--step start <id>` | move a step from `plan_todo/` to `plan_current/` and claim it: `author:` is stamped from `git config user.name`. Refuses when *your* active step is already at `plan_active_max` — a teammate's claimed step never blocks you — or when the destination id is already carried |
| `--step block <parent> <name>` | create a blocking child in `plan_current/` and pause its parent; the name follows the same `[A-Za-z0-9_]+` rule as `--step new` |
| `--step unpause <id>` | clear a `paused_by` that never resolves: one naming a step in no plan directory, one naming the step itself, or one in a ring of steps pausing each other. Exactly the cases `--validate` reports. Refuses when the pauser exists and is reachable — complete that one instead, which unpauses the parent on its way out |
| `--step done <id>` | complete a step and move it to `plan_done/`, refusing before the suite gate runs when `plan_done/` already holds that id — history is never overwritten. Runs the `test_command` suite gate when the marker sets one, refuses on a non-zero exit. `--stamp` is required free text; multi-line stamps are written as indented continuations (DEC-048) |
| `--step status` | regenerate `status.md` from the filesystem, keeping the Parked list |
| `--audit new <type>` | open `adocs/audit/YYYY-MM-DD_<type>.md`; never overwrites a report — a same-day re-run becomes `YYYY-MM-DD_<type>.2.md`, and its findings are numbered from that name. The type must match `[A-Za-z0-9_-]+`, so it stays a filename and cannot collide with that `.2` suffix. Also records a working-tree baseline for `--audit check` |
| `--audit list` | every finding, its status, and what references it; exits 1 while an open finding has neither a step nor a decision, or while a report names a finding a code fence hides, which lists as `hidden` (INV-14) |
| `--audit check` | reconcile what the run changed against that baseline: the report and new files under `tests/` are expected, anything else exits 1. Run it after the reviewer returns, before acting on a finding |
| `--watch <log> <regex> --ceiling <dur>` | self-terminating watcher for long runs; see "Watching long runs". Optional `--pid <p>`, `--fail-re <regex>`, `--interval <dur>` |
| `--session-start` | SessionStart hook: emit the stack and derived next step as context |
| `--pre-write` | PreToolUse hook for Write and Edit: refuse writes into `plan_done/`, step files outside the plan directories, and reviewer writes other than `adocs/audit/` or a new file under `tests/` |
| `--pre-command` | PreToolUse hook for Monitor: refuse watcher arms that cannot end themselves (INV-17); see "Watching long runs" |
| `--post-write` | PostToolUse hook: cheap invariant scan, surfaced but non-blocking |
| `--stop` | Stop hook: refuse to end a turn on violations, a stale `status.md`, or a completion that arrived without its stamp |

`--step new` takes `--goal TEXT`; `--step done` takes `--stamp TEXT` and
requires it. Both are written as one line of a step file, so a value containing
a line break is refused rather than reflowed: the continuation would land flush
left, where the parser reads it as a new field and drops it, and where `plan.md`
reads it as another list entry. Long single lines are the convention here. Every mode exits 0 immediately in a repository with no marker, or
one whose marker says `enabled: false` — except `--scaffold` and `--decline`,
which exist to create that marker, and `--watch`, whose exit codes are answers
about a run and must never be faked by the gate.

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
| `3` `4` `124` | `--watch` only: watched pid died, `--fail-re` matched, ceiling reached | stderr |

Exit `1` means two different things and they arrive on different streams:
`--validate`, `--audit list`, and `--audit check` print findings to stdout, while
every refusal — `--step` transitions, an unknown operation, a failing
`test_command`, `--decline` against an enabled repository — goes to stderr. `--audit new` on an existing report is not among
them: it takes a `.2` suffix and exits `0`. **If you script
this, capture both**, or you will get an exit code with no message. That matters
most outside Claude Code, where `--validate` is the only lever you have.

Since 0.6.0 no mode ends in a Python traceback. A file moltke cannot read — a directory
where a step file belongs, a path the index has and the worktree does not — is
reported as a violation naming the check that hit it, and anything else a broken
tree reaches is caught at the top and exits `2` with the path. `--session-start`
still exits `0` there, because it may never block.
`--scaffold` and `--decline` are the exception to where that catch lives: they run
before it, since they exist to create the marker it comes after, so each guards its
own writes and refuses with exit `1`. A `--scaffold` that fails partway removes what
that run had created, rather than leaving an enabled marker over a tree it never
finished building.

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
however you moved it — `git mv`, a plain `mv`, or `mv` then `git add -A`. Up to
and including 0.4.0 a staged rename walked past it, because it read the old
path; 0.5.0 carries the fix. It abstains before the first commit, where every file is new, and it skips
a path the index has and the worktree does not — which is what moving a step
back out of `plan_done/` produces, and the only compliant way to undo a
completion, since the file itself may not be edited there. The same used to be true of the green-suite
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

If the baseline `HEAD` is no longer reachable, that is reported rather
than skipped, because history was rewritten under the run. Without git, or before
`--audit new` has run, the check refuses instead of passing quietly.

**Code fences hide content from the scanners, and nothing blocks on it.** Every
check that reads `plan.md`, `decisions.md`, or an audit report strips fenced
blocks first, so a template's worked example is never mistaken for a real
decision or finding — and a quoted finding heading inside a fence stays a quote.
The fence police (INV-13/14/16) were retired in 0.11.0 (DEC-047): an unclosed
fence no longer blocks anything, and its one real consequence is visible in
`--audit list`, which names a swallowed finding as `hidden` and exits 1 until
the fence is closed.

**The immutability check needs git, and reads history as well as HEAD.** INV-7
(`plan_done/` unchanged) compares the working tree against `git HEAD`, which
covers changes you have not committed, and also walks `git log`, which covers
changes you have. Committing tampering therefore does not hide it. The commit the
violation names is the one it compares against — the commit that added the file —
not the commit that did the damage, which moltke never identifies. Restoring
those bytes in a new commit is what clears it. In a repository with no history,
or for a file not yet committed, there is no baseline and the check abstains
rather than guessing. INV-8, which held `adocs/decisions.md` append-only the same
way, was retired in 0.9.0 (DEC-042): the documents hold current state, and git is
the archive.

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

**Without somewhere to write its state, the Stop hook has no cap.** The counter
lives beside the git directory, so in a marked repository that was never
`git init`ed — or one whose `.git` cannot be written — there is nowhere to keep
it and the waiver below never fires: every `Stop` refuses until you fix
what it names. The refusals are correct and actionable, there is simply no escape
hatch behind them. `git init` fixes it permanently, and deleting `.moltke.json`
turns everything off. This is accepted rather than planned (DEC-031): a
repository without git already gets no immutability checks, no `--audit check`,
and no `--audit check`, and the alternative was keeping moltke state
outside your project. An unwritable `.git` is the same case and says so: the
`Stop` message names the state file it could not write, so the missing waiver is
explained rather than mysterious.

**Otherwise the Stop hook can never wedge a session, and never goes quiet either.** If it
blocks three times on the same problems inside one turn, the fourth attempt is
allowed with a warning — otherwise an unfixable refusal would trap you. That
count is per problem set: fixing one thing and hitting a different one starts
over, so partial progress does not spend attempts, and identical problems
carried across turns keep counting — a stuck session frees itself either way. The waived turn still prints everything that was wrong. Before
0.4.0 the count keyed on a payload field that may not exist, and when it was
missing the counter was global and stored on disk, so from the fourth blocked
turn onward every Stop check was skipped — and stayed skipped across sessions.

**A marked project can sit below the git top level.** Vendoring a moltke project
into a monorepo, or having any ancestor directory be a git repository, used to
break every git-derived check at once: INV-7 called a present file gone with a
remedy that could not run, INV-8 said nothing about real tampering, `--audit
check` reported its own report as unexpected. moltke now translates between the two directories. One place
the difference shows: the `git show <sha>:<path>` half of a printed remedy keeps
the path from the top level, because that is what `git show` resolves — the file
it names and the destination it writes are yours.

**Linked worktrees and submodules work.** moltke keeps three small state files
next to your git data — the prompt-failure breadcrumb, the `Stop` block counter
that guarantees a session can never be wedged, and the `--audit new` baseline.
It finds that location by asking git, so a linked worktree created with
`git worktree add` and a repository used as a submodule get all three, each
scoped to that worktree. Before 0.4.0 they were located by assuming `.git` is a
directory, which it is not in either case: all three vanished at once, with no
diagnostic and with `--validate` still reporting all checks pass.
