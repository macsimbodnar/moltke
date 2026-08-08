id:         S058
goal:       bump 0.5.0, re-run the audit, close the findings it no longer reports
accepts:    .claude-plugin/plugin.json reads 0.5.0 and the golden plugin test still passes; a fresh adversarial audit runs against the code at that commit through the adversarial_reviewer subagent, with --audit check clean before anything is acted on; every 2026-08-07_adversarial.2 finding the re-run no longer reports moves to closed in its own report, and 2026-08-07_adversarial-F02 with it, since S049 closed the half S033 left; a finding the re-run still reports stays open and gets a step or a decision rather than a closed stamp; new findings are triaged one step each, correctness defects ordered ahead of feature work; MANUAL's version-attributed sentences that read "up to and including 0.4.0" are corrected to name 0.5.0 as the release that carries the fix
touches:    .claude-plugin/plugin.json; adocs/audit/; adocs/plan.md and new step files; MANUAL.md; adocs/status.md
excludes:   reinstalling the plugin and verifying hooks live, which is S059; fixing anything the re-run finds, which is the triaged steps' job — the report is written before any fix
decisions:  DEC-034
closes:
blocks:
paused_by:
done:
