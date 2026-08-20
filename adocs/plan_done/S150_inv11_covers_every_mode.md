id:         S150
goal:       INV-11's marker-gate test derives its mode list from the parser, with a named exempt set
accepts:    the INV-11 marker-gate test derives its mode list from build_parser() and names an explicit exempt set, so adding a mode without exempting it fails; specs.md INV-11 lists the same exemptions; red observed first against today's six-of-thirteen coverage
touches:    the INV-11 test, tests/surface.py if the derivation is shared, specs.md INV-11 wording
excludes:   changing which modes are actually exempt from the marker gate
decisions:
closes:     2026-08-19_adversarial-F10
blocks:
paused_by:
done:      INV-11's every-mode test derived nothing: ALL_MODES was a hand-written six of the
            thirteen modes the parser declares, so --pre-command, --roadmap, --step and --audit
            were gated only by the code happening to be right. Proven by returning EXIT_BLOCK for
            --audit ahead of the gate when find_root() is None: all 489 tests stayed green, and
            the rewritten test failed on it.
            Both loops now read gated_modes(), built from surface.declared_modes() off
            build_parser()'s mutually exclusive group minus a named GATE_EXEMPT of --version,
            --scaffold, --decline and --watch, each carrying its reason. A mode added without a
            decision about it lands in the gated list and has to exit 0; an exemption has to be
            written down to exist. A third test keeps the derivation honest — --validate and
            --session-start must be in it, every exempt and every armed flag must be declared,
            and gated plus exempt must account for every mode — so a derivation that quietly
            returned nothing cannot pass as all of them.
            specs' INV-11 named two of the four exemptions and MANUAL three; both now name four.
            Six of thirteen becomes nine gated plus four exempt. 490 green, --validate clean,
            README checked and unchanged: the golden reads current_surface(), which declared_modes
            does not enter.
author:    Maksym Bodnar
