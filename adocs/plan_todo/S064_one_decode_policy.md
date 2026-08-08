id:         S064
goal:       one decode policy for every file moltke reads
accepts:    every read of a repository file uses the same decode policy, so one non-UTF-8 byte cannot turn --validate, --post-write, --stop, --session-start, --step, or --audit list into a traceback; INV-14's two halves stop disagreeing about the same file, which is the clearest instance; the policy is stated once in specs rather than repeated per call site, and a single helper is what enforces it; red observed by planting one invalid byte and watching each mode raise
touches:    bin/moltke.py, every read_text and read_bytes call site; tests, wherever the shared reader needs pinning
excludes:   changing what any check concludes about well-formed files
decisions:
closes:     2026-08-08_adversarial-F05
blocks:
paused_by:
done:
