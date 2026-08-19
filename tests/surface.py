"""The guarded public surface, declared once and read by the golden and by the
plugin tests (S023, DEC-010).

`surface_guard` is `cli`, but the surface a user of the *plugin* touches is wider
than argparse: three skills, five hook events, and the marker keys. Those are the
components most likely to drift from the documentation, and until S023 the golden
covered none of them — a fourth skill was invisible and deleting the `Stop` hook
left the suite green.
"""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("moltke", REPO / "bin" / "moltke.py")
moltke = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(moltke)


def declared_skills():
    """Skill names as the plugin declares them: the `name:` in each frontmatter,
    not the directory name, because that is what `/moltke:<name>` resolves."""
    names = []
    for skill in sorted((REPO / "skills").glob("*/SKILL.md")):
        for line in skill.read_text(encoding="utf-8").splitlines():
            if line.startswith("name:"):
                names.append(line.split(":", 1)[1].strip())
                break
    return sorted(names)


def declared_hook_events():
    hooks = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    return sorted(hooks.get("hooks", {}))


def declared_hook_wiring():
    """One triple per declared hook command: `(event, tool matcher, mode flag)`.

    The event set alone left every connection between the plugin and the code
    unguarded (S142, F02): the `Write|Edit` matcher could be deleted and `Stop`
    repointed at `--roadmap` with the suite green. An absent matcher is reported
    as `*`, because "fires for every tool" is itself part of the wiring — adding
    a matcher would narrow it. A command with no mode flag reads `(no mode)`
    rather than being skipped, so unwiring one cannot shrink the golden quietly.
    """
    hooks = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    triples = []
    for event, matchers in sorted(hooks.get("hooks", {}).items()):
        for matcher in matchers:
            for entry in matcher.get("hooks", []):
                flags = [token for token in entry.get("command", "").split()
                         if token.startswith("--")]
                triples.append((event, matcher.get("matcher", "*"),
                                flags[0] if flags else "(no mode)"))
    return triples


def cli_lines():
    """One line per option: its flags, its argument shape, and its operations.

    Reads argparse's actions rather than --help text, so wording changes do not
    churn the golden but a rename or a new flag does.
    """
    lines = []
    for action in moltke.build_parser()._actions:
        if not action.option_strings:
            continue
        flags = "/".join(sorted(action.option_strings))
        if action.nargs == 0:
            shape = ""
        elif action.nargs == "?":
            shape = f"[{action.metavar or 'VALUE'}]"
        elif action.nargs in ("+", "*"):
            shape = f"{action.metavar or 'VALUE'}..."
        else:
            shape = action.metavar or "VALUE"
        ops = ""
        if flags == "--step":
            ops = "  ops: " + ",".join(sorted(moltke.STEP_OPS))
        elif flags == "--audit":
            ops = "  ops: " + ",".join(sorted(moltke.AUDIT_OPS))
        lines.append(f"{flags} {shape}".rstrip() + ops)
    return lines


def current_surface():
    lines = cli_lines()
    lines.append("hooks: " + ",".join(declared_hook_events()))
    for event, matcher, mode in declared_hook_wiring():
        lines.append(f"hook {event} {matcher} -> {mode}")
    lines.append("marker keys: " + ",".join(sorted(moltke.MARKER_KEYS)))
    lines.append("skills: " + ",".join(declared_skills()))
    return "\n".join(sorted(lines)) + "\n"
