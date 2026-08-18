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

WATCH_DIR = "moltke_watch"  # mirrors bin/moltke.py

DONE_RE = "RUN-DONE"
FAIL_RE = "RUN-FAILED"


def start_watch(cwd, log, regex, *extra):
    return subprocess.Popen(
        [sys.executable, str(MOLTKE), "--watch", str(log), regex, *extra],
        cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def run_watch(cwd, log, regex, *extra, timeout=15):
    proc = start_watch(cwd, log, regex, *extra)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        # A watcher outliving its ceiling is exactly what these tests catch, and
        # communicate() leaves it running: the red state of S132 leaked three
        # spinning watchers into the machine before this.
        proc.kill()
        proc.communicate()
        raise
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


# S132 (2026-08-18_adversarial-F02): classic catastrophic backtracking. 40 a's
# against a non-matching tail is ~2**40 steps, so any exit inside the ceiling is
# the bound working and never the scan finishing early.
BACKTRACK_RE = r"(a+)+$"
BACKTRACK_LOG = "a" * 40 + "X\n"

NO_TIMER_DRIVER = '''\
"""Drive --watch with the interval timer taken away (S132).

argv: <path to moltke.py> <moltke argv...>.
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("moltke_under_test", sys.argv[1])
moltke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(moltke)

moltke.HAS_SCAN_ALARM = False
sys.exit(moltke.main(sys.argv[2:]))
'''


class TestWatchScanIsBounded(unittest.TestCase):
    """S132: the ceiling is a deadline for the process, not for the poll loop.

    The scan itself is caller-supplied work — an arbitrary regex over a file of
    arbitrary size — so a bound checked only between polls is not a bound at
    all. Each of these hangs forever inside one `pattern.search` without an
    out-of-band timer.
    """

    def test_backtracking_regex_still_exits_at_the_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text(BACKTRACK_LOG, encoding="utf-8")
            started = time.monotonic()
            code, out, err = run_watch(tmp, log, BACKTRACK_RE,
                                       "--ceiling", "1s", "--interval", "5s")
            self.assertEqual(code, 124, err)
            self.assertIn("ceiling", out)
            self.assertLess(time.monotonic() - started, 10)

    def test_bounded_scan_reports_the_ceiling_not_a_dead_pid(self):
        # A scan cut mid-flight must not fall through as "no marker found" and
        # get reported as whatever the next check happens to conclude.
        watched = sleeper(30)
        self.addCleanup(watched.wait)
        self.addCleanup(watched.kill)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text(BACKTRACK_LOG, encoding="utf-8")
            code, out, err = run_watch(tmp, log, BACKTRACK_RE, "--pid", str(watched.pid),
                                       "--ceiling", "1s", "--interval", "5s")
            self.assertEqual(code, 124, err)
            self.assertIn("ceiling", out)
            self.assertNotIn("died", out)

    def test_platform_without_a_timer_warns_and_still_reaches_its_ceiling(self):
        # Windows has no setitimer, so the degraded path has no platform in this
        # suite to run on. Disabling the timer is the only way to observe that
        # it says so and still ends at the ceiling between polls.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "run.log"
            log.write_text("no marker\n", encoding="utf-8")
            driver = root / "no_timer_driver.py"
            driver.write_text(NO_TIMER_DRIVER, encoding="utf-8")
            proc = subprocess.Popen(
                [sys.executable, str(driver), str(MOLTKE), "--watch", str(log),
                 DONE_RE, "--ceiling", "0.4s", "--interval", "0.05s"],
                cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = proc.communicate(timeout=15)
            self.assertEqual(proc.returncode, 124, err)
            self.assertIn("no interval timer", err)
            self.assertIn("ceiling", out)

    def test_bounded_scan_records_a_ceiling_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
            log = root / "run.log"
            log.write_text(BACKTRACK_LOG, encoding="utf-8")
            code, _out, err = run_watch(tmp, log, BACKTRACK_RE,
                                        "--ceiling", "1s", "--interval", "5s")
            self.assertEqual(code, 124, err)
            record = json.loads(next((root / ".git" / WATCH_DIR).glob("*.json"))
                                .read_text(encoding="utf-8"))
            self.assertEqual(record["outcome"], "ceiling")
            self.assertEqual(record["exit_code"], 124)


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


ARM_WINDOW_DRIVER = '''\
"""Drive --watch with a SIGTERM forced into the arm window (S140).

argv: <path to moltke.py> before|after <moltke argv...>. The kill is sent from
inside the registration write itself, so the window is hit on every run rather
than once every few hundred under load.
"""
import importlib.util
import os
import signal
import sys

spec = importlib.util.spec_from_file_location("moltke_under_test", sys.argv[1])
moltke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(moltke)

when, real, fired = sys.argv[2], moltke._watch_write, []


def kill_at_registration(path, record):
    if fired:  # the outcome write on the way out, left alone
        return real(path, record)
    fired.append(True)
    if when == "before":
        os.kill(os.getpid(), signal.SIGTERM)
        return real(path, record)  # reached only if nothing handled the signal
    real(path, record)
    os.kill(os.getpid(), signal.SIGTERM)


moltke._watch_write = kill_at_registration
sys.exit(moltke.main(sys.argv[3:]))
'''


class TestWatchArmWindow(unittest.TestCase):
    """S140: the window between registering an obligation and being able to
    answer for it. A SIGTERM landing there once killed the watcher through the
    default disposition, leaving a record with no outcome — an obligation
    nobody can discharge, since discharging one means deleting a finished
    record. Deterministic: the signal comes from inside the arm sequence."""

    def _kill_at_registration(self, tmp, when, log, *extra):
        root = Path(tmp)
        marked_repo(tmp)
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
        driver = root / "arm_window_driver.py"
        driver.write_text(ARM_WINDOW_DRIVER, encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(driver), str(MOLTKE), when,
             "--watch", str(log), DONE_RE, *extra],
            cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _out, err = proc.communicate(timeout=15)
        return proc.returncode, err, root / ".git" / WATCH_DIR

    def test_kill_just_after_registration_is_recorded_as_stopped(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("no marker\n", encoding="utf-8")
            code, err, watch_dir = self._kill_at_registration(
                tmp, "after", log, "--ceiling", "60s", "--interval", "0.05s")
            self.assertEqual(code, 128 + signal.SIGTERM, err)
            records = list(watch_dir.glob("*.json"))
            self.assertEqual(len(records), 1, err)
            record = json.loads(records[0].read_text(encoding="utf-8"))
            self.assertEqual(record["outcome"], "stopped")
            self.assertEqual(record["exit_code"], 128 + signal.SIGTERM)
            self.assertIn("ended_at", record)

    def test_kill_before_registration_leaves_no_record(self):
        # Nothing reached the disk, so nothing is owed: an empty directory is
        # the right answer, not a record that would block a stop until deleted.
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.log"
            log.write_text("no marker\n", encoding="utf-8")
            code, err, watch_dir = self._kill_at_registration(
                tmp, "before", log, "--ceiling", "60s", "--interval", "0.05s")
            self.assertEqual(code, 128 + signal.SIGTERM, err)
            self.assertEqual(list(watch_dir.glob("*.json")), [], err)


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
