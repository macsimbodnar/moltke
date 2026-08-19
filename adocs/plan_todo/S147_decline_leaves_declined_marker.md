id:         S147
goal:       `--decline` leaves an already-declined marker untouched, as INV-11 says
accepts:    `--decline` on an already-declined repository leaves the marker byte-identical and says so, matching the left-untouched message --scaffold prints; red observed first
touches:    bin/moltke.py mode_decline
excludes:   changing what --decline writes on a first run
decisions:
closes:     2026-08-19_adversarial-F07
blocks:
paused_by:
done:
