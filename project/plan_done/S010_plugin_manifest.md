id:         S010
goal:       plugin manifest, marketplace entry, install verification on a second machine
accepts:    2026-08-01 narrowed by DEC-019 to what needs no environment change: .claude-plugin/plugin.json carries an explicit version field; the marketplace entry resolves to this plugin; skills are laid out so they resolve as /moltke:name; hooks reference ${CLAUDE_PLUGIN_ROOT}; `claude plugin validate --strict` passes on both manifests. Installing, live hook firing, second machine, and the DEC-002 push confirmation are S012, owned by Max
touches:    .claude-plugin/, marketplace entry
decisions:  DEC-001, DEC-002
done:      2026-08-01 suite green 110/110 (1 skipped); claude plugin validate --strict passes; scope narrowed by DEC-019; README and MANUAL checked, absent by plan (S011)
