id:         S147
goal:       `--decline` leaves an already-declined marker untouched, as INV-11 says
accepts:    `--decline` on an already-declined repository leaves the marker byte-identical and says so, matching the left-untouched message --scaffold prints; red observed first
touches:    bin/moltke.py mode_decline
excludes:   changing what --decline writes on a first run
decisions:
closes:     2026-08-19_adversarial-F07
blocks:
paused_by:
done:      2026-08-19 A declined marker is now the first thing mode_decline checks, and it returns there: INV-11 says both setup modes leave a declined repository untouched, and this one rewrote the marker down to its two keys, discarding a note saying why the repository declined or configuration a later enabled:true would have restored. The left-untouched message is one function both modes call, so "says what --scaffold says" is structural rather than two copies of a sentence that can drift. The refusal below it is unchanged: an enabled marker is still exit 1 on stderr. Closes 2026-08-19_adversarial-F07. Red observed first on both reproductions, the third test anchoring non-vacuity by proving a first --decline still writes. specs' surface row and MANUAL's mode row state the behaviour; README needed only its test count, 476 to 479.
author:    Maksym Bodnar
