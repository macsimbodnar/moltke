id:         S171
goal:       release 1.1.0 — the audit fixes ship, tagged
accepts:    plugin.json says 1.1.0; the release commit carries an annotated
            tag v1.1.0; plan.md and status.md state the true plan state at
            completion; Max pushes commits and tag; each config root present
            takes the update once master carries it
touches:    .claude-plugin/plugin.json, git tags, plan.md, status.md
excludes:   any product change beyond the version field
closes:     2026-08-29_adversarial.2-F01
paused_by:  S173
author:     Maksym Bodnar
done:
