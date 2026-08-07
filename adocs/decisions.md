# Decisions

Append only, newest last. Every entry: stable `DEC-<nnn>` id, tags, context,
decision, rejected options, consequences. A reversal marks the old entry `VOID`,
dated, with a pointer to the superseding entry; it never deletes.

DEC-001..DEC-012 seeded during S001 from `bootstrap.md` §2: locked by Max in the
planning session of 2026-08-01, analysis and options supplied by the agent in
that session. Not to be relitigated during implementation. Originally seeded
newest first; reordered oldest first under DEC-013, same day, before any
enforcement existed.

## DEC-001  2026-08-01  Package as a plugin, not a loose skill
Tags:         distribution, plugin
Context:      the workflow must work on several dev machines.
Decision:     plugin in a git repo, installed via marketplace. (Max, planning session)
Rejected:     personal skill in `~/.claude/skills/` (per machine, unversioned, drifts); dotfiles symlink (no versioning, no update path).
Consequences: skills are namespaced `/max_agent_workflow:name`; updates land only when `version` in `plugin.json` is bumped.

## DEC-002  2026-08-01  Repository is public, with an explicit version field
Tags:         distribution, security
Context:      public exposes the workflow but not any project data. The real risk is write access, not read access, because plugin hooks execute shell commands on every machine where the plugin is installed.
Decision:     public repository, explicit `version` in `plugin.json` so updates require a deliberate bump, branch protection on `main`, 2FA on the account, no blind PR merges. (Max, planning session)
Rejected:     private repo (hides internal conventions, but the templates carry no project-specific content, and private adds a credential requirement on each new machine).
Consequences: templates must stay generic. Nothing about any employer, product, or internal architecture goes into this repository. Confirm this decision with Max before the first push.

## DEC-003  2026-08-01  AGENTS.md is the single source of truth for the rules
Tags:         rules, tools
Context:      Codex and Cursor may run in the same repositories.
Decision:     rules live in `AGENTS.md` at the target repo root; `CLAUDE.md` contains only `@AGENTS.md`; Cursor gets a thin `.cursor/rules` pointer. (Max, planning session)
Rejected:     maintaining parallel rule files per tool (guaranteed drift).
Consequences: Claude Code reads `CLAUDE.md`, not `AGENTS.md`, so the import line is mandatory and must be verified against current docs.

## DEC-004  2026-08-01  The workflow directory is project/, not agents/
Tags:         layout, naming
Context:      `agents/` collides with `AGENTS.md`, with `.claude/agents/` for subagent definitions, and with the plugin layout's own `agents/` directory.
Decision:     `project/`. (Max, planning session)
Rejected:     `agents/` (the collisions above).
Consequences: this repository, being a plugin, has a real `agents/` directory for subagents, and it must not be confused with workflow state.

## DEC-005  2026-08-01  Marker file .workflow.json at target repo root
Tags:         marker, hooks
Context:      hooks need one fixed path to check, and declining setup must be recordable without creating the directory the user declined.
Decision:     `.workflow.json` at root carries `schema`, `enabled`, `plan_active_max`, `plan_stack_max`, `surface_guard`. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: every hook exits 0 immediately when the file is absent or `enabled` is false. No marker, no friction.

## DEC-006  2026-08-01  Enforcement is blocking, gated on the marker
Tags:         hooks, enforcement
Context:      Max asked for maximum strictness conditional on correct setup.
Decision:     hooks block rather than warn, but only in marked repositories. (Max, planning session)
Rejected:     warn-only (ignored in practice); always-on (unusable in third-party checkouts).
Consequences: every blocking message must state exactly what to do to unblock, because a `Stop` hook has a cap on consecutive blocks and an unactionable message deadlocks the session.

## DEC-007  2026-08-01  plan_current/ is a stack, not a set
Tags:         plan, concurrency
Context:      work discovered mid-step often blocks the step in progress.
Decision:     blocking discoveries are promoted as children with `blocks:` and `paused_by:` links; `plan_active_max` non-paused steps (default 1), `plan_stack_max` total depth (default 3). (Max, planning session)
Rejected:     simply raising a concurrency counter (loses the dependency, conflates blocking work with parallel work).
Consequences: exceeding the depth limit is a signal the plan is wrong at design level and routes to a decision plus a replan.

## DEC-008  2026-08-01  Step ids are stable and never renumbered
Tags:         plan, naming
Context:      position-encoding filenames make insertion and reordering expensive.
Decision:     `S<nnn>_short_name.md` allocated in creation order; plan order lives only in `plan.md`. (Max, planning session)
Rejected:     position-encoding filenames (renaming cascades on every insertion or reorder).
Consequences: reordering is a one-line edit; ids stay valid as references from commits, decisions, and audit findings.

## DEC-009  2026-08-01  status.md added; ideas.md and history/ rejected
Tags:         layout, status
Context:      a prior working system used all three.
Decision:     keep `status.md` (session pointer, rewritten in place). (Max, planning session)
Rejected:     `ideas.md` (its function is covered by a Parked section in `status.md` and by recorded rejected options in `decisions.md`); `history/` (`plan_done/` plus git already is the history, and a second copy invites resuming retired checklists).
Consequences: the rule "never resume a checklist from `plan_done/`" carries the weight `history/` would have carried.

## DEC-010  2026-08-01  The public-surface golden test is mandatory
Tags:         testing, docs, surface
Context:      documentation drifts silently from code.
Decision:     a golden test over whatever `surface_guard` names, failing until MANUAL and specs are updated in the same commit. Opting out requires `surface_guard: "none"` plus a recorded reason. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: this repository's own surface is the `workflow_check` CLI, so `surface_guard` here is `cli`.

## DEC-011  2026-08-01  worklog.md is forensic, never a context source
Tags:         worklog, context
Context:      an append-only prompt log grows without bound and would become the largest and least useful file in the repo.
Decision:     agents never read `worklog.md` to determine state or reasoning. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: anything in it that matters must be promoted into `status.md`, `specs.md`, or `decisions.md`.

## DEC-012  2026-08-01  This repository self-hosts the workflow
Tags:         process, dogfood
Context:      the conventions should be tested somewhere low-stakes before being applied to real work.
Decision:     `max_agent_workflow` is the first project to use the workflow, with `bootstrap.md` becoming its `project/specs.md` and this build becoming its first plan. (Max, planning session)
Rejected:     none recorded in the planning session.
Consequences: the root `AGENTS.md` is the live ruleset, `templates/AGENTS.md` is the shipped copy, and a test asserts the two are identical.

## DEC-013  2026-08-01  decisions.md orders oldest first, newest appended at bottom
Tags:         decisions, layout, efficiency
Context:      AGENTS.md mandated newest-first ordering while INV-8 required append-only growth with earlier bytes unchanged; a new entry at the top shifts earlier bytes. Surfaced during S001, routed to S004, resolved by Max the same day.
Decision:     newest last. Entries append at the bottom via shell append, costing no reads; INV-8 stays literal byte-append for both `worklog.md` and `decisions.md`. (Max)
Rejected:     newest-first with an entry-integrity check (every write costs a partial read; INV-8 becomes entry-based — more code, weaker guarantee; recency reads are `tail -n` and lookups are grep either way, so top ordering bought nothing).
Consequences: AGENTS.md §2 and §8 amended; the seeded DEC-001..DEC-012 reordered oldest first in the same commit, authorized by this decision as a one-time exception to the §11 reorder prohibition; the S004 reconcile clause dropped.

## DEC-014  2026-08-01  GitHub configuration is Max's own; agent git surface is commits only
Tags:         git, github, process
Context:      S001 surfaced open items around repository visibility (DEC-002 confirmation), branch naming versus the `main` protection target, and pushing.
Decision:     Max handles GitHub configuration personally: visibility, remotes, branch naming and protection, pushes, app installs. The agent creates commits and nothing else, until new orders. (Max)
Rejected:     agent-driven branch rename and push preparation (offered, declined).
Consequences: DEC-002 confirmation resolves whenever Max pushes; master/main naming is Max's call; status.md parked items updated accordingly.

## DEC-015  2026-08-01  Project renamed to moltke
Tags:         naming, distribution
Context:      Max renamed the project before implementation started. Moltke commanded armies he could not see by writing orders that survived his absence; same problem, smaller scale.
Decision:     full rename: plugin and repository `moltke`; skills `init`, `step`, `audit` (commands /moltke:init, /moltke:step, /moltke:audit); CLI `bin/moltke.py`; marker `.moltke.json`; template `templates/moltke.json`. (Max)
Rejected:     namespace-only rename keeping `workflow_check.py`, `.workflow.json`, and the long skill names (smallest diff, but a generic marker name can collide with other tools, and nothing is coded yet, so the full rename is free now versus a migration later).
Consequences: earlier entries and immutable history naming `max_agent_workflow`, `workflow_check`, or `.workflow.json` (DEC-001, DEC-005, DEC-010, DEC-012, plan_done/S001, old testing.md rows, worklog) read through this entry; specs, AGENTS.md, plan, and step files updated in the same commit; GitHub repository rename and local directory rename are Max's own (DEC-014).

## DEC-016  2026-08-01  Build moltke rather than adopt an existing tool
Tags:         scope, ecosystem
Context:      before S002, Max asked whether an existing tool makes this redundant. Web evaluation of 2026-08-01: GitHub Spec Kit (~93k stars, constitution + specify/plan/tasks loop), GSD Core (STATE.md/CONTEXT.md phase loop, ex-GSD after archive/fork churn), BMAD (multi-agent personas), OpenSpec (change proposals with deltas), Beads (git-backed graph issue tracker as agent memory), SpillwaveSolutions/project-memory (memory-files skill, explicitly no enforcement). All are convention- or prompt-based: none ships marker-gated blocking enforcement, an append-only decision log with mandatory rejected options, report-before-fix audit discipline, or a red-first testing ledger.
Decision:     proceed with moltke as planned. (Max, after agent-supplied evaluation)
Rejected:     Spec Kit or GSD Core plus Beads (~70% coverage — planning structure and task state — at zero build cost, but compliance stays advisory and the evidence discipline is absent); adopting project-memory (no enforcement, no plan lifecycle, no testing ledger).
Consequences: the differentiator to protect is DEC-006 enforcement plus the evidence discipline; AGENTS.md as single source (DEC-003) matches the now-standard convention; the S002..S011 plan stands unchanged.

## DEC-017  2026-08-01  Setup modes are exempt from the INV-11 marker gate
Tags:         marker, cli, invariants
Context:      INV-11 requires every mode to exit 0 immediately when the marker is absent, but `--scaffold` exists precisely to create the marker in a repository that has none. Surfaced during S002, resolved at S006.
Decision:     INV-11 applies to every mode except the setup modes `--scaffold` and `--decline`, which run before the gate. `--decline` is added to the surface so declining is mechanical and durable rather than hand-written JSON. (Max, agent-supplied analysis)
Rejected:     dropping the gate for all modes (unmarked third-party checkouts would gain friction, defeating DEC-005); having the skill hand-write the declined marker (untestable, and the decline path is exactly what must be reliable).
Consequences: specs INV-11 carries a dated amendment; the CLI surface grows `--decline`, which the S009 golden test must cover; both setup modes still refuse to touch a repository whose marker says `enabled: false`.

## DEC-018  2026-08-01  Cursor pointer kept thin; Cursor reads AGENTS.md natively
Tags:         cursor, tools, templates
Context:      DEC-003 planned a `.cursor/rules` pointer. Cursor documentation checked 2026-08-01 states Cursor reads `AGENTS.md` natively and calls it a simple alternative to `.cursor/rules`; the legacy `.cursorrules` file is gone and project rules are `.cursor/rules/*.mdc` with `description`, `globs`, `alwaysApply` frontmatter.
Decision:     scaffold a minimal always-applied `.cursor/rules/moltke.mdc` that points at `AGENTS.md` and states no rules of its own. (agent-supplied analysis and choice, low-stakes; reversible by deleting the template)
Rejected:     dropping the pointer entirely (native support makes it redundant, but the pointer costs five lines and covers Cursor versions or configurations where native reading is off); a full parallel ruleset for Cursor (DEC-003 forbids it: guaranteed drift).
Consequences: the pointer must never carry rule content, only a reference, so `AGENTS.md` stays the single source of truth.

## DEC-019  2026-08-01  S010 narrowed to what the agent can verify; install checks become S012
Tags:         plan, verification, git
Context:      S010's acceptance included "marketplace entry installs on a second machine" and "DEC-002 confirmed before the first push". DEC-014 reserves all GitHub and environment configuration to Max: the agent commits and nothing else. Installing the plugin also mutates the local Claude Code configuration, which is outside "create commits".
Decision:     S010 covers what is mechanically verifiable without changing any environment: the manifest, the marketplace entry, component discoverability, and `claude plugin validate --strict`. Real installation, first-session hook firing, and second-machine verification move to S012, owned by Max, with the agent supplying exact commands. (agent-proposed under DEC-014, applied to the plan)
Rejected:     installing the plugin locally to satisfy the criterion (changes Max's Claude configuration without being asked, and a self-install is not the second-machine check the criterion actually wanted); marking S010 complete while claiming an unverified install (a completion stamp that overstates what was checked poisons every later reading of plan_done).
Consequences: `plan.md` gains S012 after S011; until it passes, the hooks and skills in this repository remain wired but never exercised by a live session, which is recorded in `status.md` rather than assumed away.

## DEC-020  2026-08-01  The plugin ships this repository's own workflow state
Tags:         plugin, layout, dogfood
Context:      `claude plugin validate --strict` on the plugin root warns that `CLAUDE.md` there is not loaded as project context. It is a symptom of a deliberate layout: DEC-012 self-hosts the workflow, so the repository root is simultaneously the plugin root, and `project/`, `tests/`, `.moltke.json`, `AGENTS.md`, and `CLAUDE.md` are copied into every install's plugin cache.
Decision:     keep the layout and record the consequence as a known issue in MANUAL rather than restructuring. (agent-supplied analysis; reversible)
Rejected:     moving the plugin into a `plugin/` subdirectory with `source: "./plugin"` (removes the cruft, but breaks the layout specs describe, splits the self-hosting story, and rewrites every hook and test path for a cosmetic gain); deleting the root `CLAUDE.md` (it is what makes Claude Code read `AGENTS.md` in this repository, per DEC-003).
Consequences: installs carry inert extra files, including this repository's worklog and plan history; the repository is public by DEC-002, so nothing is exposed that was not already. If the cache size or the confusion ever matters, the `plugin/` subdirectory move is the escape hatch.

## DEC-021  2026-08-02  The workflow directory is renamed project/ to adocs/
Tags:         naming, layout, distribution
Context:      `project/` is a generic name that collides with what many repositories already call their source or their build output, and it says nothing about who the files are for. The directory holds agent documentation: `adocs`.
Decision:     rename the directory to `adocs/` everywhere — scaffold output, every path in `bin/moltke.py`, the hook messages, the templates, the rules, the tests, and this repository's own state. No migration path is provided: no repository other than this one has the plugin installed, so there is nothing to migrate. `plugin.json` bumps to 0.2.0 so an install picks the change up deliberately (DEC-002). (Max; agent-supplied analysis of the blast radius)
Rejected:     making the directory name configurable through `.moltke.json` (turns a one-time rename into a permanent branch in every path expression, and a workflow whose file map varies per repository is exactly the drift AGENTS.md §2 exists to prevent); keeping `project/` and documenting the intent instead (the name is the documentation, and it is wrong); providing a migration mode that renames the directory in a target repository (no target repositories exist).
Consequences: paths inside immutable and append-only files still read `project/` — every file in `plan_done/`, and `worklog.md` and `decisions.md` entries before this one. They are history and are never rewritten; they read through this entry, exactly as DEC-015 governs the earlier `max_agent_workflow` naming. INV-8 has no HEAD baseline at the new path for exactly one commit and abstains; byte-identity across the move was verified by hand instead. Hooks in an already-installed plugin keep running the cached older copy against `project/` until the install is updated, so S012's install verification is redone against the renamed build.

## DEC-022  2026-08-06  The reviewer's write fence gives way to post-hoc reconciliation
Tags:         audit, reviewer, enforcement, hooks
Context:      the 2026-08-06 adversarial audit found (F03) that `adversarial_reviewer` holds `Bash` alongside `Write` while the fence is a `Write|Edit` PreToolUse matcher, so any shell redirect writes anywhere in the repository. The confinement specs.md and MANUAL.md described as enforced was enforced only for two tools. The deeper cause is that Claude Code expresses subagent limits in two places that do not compose: frontmatter names tools but not paths, hooks see paths but only for the tools their matcher names. The audit also exposed an incoherence: under the old fence the reviewer could not write a regression test at all except by shelling around its own fence.
Decision:     mutation during an audit is legitimate — the reviewer needs to create tests and reproduce defects, and git is the backstop. Prevention gives way to detection. `--audit new` records a working-tree baseline; a new `--audit check` reports what the run actually changed and flags anything beyond this run's report and new files under `tests/`. The fence stays but widens to `adocs/audit/` plus new files under `tests/`, as a fast clear failure on the common path rather than as the guarantee. `Bash` stays unconstrained by design. (Max, after agent-supplied analysis and options)
Rejected:     dropping `Bash` from the reviewer (makes the fence real for every write path it has, but kills reproduction — the four strongest findings in the 2026-08-06 report were Bash transcripts, and the agent's own standard is that a finding without evidence is an opinion); inspecting Bash command strings in the hook (arbitrary shell is not reliably parseable, `python3 -c "open(...,'w')"` defeats any matcher, and it would document a stronger guarantee than exists today); leaving the fence as it was and adding reconciliation on top (keeps the incoherence that the reviewer cannot write a test through the tool it is granted).
Consequences: `specs.md`'s claim that the hook "is the only place the limit can be real" is corrected, as is the `audit` skill's "that fence is enforced by a hook, not by good manners". A contaminated report is now detected rather than prevented, and detection happens between skill steps 2 and 3 so it is known before any finding is acted on. `AUDIT_OPS` grows `check`, which the S009 golden and the specs and MANUAL cross-check cover. The behavioural concern the fence existed for — a reviewer that patches stops reporting — is now addressed by the agent prompt plus reconciliation, not by the tool layer.

## DEC-023  2026-08-06  --step done gains an optional test_command gate
Tags:         testing, cli, marker, enforcement
Context:      the 2026-08-06 adversarial audit found (F07) that AGENTS.md section 4 and section 11 require a full green suite before a step completes, while `--step done` checks only that a `testing.md` row exists and that the stamp mentions README and MANUAL. It never runs or consults a test suite, and nothing else does. The workflow's headline quality gate was honour-system while MANUAL disclosed only the weaker README/MANUAL mechanical-gate problem, which made the suite check read as real.
Decision:     add an optional `test_command` key to `.moltke.json`. When present, `--step done` runs it and refuses on a non-zero exit, naming the failure. When absent, behaviour is exactly as today and the refusal path says the gate is not configured. Schema stays 1. (Max, after agent-supplied analysis and options)
Rejected:     accepting the gap and documenting it as advisory (cheapest and honest, but leaves the differentiator DEC-016 names — enforcement plus evidence discipline — resting on a gate nothing enforces); requiring `test_command` and bumping to schema 2 (strongest, but forces a migration on every existing marker and blocks completion in repositories that have no suite yet, which is exactly the state a fresh `--scaffold` leaves behind).
Consequences: the marker gains a key the S009 surface guard must cover, which is why S023 extends that guard to marker keys. `--step done` can now take as long as the suite does, so it runs with a timeout and reports the output tail. A repository that wants the old behaviour simply omits the key, so nothing existing breaks.

## DEC-024  2026-08-06  Worklog secrets are detected in the suite, never redacted at write time
Tags:         security, worklog, testing, invariants
Context:      the 2026-08-06 adversarial audit found (F08) that `--log-prompt` writes every prompt verbatim into `adocs/worklog.md`, a tracked file, and INV-8 then forbids altering earlier bytes — so a pasted secret is committed and cannot be removed without violating the workflow's own invariant, while AGENTS.md section 11 bars rewriting history outright. For moltke itself DEC-002 makes the repository public. AGENTS.md section 6 already mandates that secret-leak checks run inside the normal suite; none existed.
Decision:     detect, do not redact. A suite test fails when a prefixed key shape or a PEM private-key header appears in the worklog, and it is non-vacuous by construction: it first asserts a known-bad fixture string is caught. MANUAL records the exposure and the escape procedure for a real leak — a decisions.md entry authorising a one-time redaction, exactly as DEC-013 authorised a one-time reorder. (Max, after agent-supplied analysis and options)
Rejected:     redacting inside `mode_log_prompt` before appending (strongest containment, but it contradicts the verbatim guarantee of AGENTS.md section 9, and a false positive silently destroys forensic content, so the log stops being evidence of what was actually said); documenting the exposure with no detection at all (leaves the section 6 mandate unmet and a leak is found only when a human happens to notice).
Consequences: detection uses prefixed key shapes and PEM headers only, with no generic entropy or bare-hex rule, because this worklog is full of git shas and those heuristics would false-positive constantly. That is a deliberate sensitivity trade: the check catches the shapes worth catching and stays quiet otherwise. A leak still requires a human decision to clean, and that decision is now a documented procedure rather than an improvisation.

## DEC-025  2026-08-06  worklog.md drops out of INV-8; decisions.md keeps append-only
Tags:         worklog, invariants, immutability, decisions
Context:      INV-8 covers `adocs/worklog.md` and `adocs/decisions.md` in one rule, and AGENTS.md section 11 bars rewriting either. Max, reviewing S014, judged the worklog to be a useful history list rather than something worth an enforced invariant: it is forensic, never a context source (DEC-011), it grows without bound, and nothing cites a line of it by id. The cost of enforcing it is real — DEC-024 exists only because a secret pasted into a prompt becomes uneditable once committed.
Decision:     narrow INV-8 to `decisions.md` alone. The worklog stays append-only by convention and is no longer checked, so it can be trimmed, corrected, or redacted without violating anything. `decisions.md` keeps enforcement because `DEC-<nnn>` ids are cited from code comments, commit messages, `specs.md`, and step files, and a rewritten entry silently changes what every one of those citations means. (Max, choosing from agent-supplied options)
Rejected:     dropping INV-8 entirely, worklog and decisions together (one fewer invariant and no git-baseline logic left, but then nothing detects a decision entry being rewritten or dropped, and a DEC id cited in a commit can end up pointing at text it was never written against — the bidirectional traceability of section 8 is the thing INV-8 protects); keeping INV-8 as it stands (no change, but leaves an enforced invariant on a file whose only reader is a human doing forensics, and keeps a committed secret unremovable by rule).
Consequences: `INV-8`'s wording, `APPEND_ONLY_FILES`, AGENTS.md sections 2, 9 and 11, and `templates/AGENTS.md` all change together; the S004 INV-8 tests are re-targeted, not deleted, so the worklog case now asserts the check abstains while `decisions.md` still bites. S018 narrows to `plan_done/` and `decisions.md`. DEC-024 is not void — detection in the suite still beats redaction at write time — but its escape procedure gets simpler: cleaning a leaked secret from the worklog no longer needs a decisions.md entry authorising it. S015 is unaffected: its recap gate keys on a recap heading after the last logged prompt, not on worklog immutability.

## DEC-026  2026-08-07  A committed immutability violation clears when the content is restored
Tags:         invariants, immutability, git, audit
Context:      the 2026-08-07 adversarial audit found (F03) that S018's history baselines gave INV-7 and INV-8 no legal terminal state. They report any commit whose `plan_done/` status is not `A`, or that removed a line from `decisions.md`, and that commit is in history forever — so following the violation message exactly, restoring the content in a new commit, leaves `--validate` at exit 1 and `--stop` blocking every turn. The only operation that would clear it is a history rewrite, which the same message forbids and AGENTS.md section 11 prohibits. One accident therefore makes a repository permanently red, and after three blocks the Stop waiver fires and waves through every other Stop check for that prompt. This is not hypothetical: `e8084d3` removed 67 lines from `project/decisions.md` under DEC-013's authorised reorder, and this repository is green only because S013's rename moved the file and `--no-renames` starts its history there.
Decision:     the invariants judge current content against history, not the existence of a bad commit. A `plan_done/` file is clean when its bytes match the version at the commit that added it; `decisions.md` is clean when its current content still starts with every version it has ever had. Restoring what was removed, in a new commit, therefore clears the violation, and leaving it tampered keeps reporting it. History stays intact as the record and is never rewritten. (Max, choosing from agent-supplied options)
Rejected:     demoting a repaired violation to a non-failing note (keeps the event visible forever, but puts two severities inside one invariant and produces standing notes that people learn to skim past); requiring a dated waiver entry in `decisions.md` naming the commit sha, which is what DEC-013 did by hand (strongest audit trail, but the ceremony lands on whoever is cleaning up someone else's accident, and waivers accumulate unrevisited); repair-clears plus a waiver path for cases where restoration is wrong, such as an intended deletion or the DEC-013 reorder (covers both shapes, at the cost of two mechanisms to build, document, and test — deferred rather than dismissed, and worth revisiting the first time a legitimate removal has nowhere to go).
Consequences: the checks move from `git log --name-status` and `--numstat`, which read what happened, to content comparison against the add-commit blob and against every historical version, which reads what is true now. That costs blob fetches rather than a diff summary, so both use a single batched `git cat-file`. A tampering that is repaired leaves no standing signal in the tool — the commit is still in the log, and nothing points at it — which is the accepted cost of being able to return to green. The uncommitted-window checks against HEAD are unaffected. Under this rule the DEC-013 reorder would still be a violation until the removed lines were restored, because it genuinely removed content; that case is what a future waiver path would serve.

## DEC-027  2026-08-07  INV-8 judges one fixed baseline, and the gap that leaves is accepted for now
Tags:         invariants, immutability, git, decisions
Context:      DEC-026 chose "a repair commit clears it" and described INV-8 as "current content still starts with every version it has ever had". Implementing it in S034 showed that rule can never be satisfied after a repair: the tampered version is itself history, and no restoration can make the file start with it again, so the naive form has exactly the permanence problem DEC-026 set out to remove. Two escapes were tried and measured. Forgiving a version when a longer version is a prefix of the current file clears the repair case but also clears a same-position edit that lengthens the file — it passed `test_committing_a_rewrite_does_not_hide_it`, which is a real rewrite. Forgiving per adjacent pair does not clear the repair either, because the restoring commit does not start with the tampered version.
Decision:     INV-8's history check compares the current content against one fixed baseline, the version at the file's first commit, exactly as INV-7 compares against the version at the commit that added the file. Restoring the baseline content clears it; leaving it rewritten keeps reporting it. The HEAD comparison for the uncommitted window is unchanged. (Agent-chosen during implementation, from options measured against the suite; Max's DEC-026 decision on the terminal state is unchanged and this only settles the mechanism.)
Rejected:     requiring every historical version to be a prefix (unsatisfiable after any repair, so it reintroduces the permanent-red defect); forgiving a version when a longer one is a prefix (measured: clears a genuine same-position rewrite); pairwise adjacent-version checks (measured: does not clear a correct repair); keeping the `--numstat` "a commit removed lines" rule (strongest detection, and the exact rule DEC-026 rejected for having no terminal state).
Consequences: detection is weaker than the rule it replaces, in one stated way, measured rather than assumed: a rewrite of text that was appended after the file's first commit is reported while uncommitted and not once committed. Verified in a throwaway repository — legitimate append exit 0, post-baseline rewrite uncommitted exit 1, the same rewrite committed exit 0, baseline rewrite committed exit 1. That gap is planned as S046 rather than left in a code comment. `git_blobs` batches the blob fetches into one `git cat-file --batch` so both invariants stay at two or three git processes per run.

## DEC-028  2026-08-07  INV-8 tracks a high-water mark of legitimate content
Tags:         invariants, immutability, git, decisions
Context:      DEC-027 settled INV-8 on one fixed baseline, the first committed version, and accepted a measured gap: a rewrite of text appended after that commit was reported while uncommitted and not once committed. S046 closed the gap and needed a rule satisfying both halves at once. Two more candidates were implemented and run. Comparing the current file against every past version, by line subsequence rather than prefix, catches the rewrite but still cannot pass after a repair — a rewrite introduces a line that the repair rightly discards, so the tampered version is not a subsequence of the corrected file either. Comparing against the longest past version misses a rewrite that lengthens the file, which is the common shape of an in-place edit.
Decision:     INV-8 walks the versions oldest first and maintains a high-water mark: a version that still contains, in order, every line the mark requires becomes the new mark, and a version that dropped something is a tampering and is skipped rather than becoming the mark. The file as it stands must then contain the mark's lines, in order. Restoring the text puts the mark back and clears the whole history at once; a removal, an in-place rewrite, and a line moved to the end are each caught, because in every one of them a required line is no longer in order. (Agent-chosen during implementation, from candidates measured against the suite.)
Rejected:     the fixed first-commit baseline of DEC-027, superseded here because it could not see a post-baseline rewrite; every-version subsequence without skipping (measured: `test_a_repair_of_post_baseline_text_clears_it` stayed red, because the tampered version holds a line the repair removed); comparing against the longest past version (measured earlier: clears a same-position rewrite that lengthens the file); returning to `--numstat`, which DEC-026 rejected for having no terminal state.
Consequences: DEC-027's accepted gap is closed and its mechanism sentence is superseded by this entry; DEC-027 stays as the record of why a fixed baseline was tried and what it cost. Re-measured in a throwaway repository against the same five states DEC-027 used: legitimate append exit 0, post-baseline rewrite uncommitted exit 1, the same rewrite committed exit 1 where it was 0, the repair exit 0, baseline rewrite committed exit 1. Two behaviours worth stating rather than discovering later: mid-file insertion is permitted, since only removal and reordering break a subsequence, and reordering entries is a violation until reversed — which is what DEC-013's authorised reorder would be today, and the case a waiver path would serve if one is ever built.

## DEC-029  2026-08-07  The Stop waiver counts retries within a turn, derived from the worklog rather than from an unobserved payload field
Tags:         hooks, stop, invariants, deadlock
Context:      the 2026-08-07 re-run found (.2-F01) that the deadlock waiver counted consecutive blocks per `prompt_id`, a Stop payload field nothing in this repository establishes exists. Every other hook field in `bin/moltke.py` carries a dated live observation and this one did not. When the key is absent the counter is global and persists on disk, so from the fourth blocked turn onward every Stop check — invariants, stale `status.md`, the recap gate, the README and MANUAL stamp — is waved through, and stays waved through across sessions. Two routes reach the empty key regardless of what Claude Code sends: `hook_input` returns `{}` on a parse error, which is deliberate fail-open, and again when stdin is a tty. Measured: eight turns read `2 2 2 0 0 0 0 0`, with `{"prompt_id": "", "count": 8}` on disk.
Decision:     the waiver counts retries within one turn, and "the same turn" is `prompt_id` and `session_id` when the payload carries them, plus the number of prompt headings in `adocs/worklog.md`, which `UserPromptSubmit` advances exactly once per turn. The count also resets when the set of problems changes, so making partial progress does not spend attempts. The waived turn prints the problems before allowing the stop. (Agent-chosen during implementation; the alternative was put to the same standard S016 set for `agent_type`.)
Rejected:     observing a live Stop payload and keying on `prompt_id` alone, the way S016 established `agent_type` (correct in spirit, but it needs instrumenting the installed plugin again for one field, and it would still fail open on both `hook_input` fallbacks — the redesign removes the dependency instead of confirming it); keying on the problem fingerprint alone (resets correctly on progress, but a repository broken the same way every turn would be waived from the fourth turn onward, which is the defect); removing the cap (INV-12 and DEC-006 require it, and a hook that blocks forever with an unactionable message is the deadlock it exists to prevent).
Consequences: the worklog is now load-bearing for a hook decision, which is new — it was forensic and never a context source (DEC-011), and this reads its shape rather than its content, but the coupling is real and worth knowing. A repository whose `UserPromptSubmit` is failing keeps a constant prompt count, so retries within what is really several turns share a key and the cap can fire early; that failure is itself reported at SessionStart since S014. `mode_stop` now reads stdin once and shares the payload, because two `hook_input()` calls in one process would give the second an empty dict.
