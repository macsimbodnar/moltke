id:         S169
goal:       MANUAL discloses that an install ships this repository whole
accepts:    the DEC-020 condition holds again: a Known-limits line says an
            install carries the full repository including adocs/ history, and
            roughly what that weighs; the plugin/ escape hatch stays parked
touches:    MANUAL.md
excludes:   restructuring the tree (the DEC-020 escape hatch)
closes:     2026-08-29_adversarial-F06
author:     Maksym Bodnar
done:       2026-08-29: MANUAL's Known limits carries the disclosure again —
            an install ships the repository whole, adocs/ history is most of
            the ~1 MB, cached per root and per version, DEC-020 named and
            the plugin/ escape hatch still parked. Verified against the real
            1.0.0 cache measured this session (1.2M total, 1.1M adocs/).
            README unchanged, checked. No suite, per the TESTS rule.
