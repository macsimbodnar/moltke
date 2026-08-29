id:         S161
goal:       release 1.0.0 to the config roots
accepts:    master carries the v1 tree at version 1.0.0; Max has pushed; every
            Claude config root present on the machine serves 1.0.0 at every
            scope it holds an install for
touches:    git (merge v1 into master), the installed plugin registries
excludes:   any product change
author:     Maksym Bodnar
done:       2026-08-29: master carries the v1 tree at 1.0.0. The branch was
            squash-merged through GitHub as `bc78bfc`, one commit with one
            parent, so the nine per-step commits stay on `v1` while master's
            tree is byte-identical to it; Max chose to record nothing about
            that. The one Claude config root present on this machine took the
            release at user scope: marketplace refreshed to `bc78bfc`, then
            `claude plugin update moltke@moltke` moved 0.13.0 -> 1.0.0, and
            the registry now names the 1.0.0 cache at that commit. Verified
            by reading the installed cache rather than a version string: three
            skills (audit, init, rules), no bin/, no hooks/, no tests/, and a
            recursive diff against the checkout clean apart from the `.in_use`
            marker. Two deviations. The accepts named two roots and three
            scopes; only one root exists here now, so it was amended mid-step
            and the machine-local detail was scrubbed out of the living
            documents in the same step (73cbe3d, DEC-065). And `git fetch
            origin` fails in this environment — the ssh-agent holds no
            identity — so master was fetched over anonymous HTTPS instead;
            nothing was pushed. The second root Max wants on this machine
            needs him to sign in, so it is S163 rather than part of this step.
            README and MANUAL describe install generically and needed no
            change. No suite, per the TESTS rule.
