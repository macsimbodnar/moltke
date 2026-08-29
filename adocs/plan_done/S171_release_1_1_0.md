id:         S171
goal:       release 1.1.0 — the audit fixes ship, tagged
accepts:    plugin.json says 1.1.0; the release commit carries an annotated
            tag v1.1.0; plan.md and status.md state the true plan state at
            completion; Max pushes commits and tag; each config root present
            takes the update once master carries it
touches:    .claude-plugin/plugin.json, git tags, plan.md, status.md
excludes:   any product change beyond the version field
closes:     2026-08-29_adversarial.2-F01
author:     Maksym Bodnar
done:       2026-08-29: plugin.json says 1.1.0 (bumped in e52b91d) and the
            annotated tag v1.1.0 sits on this completion commit — the last
            commit of the release, so the tag carries S164-S170 and the .2
            re-run's S172/S173 with all fast-check fixes. The tag was first
            cut on e52b91d and moved here before any push, because the .2
            re-run surfaced two lows worth shipping in the same release;
            paused_by tracked S172 then S173 while they landed. plan.md and
            status.md state the true plan state, which closes .2-F01. Max
            pushes commits and the tag (git push --follow-tags); the config
            root updates after that. No suite, per the TESTS rule.
