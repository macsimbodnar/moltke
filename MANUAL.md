# moltke manual

Install, operate, known issues. For working on moltke itself, see
[README.md](README.md).

## What it does

moltke keeps a project's memory in tracked files and refuses to let it drift:

- `project/status.md` where we are, regenerated from the filesystem
- `project/specs.md` the prime directive and the numbered invariants
- `project/plan.md` plus `plan_todo/`, `plan_current/`, `plan_done/`
- `project/decisions.md` why things are the way they are, with rejected options
- `project/testing.md` acceptance criteria and their covering tests
- `project/audit/` findings, as evidence, before any fix

Enforcement is blocking, and only in repositories that opt in. A repository
without `.moltke.json` feels nothing at all.

## Install

Once per machine. From a checkout of this repository:

```
claude plugin marketplace add /path/to/moltke
claude plugin install moltke@moltke
```

Or from Claude Code, with `/plugin marketplace add`, `/plugin install`, then
`/reload-plugins` to activate it in the current session. Once the repository is
hosted, the same commands accept its git URL in place of the path.

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
`.moltke.json`, and a populated `project/`. No records the refusal durably and
never asks again. Nothing existing is ever overwritten: a repository that
already has an `AGENTS.md` keeps it, and moltke reports what it left alone.

Then fill in `project/specs.md`, the one file moltke cannot write for you: the
prime directive, and the invariants as numbered testable properties.

`.moltke.json` controls everything:

```json
{
  "schema": 1,
  "enabled": true,
  "plan_active_max": 1,
  "plan_stack_max": 3,
  "surface_guard": "cli"
}
```

`enabled: false` disables every check, permanently, until the file is deleted.
`plan_active_max` is how many steps may be in progress at once, `plan_stack_max`
how deep the paused stack may go. `surface_guard` is `cli`, `api`, `both`, or
`none`, and `none` is only valid alongside a decision entry saying why the
project has no checkable surface.

## Daily use

Nothing to remember. Hooks fire on their own:

- session start prints the current stack and the next step, and says so when
  `status.md` disagrees with the filesystem
- every prompt is appended verbatim to `project/worklog.md`
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
| `--scaffold` | create the marker, `AGENTS.md`, `CLAUDE.md`, the Cursor pointer, and `project/` from templates; never overwrites an existing file |
| `--decline` | record that this repository declines the workflow, durably; refuses to disable an already-enabled repository |
| `--step new <name>` | allocate the next step id, write the step file, list it in `plan.md` |
| `--step start <id>` | move a step from `plan_todo/` to `plan_current/` |
| `--step block <parent> <name>` | create a blocking child in `plan_current/` and pause its parent |
| `--step done <id>` | complete a step and move it to `plan_done/`, refusing if anything is missing |
| `--step status` | regenerate `status.md` from the filesystem, keeping the Parked list |
| `--audit new <type>` | open `project/audit/YYYY-MM-DD_<type>.md`; refuses to overwrite a report |
| `--audit list` | every finding, its status, and what references it; exits 1 while an open finding has neither a step nor a decision |
| `--session-start` | SessionStart hook: emit the stack and derived next step as context |
| `--log-prompt` | UserPromptSubmit hook: append the prompt to the worklog. Never blocks, because blocking here would erase your prompt |
| `--pre-write` | PreToolUse hook for Write and Edit: refuse writes into `plan_done/`, step files outside the plan directories, and anything outside `project/audit/` written by the reviewer |
| `--post-write` | PostToolUse hook: cheap invariant scan, surfaced but non-blocking |
| `--stop` | Stop hook: refuse to end a turn on violations, a stale `status.md`, or unrecapped source changes |

`--step new` takes `--goal TEXT`; `--step done` takes `--stamp TEXT` and
requires it. Exit codes: `0` fine, `1` violations on stdout, `2` blocked with
the reason on stderr. Every mode exits 0 immediately in a repository with no
marker, or one whose marker says `enabled: false` — except `--scaffold` and
`--decline`, which exist to create that marker.

## Known issues

**The plugin ships moltke's own project state.** The repository root is also
the plugin root, so `project/`, `tests/`, `AGENTS.md`, and `CLAUDE.md` are
copied into every install's cache. They are inert. `claude plugin validate
--strict` warns that the root `CLAUDE.md` is not loaded as project context; the
warning is accurate and harmless. Recorded as DEC-020, with a `plugin/`
subdirectory move as the escape hatch if it ever matters.

**The README and MANUAL gate is mechanical.** `--step done` and the Stop hook
require the completion stamp to mention README and MANUAL. They cannot tell
whether you actually looked. The check enforces that the question was asked,
not that it was answered honestly.

**The reviewer's write fence depends on one field.** `adversarial_reviewer` is
confined to `project/audit/` by the PreToolUse hook reading `agent_type`.
Subagent frontmatter has no path restriction, so this is the only place the
limit can live. If that field is ever renamed or absent, the fence opens
silently rather than failing closed.

**Immutability checks need git.** INV-7 (`plan_done/` unchanged) and INV-8
(append-only files) compare against `git HEAD`. In a repository with no history,
or for a file not yet committed, there is no baseline and the check abstains
rather than guessing.

**Live hook behaviour is not yet verified.** The hooks are wired and unit
tested, but moltke has not been installed and exercised in a real session, on
this machine or a second one. That is step S012 in `project/plan.md` and it is
not done. Until it is, treat the hook layer as untested in the field.
