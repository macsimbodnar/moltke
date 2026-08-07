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

Then fill in `adocs/specs.md`, the one file moltke cannot write for you: the
prime directive, and the invariants as numbered testable properties.

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
non-empty string if present; a blank one is a marker violation, because a gate
that silently checks nothing is worse than no gate. The command runs with your
shell and your privileges, so treat the marker as executable content: do not set
it to something you would not run by hand.

## Daily use

Nothing to remember. Hooks fire on their own:

- session start prints the current stack and the next step, and says so when
  `status.md` disagrees with the filesystem
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
| `--scaffold` | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `adocs/` from templates; never overwrites an existing file |
| `--decline` | record that this repository declines the workflow, durably; refuses to disable an already-enabled repository |
| `--step new <name>` | allocate the next step id, write the step file, list it in `plan.md` |
| `--step start <id>` | move a step from `plan_todo/` to `plan_current/` |
| `--step block <parent> <name>` | create a blocking child in `plan_current/` and pause its parent |
| `--step done <id>` | complete a step and move it to `plan_done/`, refusing if anything is missing. Runs the `test_command` suite gate when the marker sets one, and refuses on a non-zero exit |
| `--step status` | regenerate `status.md` from the filesystem, keeping the Parked list |
| `--audit new <type>` | open `adocs/audit/YYYY-MM-DD_<type>.md`; never overwrites a report — a same-day re-run becomes `YYYY-MM-DD_<type>.2.md`, and its findings are numbered from that name. Also records a working-tree baseline for `--audit check` |
| `--audit list` | every finding, its status, and what references it; exits 1 while an open finding has neither a step nor a decision |
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
not that it was answered honestly. The same used to be true of the green-suite
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

**`--audit check` sees what `git status` sees.** It compares porcelain output
with `-uall` plus a content hash per changed file, against the baseline recorded
by `--audit new`. Consequences worth knowing: a change to a `.gitignore`d path is
invisible to it, because git does not report those; changes the reviewer commits
itself stop being reported as changed and show up as "reverted or committed",
which is flagged as unexpected rather than hidden; and pre-existing dirt in your
tree is in the baseline, so it is never blamed on the audit. Without git, or
before `--audit new` has run, the check refuses instead of passing quietly.

**Immutability checks need git, and read history as well as HEAD.** INV-7
(`plan_done/` unchanged) and INV-8 (`adocs/decisions.md` append-only) compare the
working tree against `git HEAD`, which covers changes you have not committed, and
also walk `git log`, which covers changes you have. Committing tampering
therefore does not hide it: the violation names the commit that did it. In a
repository with no history, or for a file not yet committed, there is no baseline
and the check abstains rather than guessing.

What this cannot do is unwrite history, and it does not try. Both checks compare
what the file says **now** against the version it had at a fixed point — the
commit that added a `plan_done/` file, the first commit for `decisions.md`. So
the way back to green is the one the message tells you: restore those bytes in a
new commit, and the violation clears. Leave it rewritten and it keeps reporting.
Nothing is ever reverted for you, and git history stays intact as the record.

For `decisions.md` the comparison is by line, not by byte: every line the file
legitimately had must still be there, in that order. So appending is free,
inserting in the middle passes, and removing a line, rewriting one in place, or
moving one to the end are all caught. Reordering entries is a violation until it
is reversed.

Three known limits. A file created and deleted inside the same commit leaves
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
