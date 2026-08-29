id:         S170
goal:       README's Ship order commits the version bump before the push
accepts:    the Ship list reads bump, commit, push — so step 4's plugin update
            sees the new version; no other Ship semantics change
touches:    README.md
excludes:   the release mechanics themselves
closes:     2026-08-29_adversarial-F07
author:     Maksym Bodnar
done:       2026-08-29: the Ship list reads bump, commit, push — the bump
            commit named as the release commit, so the push carries the new
            version and step 4's update sees it. Verified by re-reading the
            list against the release mechanics MANUAL states (updates
            compare version and nothing else): no order now exists in which
            the push precedes the bump. MANUAL unchanged, checked. No
            suite, per the TESTS rule.
