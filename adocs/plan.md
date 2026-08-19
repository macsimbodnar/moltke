# Plan

Build the `moltke` Claude Code plugin: a document-driven development workflow
giving an agent durable, cross-session, cross-tool memory of a project,
distributed as a git repository plus a plugin marketplace entry, enforced by
hooks in marked repositories. Spec: `adocs/specs.md`.

This repository self-hosts the workflow (DEC-012). The first step was worked by
hand; from the second onward the workflow enforces itself.

Order lives here and nowhere else (DEC-008). Step detail lives in the step files.

Two branches diverged at the adocs rename and were merged 2026-08-18 (DEC-052).
The watcher primitive and its arm-time lint arrive from the local branch with
new ids, since the ids they were minted under mean other work here. Three of the
six 2026-08-18 findings did not survive re-triage against this code (DEC-053).
Step ids belong in the numbered list below and nowhere else in this file: the
derived next step is the first id in document order, so an id mentioned in prose
above the list becomes the next step instead.

The 2026-08-19 adversarial run against the merged tree produced thirteen
findings — one high, four medium, eight low — and each has its own step below,
one to one. The list is ordered severity first: correctness ahead of politeness,
which is why the audit's own steps sit in front of everything it did not raise.
That run's verdicts closed three of the 2026-08-18 findings and left the other
three accepted.

139. S144  `--audit check` reports the source a staged rename into tests/ removed
140. S145  an out-of-range or non-positive --pid is refused at parse time, never a traceback
141. S146  MOLTKE_UNBOUNDED_OK covers the persistent-arm rule only, never the follow refusal
142. S147  `--decline` leaves an already-declined marker untouched, as INV-11 says
143. S148  the audit skill stops documenting the removed worklog and --log-prompt
144. S149  a multi-line --stamp round-trips, or a blank line in one is refused
145. S150  INV-11's marker-gate test derives its mode list from the parser, with a named exempt set
146. S151  the reviewer fence refuses overwriting another report and permits correcting its own new test
147. S152  DEC and finding id scanners are not blind past their width, and AGENTS.md 5's lint claim is enforced or dropped
148. S153  the self-host checks name what they check, and the audit commit shape is stated
149. S154  the lifecycle can undo a claim, returning a step to plan_todo/ without a by-hand move
150. S155  release 0.13.0 and reinstall it in both config roots
151. S156  testing.md's header says what the tool does to it: rows leave with their plan entry, so "Append only" reads as write discipline, not as nothing is ever removed
