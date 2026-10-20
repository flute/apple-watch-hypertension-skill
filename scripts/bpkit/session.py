"""Local bounded worker supervision. No USB/device access in this module."""

import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP_HOME = Path.home() / "Library/Application Support/apple-watch-hypertension"


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".state-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except FileNotFoundError:
        return default


def fingerprint(pid):
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "lstart="],
        capture_output=True,
        text=True,
        check=False,
        timeout=3,
    )
    return result.stdout.strip()


def process_alive(pid, fingerprint, token):
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "stat=", "-o", "lstart=", "-o", "args="],
        capture_output=True,
        text=True,
        check=False,
        timeout=3,
    )
    line = result.stdout.strip()
    return bool(
        line and not line.startswith("Z") and fingerprint and fingerprint in line and token in line
    )


def group_members(group):
    result = subprocess.run(
        ["ps", "-axo", "pid=,pgid=,stat=,lstart="],
        capture_output=True,
        text=True,
        check=True,
        timeout=3,
    )
    members = {}
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) == 4 and int(parts[1]) == group and not parts[2].startswith("Z"):
            members[int(parts[0])] = parts[3].strip()
    return members


def stop_process(record, grace_seconds=6):
    """Verify group ownership, then wait for every non-zombie member, including children."""
    if not process_alive(**record):
        return False
    pid = record["pid"]
    if os.getpgid(pid) != pid or pid == os.getpgrp():
        raise RuntimeError("Refusing to signal an unrelated process group")
    owned = group_members(pid)
    for sig, budget in [(signal.SIGTERM, grace_seconds), (signal.SIGKILL, 2)]:
        current = group_members(pid)
        if not current:
            return True
        if not any(owned.get(member) == stamp for member, stamp in current.items()):
            raise RuntimeError("Process group ownership changed; termination unverified")
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            return True
        deadline = time.monotonic() + budget
        while time.monotonic() < deadline:
            if not group_members(pid):
                return True
            time.sleep(0.05)
    raise RuntimeError("Worker group termination could not be confirmed")


def spawn_worker(command, folder):
    """Never leave a new worker alive if its recovery metadata cannot be recorded."""
    fd = os.open(folder / "events.jsonl", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=log, start_new_session=True, cwd=ROOT
        )
    try:
        stamp = fingerprint(process.pid)
        if not stamp:
            raise RuntimeError("Worker exited during startup; inspect private session events")
        record = {"pid": process.pid, "fingerprint": stamp, "token": folder.name}
        atomic_json(folder / "process.json", record)
        return record
    except BaseException:
        # Popen still owns/unreaped PID: no PID reuse is possible before wait().
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        # Keep the leader unreaped until the last group signal: its PID cannot be reused.
        time.sleep(0.1)
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=2)
        raise


def resolve_session(value):
    path = Path(value).expanduser()
    if not path.is_absolute():
        if path.name != value or not value or value in {".", ".."}:
            raise ValueError("Use the session ID returned by start, or its absolute directory")
        path = APP_HOME / "sessions" / value
    path = path.resolve()
    if not (path / "config.json").is_file() or not (path / "process.json").is_file():
        raise ValueError("Unknown session; do not guess a PID or session ID")
    return path
