id:         S163
goal:       give this machine its second Claude config root and put 1.0.0 in it
accepts:    a second root exists alongside the default one and is signed in to
            the account it is meant for; moltke 1.0.0 is installed there and
            `CLAUDE_CONFIG_DIR=<root> claude plugin list` reports it enabled
touches:    the machine's Claude configuration, not the repository
excludes:   any product change; recording in this repository which root is
            which or which account it carries (DEC-065)
author:
done:
