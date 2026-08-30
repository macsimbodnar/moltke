id:         S177
goal:       the Ship order includes the release tag
accepts:    README's Ship list tags the release commit (annotated
            v<version>) and pushes commits and tag together; MANUAL agrees
            where it describes updating
touches:    README.md; MANUAL.md if needed
excludes:   retroactive tags for released versions before 1.1.0
closes:     2026-08-29_adversarial.3-F05
author:     Maksym Bodnar
done:       2026-08-30: README's Ship order gains a tag step — annotated
            v<version> on the release commit after every release-bound
            change has landed, per DEC-069 — and the push becomes
            git push --follow-tags so commits and tag travel together.
            Verified by re-reading the Ship section: the next release
            following it produces and publishes the tag. MANUAL checked
            where it describes updating (version-bump gating): nothing
            there contradicts tagging, unchanged. No suite, per the TESTS
            rule.
