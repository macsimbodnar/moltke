id:         S117
goal:       the decisions index matches the entries, newest last
accepts:    decisions.md's index has one line per entry (44 today), the body is
            ordered oldest to newest, and DEC-043/DEC-044 appear in both. Doc
            edit; --validate green before and after, INV-9 unchanged.
touches:    adocs/decisions.md
excludes:   any enforcement of index-body agreement, which stays a habit
decisions:
closes:     2026-08-11_adversarial-F06
blocks:
paused_by:
done:      2026-08-11: the decisions index matches the entries, closing 2026-08-11_adversarial-F06. DEC-043 and DEC-044 were appended by S108/S109 without index lines and in commit order rather than id order; the index is rebuilt from the body itself — one line per entry, 44 for 44 — and the body reordered oldest to newest. Doc edit, no code; --validate and --audit list exit 0 before and after, INV-9 unchanged. Suite 453 OK, --validate green. README and MANUAL checked, no change.
