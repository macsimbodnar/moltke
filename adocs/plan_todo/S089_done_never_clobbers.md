id:         S089
goal:       --step done and --step start refuse when the destination file already exists
accepts:    With the same step id present in plan_current/ and plan_done/,
            --step done refuses on stderr with exit 1, names the duplicate id and
            INV-6, and leaves the plan_done/ file byte-identical.
            --step start refuses the same way when the target name already exists
            in plan_current/.
            Both checks run before anything is written, as S070 established for
            writability.
            A test asserts the plan_done/ body and its original done: stamp survive
            a --step done on a duplicate id; it fails without the fix.
touches:    bin/moltke.py step_done (destination write), step_start (path.rename);
            tests/test_s0nn_step_*.py
excludes:   changing INV-6, changing locate_step's search order, or resolving the
            duplicate automatically.
decisions:
closes:     2026-08-08_adversarial.4-F02
blocks:
paused_by:
done:
