# This machine

Machine-local instructions for agents working in this repository. moltke
created this file, keeps it out of git via `.git/info/exclude`, and injects
its content into every session's context — so keep it small: every line here
is paid for in every session.

What belongs here is what is true on this machine only and would be wrong or
meaningless on another:

- tools and their paths (`stockfish is /opt/homebrew/bin/stockfish`)
- platform directives (`on this mac, keep the engine alive between runs`)
- local credentials locations by *reference*, never the secrets themselves

What does not belong here: anything a teammate's machine also needs — that is
project state and goes in the tracked files.

Delete this guidance once you have real content.
