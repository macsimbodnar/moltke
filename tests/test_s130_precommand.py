"""S130: arm-time watcher lint (--pre-command, INV-17) and watch-state
reporting (DEC-049, DEC-051).

The lint payload shapes mirror the live Monitor tool schema, verified
2026-08-18: tool_input carries `command` (absent on ws arms) and a required
`persistent` boolean; non-persistent arms are bounded by a 1h timeout cap.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fixtures import workflow_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"
HOOKS = Path(__file__).resolve().parent.parent / "hooks" / "hooks.json"

CHESSO_FORM = 'tail -f /tmp/chesso_rating.log | grep -E --line-buffered "RATING-RUN-DONE|RATING-RUN-FAILED"'
PRIMITIVE_FORM = ("python3 ${CLAUDE_PLUGIN_ROOT}/bin/moltke.py --watch run.log "
                  "'RUN-(DONE|FAILED)' --ceiling 8h --pid 4242")


def run_moltke(cwd, *args, stdin=""):
    return subprocess.run(
        [sys.executable, str(MOLTKE), *args],
        cwd=cwd, capture_output=True, text=True, input=stdin,
    )


def monitor_arm(command=None, persistent=True, **extra):
    tool_input = dict(extra)
    tool_input["persistent"] = persistent
    if command is not None:
        tool_input["command"] = command
    return json.dumps({"tool_name": "Monitor", "tool_input": tool_input})


def git_baseline(root):
    for args in (("init", "-q"), ("add", "-A"), ("commit", "-qm", "base")):
        subprocess.run(
            ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
            capture_output=True, text=True, check=True,
        )


def write_record(root, name="1_1.json", **fields):
    directory = Path(root) / ".git" / "moltke_watch"
    directory.mkdir(parents=True, exist_ok=True)
    record = {"schema": 1, "log": "/tmp/run.log", "regex": "RUN-DONE",
              "ceiling": "8h", "armed_at": "2026-08-18T02:00:00+02:00",
              "watcher_pid": os.getpid()}
    record.update(fields)
    path = directory / name
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return path


def dead_pid():
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait(timeout=10)
    return proc.pid


class TestPreCommandLint(unittest.TestCase):
    """INV-17 at arm time: the leaked-monitor class is unarmable."""

    def test_persistent_tail_grep_is_blocked_with_the_primitive_named(self):
        # The exact chesso failure: unbounded follow, persistent, no exit.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command",
                                stdin=monitor_arm(CHESSO_FORM, persistent=True))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("--watch", result.stderr)
            self.assertIn("MOLTKE_UNBOUNDED_OK", result.stderr)

    def test_single_match_follow_is_blocked_even_when_bounded(self):
        # tail -f | grep -m1 looks like a fix and is not: SIGPIPE never comes.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "tail -f run.log | grep -m 1 DONE", persistent=False))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("SIGPIPE", result.stderr)

    def test_persistent_primitive_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command",
                                stdin=monitor_arm(PRIMITIVE_FORM, persistent=True))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_primitive_without_an_interpreter_is_allowed(self):
        # The primitive is the executable itself as often as it is an argument.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "bin/moltke.py --watch run.log 'RUN-(DONE|FAILED)' --ceiling 8h",
                persistent=True))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_primitive_inside_bash_c_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "bash -c 'python3 bin/moltke.py --watch run.log RUN-DONE --ceiling 8h'",
                persistent=True))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_comment_mentioning_the_primitive_does_not_arm_a_leak(self):
        # 2026-08-18_adversarial-F04: the substring test made a comment an
        # undocumented second escape hatch, one an agent trips by accident.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "tail -f run.log | grep BOOM  # prefer moltke.py --watch here",
                persistent=True))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("--watch", result.stderr)

    def test_echoing_the_primitive_before_a_leak_does_not_arm_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "echo moltke --watch ; tail -f run.log | grep BOOM", persistent=True))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("--watch", result.stderr)

    def test_the_primitive_trailed_by_a_leak_does_not_arm_it(self):
        # The mirror image: the primitive really is executed, and so is the leak.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                PRIMITIVE_FORM + " ; tail -f run.log | grep BOOM", persistent=True))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_a_comment_mentioning_the_primitive_still_honours_the_token(self):
        # MOLTKE_UNBOUNDED_OK stays the one escape, and it lives in a comment.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "tail -f dev.log | grep ERROR  # MOLTKE_UNBOUNDED_OK, and see moltke --watch",
                persistent=True))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_an_unparseable_command_is_refused_rather_than_waved_through(self):
        # A wrong block is loud, a wrong pass is silent (the S016 direction).
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "moltke.py --watch run.log 'unbalanced", persistent=True))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_bounded_stream_is_allowed(self):
        # Monitor's own documented per-occurrence use; the 1h cap bounds it.
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "tail -f dev.log | grep --line-buffered ERROR", persistent=False))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_token_allows_a_deliberate_unbounded_stream(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                "tail -f dev.log | grep --line-buffered ERROR  # MOLTKE_UNBOUNDED_OK dev errors",
                persistent=True))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_ws_arm_without_command_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            result = run_moltke(root, "--pre-command", stdin=monitor_arm(
                None, persistent=True, ws={"url": "wss://x.example/stream"}))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_other_tools_are_not_this_lints_business(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            payload = json.dumps({"tool_name": "Bash",
                                  "tool_input": {"command": CHESSO_FORM}})
            result = run_moltke(root, "--pre-command", stdin=payload)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_unmarked_repo_feels_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_moltke(tmp, "--pre-command",
                                stdin=monitor_arm(CHESSO_FORM, persistent=True))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_hooks_wire_the_monitor_matcher(self):
        config = json.loads(HOOKS.read_text(encoding="utf-8"))
        entries = config["hooks"]["PreToolUse"]
        monitor = [e for e in entries if e.get("matcher") == "Monitor"]
        self.assertEqual(len(monitor), 1, entries)
        self.assertIn("--pre-command", monitor[0]["hooks"][0]["command"])


class TestWatchReporting(unittest.TestCase):
    """A watch is filesystem state: session start surfaces it, stop refuses
    to end a turn on a lost or unacknowledged obligation."""

    def test_session_start_lists_a_live_watch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            write_record(root)  # watcher_pid is this test: alive
            result = run_moltke(root, "--session-start")
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("watching", context)
            self.assertIn("RUN-DONE", context)

    def test_session_start_flags_an_unacknowledged_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            write_record(root, outcome="success marker", exit_code=0)
            result = run_moltke(root, "--session-start")
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("unacknowledged", context)

    def test_stop_blocks_on_an_unacknowledged_outcome_until_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            record = write_record(root, outcome="ceiling", exit_code=124)
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn(record.name, result.stderr)
            record.unlink()  # acknowledging is deleting
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stop_blocks_on_a_crashed_watcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            write_record(root, watcher_pid=dead_pid())
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("died", result.stderr)

    def test_stop_allows_a_live_watch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            write_record(root)  # alive: overnight arms outlive turns by design
            result = run_moltke(root, "--stop", stdin="{}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_step_status_lists_watch_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workflow_repo(tmp)
            git_baseline(root)
            write_record(root)
            result = run_moltke(root, "--step", "status")
            self.assertEqual(result.returncode, 0, result.stderr)
            status = (root / "adocs" / "status.md").read_text(encoding="utf-8")
            self.assertIn("Watching", status)
            self.assertIn("RUN-DONE", status)


if __name__ == "__main__":
    unittest.main()
