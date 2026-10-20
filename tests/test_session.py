import os
import subprocess
import sys
import time

import pytest
from bpkit.session import atomic_json, fingerprint, process_alive, stop_process


def test_atomic_json_has_owner_only_permissions(tmp_path):
    p = tmp_path / "state.json"
    atomic_json(p, {"status": "running"})
    assert p.stat().st_mode & 0o777 == 0o600
    atomic_json(p, {"status": "closed"})
    assert "closed" in p.read_text()


def test_stop_handles_missing_process_and_never_signals_reused_pid():
    assert not process_alive(99999999, "wrong", "missing")
    own = {"pid": os.getpid(), "fingerprint": "not-this-process", "token": "not-our-worker"}
    assert stop_process(own) is False


@pytest.mark.skipif(sys.platform == "win32", reason="macOS/Linux process groups")
def test_stop_terminates_only_owned_process_group():
    token = "bpkit-offline-supervisor-test"
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)", token], start_new_session=True
    )
    try:
        for _ in range(30):
            stamp = fingerprint(process.pid)
            if stamp:
                break
            time.sleep(0.01)
        record = {"pid": process.pid, "fingerprint": stamp, "token": token}
        assert process_alive(**record)
        assert stop_process(record)
        process.wait(timeout=3)
        assert not process_alive(**record)
        assert stop_process(record) is False
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX process groups")
def test_stop_also_kills_child_that_ignores_termination(tmp_path):
    ready = tmp_path / "child.pid"
    code = (
        "import signal,time,pathlib,os; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        f"pathlib.Path({str(ready)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    parent_code = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",{code!r}]); time.sleep(30)'
    token = "bpkit-owned-child-test"
    process = subprocess.Popen([sys.executable, "-c", parent_code, token], start_new_session=True)
    try:
        deadline = time.monotonic() + 3
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists()
        child = int(ready.read_text())
        child_stamp = fingerprint(child)
        record = {"pid": process.pid, "fingerprint": fingerprint(process.pid), "token": token}
        assert stop_process(record, grace_seconds=0.05)
        process.wait(timeout=3)
        assert not process_alive(child, child_stamp, "time.sleep(30)")
    finally:
        try:
            os.killpg(process.pid, 9)
        except ProcessLookupError:
            pass
        process.wait()


def test_bookkeeping_failure_rolls_back_owned_worker(tmp_path, monkeypatch):
    import bpkit.session as session

    token = tmp_path.name
    seen = []
    original = session.subprocess.Popen

    def capture(*a, **kw):
        process = original(*a, **kw)
        seen.append(process)
        return process

    def fail(_p, _data):
        raise OSError("simulated metadata failure")

    monkeypatch.setattr(session.subprocess, "Popen", capture)
    monkeypatch.setattr(session, "atomic_json", fail)
    with pytest.raises(OSError):
        session.spawn_worker([sys.executable, "-c", "import time;time.sleep(30)", token], tmp_path)
    assert seen[0].poll() is not None
