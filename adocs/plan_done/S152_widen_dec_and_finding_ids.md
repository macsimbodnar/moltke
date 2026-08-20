id:         S152
goal:       DEC and finding id scanners are not blind past their width, and AGENTS.md 5's lint claim is enforced or dropped
accepts:    the DEC and finding id scanners read ids at any width, or an unreadable id is a reported violation rather than a silently skipped line; the dead git_dir at :1013 and the doubled assignment are gone; AGENTS.md section 5 either names a linter the completion gate runs or drops the word lint, with templates/AGENTS.md following; red observed first
touches:    bin/moltke.py DEC and finding id patterns, AGENTS.md, templates/AGENTS.md
excludes:   renumbering any existing DEC or finding id
decisions:  DEC-060
closes:     2026-08-19_adversarial-F12
blocks:
paused_by:
done:      Two scanners still read a fixed width unanchored on the right, the shape S136's own
            comment calls worse than blind: `\d{3}\b` does not truncate DEC-1000, it skips the
            line whole, so INV-9 abstained on a duplicate; the same for a hundredth finding in
            one report, invisible to INV-10 and --audit list alike. Neither id has an allocator
            that could refuse at a ceiling, both being written by hand, so the fix is that no
            width is unreadable: DEC_ID_DIGITS and FINDING_ID_DIGITS state each floor once, with
            no top, and every fullmatch that spelled the width inline reads them.
            The other half of never silently skipped: a `## DEC-` heading that is not an id is
            now an INV-9 violation naming it, so a width below the form fails as loudly as one
            above it. An ordinary decisions.md is unaffected, which is the anchor.
            The dead `def git_dir(root):    return lines`, shadowed three lines later, and the
            doubled REVIEWER_AGENT assignment are gone; the audit's ast walk reported both
            against HEAD and reports none now. Nothing guards against the next one, by decision:
            AGENTS.md 5 and templates/AGENTS.md drop the word lint rather than gaining a linter
            (DEC-060, Max's call from three options). A rule nothing enforces reads as a gate at
            every review and is one at none.
            506 green, --validate clean. specs' INV-9 and the reviewer agent's id format state
            the widths; README and MANUAL checked, neither states either width.
author:    Maksym Bodnar
