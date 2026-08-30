id:         S180
goal:       release 1.1.1 — the .3 re-run fixes ship, tagged
accepts:    plugin.json says 1.1.1; the release commit carries an annotated
            tag v1.1.1; plan.md and status.md state the true plan state at
            completion; Max pushes commits and tag; each config root present
            takes the update once master carries it
touches:    .claude-plugin/plugin.json, git tags, plan.md, status.md
excludes:   any product change beyond the version field
closes:
author:     Maksym Bodnar
done:       2026-08-30: plugin.json says 1.1.1 and the annotated tag v1.1.1
            sits on this completion commit — the release commit per the
            README Ship order, carrying the .3 re-run round S174-S179.
            First release to follow the S177-amended Ship order (tag cut
            before any push, pushed with --follow-tags). plan.md and
            status.md state the true plan state. Max pushes commits and the
            tag (git push --follow-tags); each config root updates after
            that. README and MANUAL checked: no version strings, Ship order
            already current. No suite, per the TESTS rule.
