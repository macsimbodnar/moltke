id:         S179
goal:       the 0.x archive branch exists somewhere real, or the claim goes
accepts:    either watch-primitive-a304293 is pushed to origin from wherever
            it lives (user action — it is in no reachable clone: origin
            holds only master and v1, checked 2026-08-30 via the GitHub
            API), or status.md's parked note and a decision record that the
            pre-merge tip is gone
touches:    git refs on origin, or adocs/status.md and adocs/decisions.md
excludes:   recreating the branch content from history
closes:     2026-08-29_adversarial.3-F06
author:     Maksym Bodnar
done:       2026-08-30: the claim goes. Re-verified before writing: origin
            holds only master and v1 (GitHub API), and this clone has no
            watch-primitive ref, no object a304293, and no reflog trace —
            nothing to push from anywhere. DEC-070 records the loss and
            supersedes DEC-052's archive claim on that point; status.md's
            parked note now says the tip is lost and where the unmerged
            line's record lives (plan_done/, the audit reports, DEC-052).
            README and MANUAL unchanged, checked. No suite, per the TESTS
            rule.
