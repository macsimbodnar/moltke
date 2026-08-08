id:         S081
goal:       every git-derived check works when the marked root is below the git top level
accepts:    a marked repository whose root is below the git top level is either supported or refused, not silently broken: git prints top-level-relative paths and nothing checks the two roots agree, so INV-8 abstains on real tampering, INV-7 reports a present file as gone with a remedy that cannot run, --audit check lists its own report as unexpected, the recap gate treats adocs/ as source, and the stamp gate can never fire; whichever is chosen is stated in specs with the case it does not cover; red observed with a marked directory inside a git repository whose root is above it
touches:    bin/moltke.py find_root, git_dir, and every relative-path comparison against git output; tests
excludes:   supporting several marked repositories inside one git repository, which is a different feature
decisions:  
closes:     2026-08-08_adversarial.3-F02
blocks:
paused_by:
done:
