id:         S064
goal:       one decode policy for every file moltke reads
accepts:    every read of a repository file uses the same decode policy, so one non-UTF-8 byte cannot turn --validate, --post-write, --stop, --session-start, --step, or --audit list into a traceback; INV-14's two halves stop disagreeing about the same file, which is the clearest instance; the policy is stated once in specs rather than repeated per call site, and a single helper is what enforces it; red observed by planting one invalid byte and watching each mode raise
touches:    bin/moltke.py, every read_text and read_bytes call site; tests, wherever the shared reader needs pinning
excludes:   changing what any check concludes about well-formed files
decisions:
closes:     2026-08-08_adversarial-F05
blocks:
paused_by:
done:      2026-08-08: every repository file goes through read_file, which decodes UTF-8 and replaces what it cannot; 23 call sites rewritten and one real read_text left, inside the helper. Thirteen readers decoded strictly and six replaced, and INV-14's two halves disagreed about the same file, so one latin-1 byte in a pasted capture turned every mode into a traceback — and --session-start producing no JSON silences the channel S014 depends on. Replacing rather than raising is the deliberate half: moltke reads files it did not write and must keep reporting on them. S063 had already made the strip_guidance readers tolerant, so the red is measured on the ones it did not touch: a step file, testing.md, status.md. 4 tests, red observed across three files and five modes. Suite 306 OK, --validate green. README test count 302 to 306; MANUAL needed no change, since the policy is invisible when files are well formed; specs gained a dated note.
