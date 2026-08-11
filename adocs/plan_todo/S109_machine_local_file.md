id:         S109
goal:       a machine-local instructions file that the tool creates and injects
accepts:    In a marked, enabled repository, --session-start creates
            .moltke.local.md at the marked root from a shipped template when it is
            absent, appends ".moltke.local.md" to .git/info/exclude when a git
            repository is present and the line is missing, and injects the file's
            content into the SessionStart additionalContext. All three are
            idempotent: a second run creates nothing, appends nothing, and an
            existing file is never overwritten.
            In an unmarked or declined repository --session-start creates nothing
            and stays exit 0, which is INV-11 and gets its own test.
            Without git the file is still created and injected and the exclusion
            is skipped without an error.
            The template says what belongs there — machine-specific tools, paths,
            directives — that it is not committed, and to keep it small because
            its content enters every session's context.
            MANUAL.md documents the file; AGENTS.md §2 gains its row.
            Tests: creation, injection, idempotence, never-overwrite, INV-11
            silence, no-git fallback; red observed before the implementation.
touches:    bin/moltke.py (--session-start); templates/moltke_local.md;
            tests/test_s005_hooks.py; MANUAL.md; AGENTS.md §2;
            templates/AGENTS.md; adocs/decisions.md (DEC-043)
excludes:   committing the file anywhere; a size cap or truncation, which is the
            user's discipline and the template says so; --scaffold involvement
decisions:  DEC-043
closes:
blocks:
paused_by:
done:
