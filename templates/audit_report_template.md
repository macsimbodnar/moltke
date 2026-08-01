# Audit YYYY-MM-DD type

Scope: what was examined, at which commit.
Method: how it was examined. Audits run against the code, not the specs.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Every finding needs a `Status:` line reading `open`, `planned`, `closed`, or
`accepted`. An open finding must end up either in a plan step whose `closes:`
field names it, or in a decision entry stating why it will not be acted on.
A finding moves to `closed` only after the audit is re-run and no longer
reports it.

### YYYY-MM-DD_type-F01  <severity>  short title

Status: open

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
