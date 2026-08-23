# This machine

Machine-local instructions for agents working in this repository. This file
stays out of git (`.moltke.local.md` is in `.gitignore`) and is read during
the Orient step of `AGENTS.md` — so keep it small: every line here is paid
for in every session.

What belongs here is what is true on this machine only and would be wrong or
meaningless on another:

- tools and their paths (`stockfish is /opt/homebrew/bin/stockfish`)
- platform directives (`on this mac, keep the engine alive between runs`)
- local credentials locations by *reference*, never the secrets themselves

What does not belong here: anything a teammate's machine also needs — that is
project state and goes in the tracked files.

Delete this guidance once you have real content.
