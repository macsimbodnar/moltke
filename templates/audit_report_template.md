# Audit YYYY-MM-DD <type>

Scope: what was examined, at which commit.
Method: how it was examined. Audits run against the code, not against the specs.
An audit that only confirms the documentation is a documentation review.

Written before any fix. A report edited while fixing stops being evidence of
what was found.

Finding format. Every finding carries a status of `open`, `planned`, `closed`,
or `accepted`, and an id prefixed with this report's own name:

```
### YYYY-MM-DD_type-F01  high  short title

Status: open

Evidence: file and line, or the command and its output.
Impact: what breaks, for whom, under what conditions.
Suggested resolution: what would close it. Not applied here.
```

Every finding ends in one of two places: a plan step whose `closes:` field
names it, or a decision entry stating why it will not be acted on, which moves
it to `accepted`. A finding moves to `closed` only after the audit is re-run
and no longer reports it. Fixing without re-running leaves it `planned`.

## Findings

<!-- Append findings here, most severe first. A report with no findings is a
     valid result: say so explicitly rather than leaving this empty. -->
