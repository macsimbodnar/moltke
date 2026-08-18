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

126. S128  bump 0.11.0 and ship the batch
127. S129  watch primitive: a self-terminating four-exit watcher with registration
128. S130  arm-time watcher lint and watch-state reporting in hooks
129. S140  a watcher killed in its arm window still records an outcome
130. S137  decide whether arm-time watcher enforcement survives the fence retirement
131. S132  bound each `--watch` scan so the ceiling holds against a runaway regex
132. S134  the primitive must be the executed command, not a substring anywhere in it
133. S136  step ids past 999: recognised everywhere, or allocation refused loudly
134. S138  re-run the adversarial audit against the merged tree
135. S139  install and verify 0.12.0, the merged plugin
