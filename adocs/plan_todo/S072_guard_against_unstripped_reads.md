id:         S072
goal:       the structural guard against an unguarded scanner can fire again
accepts:    the S063 structural guard fires again: it looked for strip_guidance beside read_text, and S064 banned read_text everywhere, so a new scanner written the mandated way reads an unguarded file with the suite green; whatever replaces it is checked by adding such a consumer and watching the suite go red; red observed by doing exactly that
touches:    tests/test_s033_fences.py; bin/moltke.py if the guard needs a hook to check against
excludes:   reverting either S063 or S064
decisions:  
closes:     2026-08-08_adversarial.2-F06
blocks:
paused_by:
done:
