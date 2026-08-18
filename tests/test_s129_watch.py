"""S129: --watch, the self-terminating four-exit watcher (DEC-049, AGENTS.md §12).

Every exit path is observed as an exit code from a real subprocess, because
the whole point of the primitive is that the process ends by itself. Timings
use tiny intervals and ceilings; every wait is bounded by communicate(timeout).
"""

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from fixtures import marked_repo

MOLTKE = Path(__file__).resolve().parent.parent / "bin" / "moltke.py"

DONE_RE = "RUN-DONE"
FAIL_RE = "RUN-FAILED"


def start_watch(cwd, log, regex, *extra):
    return subprocess.Popen(
        [sys.executable, str(MOLTKE), "--watch", str(log), regex, *extra],
        cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def run_watch(cwd, log, regex, *extra, timeout=15):
    proc = start_watch(cwd, log, regex, *extra)
    out, err = proc.communicate(timeout=timeout)
    return proc.returncode, out, err


def sleeper(seconds):
    """A real process to watch; the test reaps it so death is observable."""
    return subprocess.Popen([sys.executable, "-c", f"import time; time.sleep({seconds})"])


class TestWatchExits(unittest.TestCase):
    """The four exits, each terminating the process with no outside help."""

    def test_exit_0_when_marker_appears_after_arming(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("starting\n", encoding="utf-8")
            proc = start_watch(tmp, log, DONE_RE, "--ceiling", "10s", "--interval", "0.05s")
            time.sleep(0.3)
            with open(log, "a", encoding="utf-8") as handle:
                handle.write("RUN-DONE rating=1234\n")
            out, err = proc.communicate(timeout=15)
            self.assertEqual(proc.returncode, 0, err)
            self.assertIn("RUN-DONE rating=1234", out)

    def test_marker_written_before_arming_is_caught(self):
        # The tail -f failure mode, cured: the whole file is scanned, so a
        # marker that landed before the watcher armed still ends the watch.
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("RUN-DONE early\n", encoding="utf-8")
            code, out, err = run_watch(tmp, log, DONE_RE, "--ceiling", "10s",
                                       "--interval", "0.05s")
            self.assertEqual(code, 0, err)
            self.assertIn("RUN-DONE early", out)

    def test_exit_4_on_fail_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("RUN-FAILED err=timeout\n", encoding="utf-8")
            code, out, err = run_watch(tmp, log, DONE_RE, "--fail-re", FAIL_RE,
                                       "--ceiling", "10s", "--interval", "0.05s")
            self.assertEqual(code, 4, err)
            self.assertIn("RUN-FAILED err=timeout", out)

    def test_exit_3_when_pid_dies_without_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("starting\n", encoding="utf-8")
            watched = sleeper(0.3)
            proc = start_watch(tmp, log, DONE_RE, "--pid", str(watched.pid),
                               "--ceiling", "10s", "--interval", "0.05s")
            watched.wait(timeout=5)  # reap, so kill(pid, 0) stops seeing it
            out, err = proc.communicate(timeout=15)
            self.assertEqual(proc.returncode, 3, err)
            self.assertIn(str(watched.pid), out)

    def test_marker_beats_dead_pid(self):
        # A run that writes its marker and exits must read as success, not as
        # a silent death: the log is checked before and after the pid probe.
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("RUN-DONE just before exiting\n", encoding="utf-8")
            watched = sleeper(0.01)
            watched.wait(timeout=5)
            code, out, err = run_watch(tmp, log, DONE_RE, "--pid", str(watched.pid),
                                       "--ceiling", "10s", "--interval", "0.05s")
            self.assertEqual(code, 0, err)
            self.assertIn("RUN-DONE", out)

    def test_exit_124_at_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("no marker ever\n", encoding="utf-8")
            started = time.monotonic()
            code, out, err = run_watch(tmp, log, DONE_RE, "--pid", str(os.getpid()),
                                       "--ceiling", "0.4s", "--interval", "0.05s")
            self.assertEqual(code, 124, err)
            self.assertIn("ceiling", out)
            self.assertLess(time.monotonic() - started, 10)


class TestWatchRefusals(unittest.TestCase):
    """Bad arms are refused with the missing condition named (INV-12 style)."""

    def test_ceiling_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("x\n", encoding="utf-8")
            code, _out, err = run_watch(tmp, log, DONE_RE)
            self.assertEqual(code, 1, err)
            self.assertIn("ceiling", err)

    def test_unparseable_ceiling_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("x\n", encoding="utf-8")
            code, _out, err = run_watch(tmp, log, DONE_RE, "--ceiling", "soon")
            self.assertEqual(code, 1, err)
            self.assertIn("soon", err)

    def test_bad_regex_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("x\n", encoding="utf-8")
            code, _out, err = run_watch(tmp, log, "(", "--ceiling", "5s")
            self.assertEqual(code, 1, err)
            self.assertIn("regex", err)

    def test_wrong_arg_count_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(MOLTKE), "--watch", "only-one-arg",
                 "--ceiling", "5s"],
                cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("usage", result.stderr)


class TestWatchRegistration(unittest.TestCase):
    """A watch is an obligation, recorded in the filesystem (prime directive):
    armed under .git/moltke_watch/, outcome written on every exit path."""

    def _git_repo(self, tmp):
        marked_repo(tmp)
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
        return Path(tmp)

    def test_record_written_on_arm_and_outcome_on_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._git_repo(tmp)
            log = root / "run.log"
            log.write_text("RUN-DONE\n", encoding="utf-8")
            code, _out, err = run_watch(tmp, log, DONE_RE, "--ceiling", "5s",
                                        "--interval", "0.05s")
            self.assertEqual(code, 0, err)
            records = list((root / ".git" / "moltke_watch").glob("*.json"))
            self.assertEqual(len(records), 1, err)
            record = json.loads(records[0].read_text(encoding="utf-8"))
            self.assertEqual(record["outcome"], "success marker")
            self.assertEqual(record["exit_code"], 0)
            self.assertEqual(record["regex"], DONE_RE)
            self.assertIn("armed_at", record)
            self.assertIn("ended_at", record)

    def test_kill_is_recorded_as_stopped(self):
        # The manual-stop belt: even that path leaves an outcome behind.
        with tempfile.TemporaryDirectory() as tmp:
            root = self._git_repo(tmp)
            log = root / "run.log"
            log.write_text("no marker\n", encoding="utf-8")
            proc = start_watch(tmp, log, DONE_RE, "--ceiling", "60s",
                               "--interval", "0.05s")
            watch_dir = root / ".git" / "moltke_watch"
            for _ in range(100):
                if list(watch_dir.glob("*.json")):
                    break
                time.sleep(0.05)
            else:
                proc.kill()
                self.fail("watch never registered itself")
            proc.send_signal(signal.SIGTERM)
            proc.communicate(timeout=15)
            self.assertEqual(proc.returncode, 128 + signal.SIGTERM)
            record = json.loads(next(watch_dir.glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(record["outcome"], "stopped")
            self.assertEqual(record["exit_code"], 128 + signal.SIGTERM)

    def test_no_git_still_watches_with_a_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("RUN-DONE\n", encoding="utf-8")
            code, out, err = run_watch(tmp, log, DONE_RE, "--ceiling", "5s",
                                       "--interval", "0.05s")
            self.assertEqual(code, 0, err)
            self.assertIn("RUN-DONE", out)
            self.assertIn("not registered", err)


class TestWatchIsGateExempt(unittest.TestCase):
    """INV-11 exemption: the gate's silent exit 0 would read as a marker seen.
    A watcher never fakes success, so --watch runs before the gate."""

    def test_watch_works_in_a_disabled_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            marked_repo(tmp, overrides={"enabled": False})
            log = Path(tmp) / "run.log"
            log.write_text("no marker\n", encoding="utf-8")
            code, out, _err = run_watch(tmp, log, DONE_RE, "--ceiling", "0.3s",
                                        "--interval", "0.05s")
            self.assertEqual(code, 124, out)


if __name__ == "__main__":
    unittest.main()
