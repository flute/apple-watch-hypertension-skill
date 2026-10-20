#!/usr/bin/env python3
"""Portable local CLI. doctor/status/report never start location transmission."""

import argparse
import asyncio
import importlib.util
import json
import math
import shutil
import sys
import time
import uuid
from dataclasses import fields
from pathlib import Path

from bpkit.session import (
    APP_HOME,
    ROOT,
    atomic_json,
    process_alive,
    read_json,
    resolve_session,
    spawn_worker,
    stop_process,
)
from bpkit.workflow import EVENTS, SOURCES, Evidence, completion, evidence_record


def output(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def start(args):
    if sys.platform != "darwin":
        raise ValueError("Live USB sessions require macOS; documentation/tests are portable")
    if not math.isfinite(args.duration) or not 1 <= args.duration <= 600:
        raise ValueError("duration must be between 1 and 600 seconds; never extend silently")
    if not Path("/usr/bin/sandbox-exec").is_file():
        raise ValueError("The local-only macOS sandbox is unavailable; no unsafe fallback")
    from bpkit.protocol import coordinate
    from bpkit.runner import load_identity

    coordinate(args.latitude, True)
    coordinate(args.longitude, False)
    identity = Path(args.identity_dir).expanduser().resolve()
    if identity.is_relative_to(ROOT):
        raise ValueError("Keep identities outside the skill checkout")
    load_identity(identity)
    sessions = APP_HOME / "sessions"
    sessions.mkdir(parents=True, exist_ok=True, mode=0o700)
    # One sender at a time, even when separate agents share the same Mac.
    import fcntl

    with (sessions / ".start.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for record in sessions.glob("*/process.json"):
            if process_alive(**read_json(record)):
                raise ValueError("An active sender exists; status/stop it before starting another")
        token = uuid.uuid4().hex
        folder = sessions / token
        folder.mkdir(mode=0o700)
        atomic_json(
            folder / "config.json",
            {
                "identity_dir": str(identity),
                "duration": args.duration,
                "started_at": time.time(),
                "probe": args.probe,
                "latitude": args.latitude,
                "longitude": args.longitude,
            },
        )
        command = [
            "/usr/bin/sandbox-exec",
            "-f",
            str(ROOT / "scripts/local-only.sb"),
            sys.executable,
            str(Path(__file__).resolve()),
            "_worker",
            "--session",
            str(folder),
        ]
        record = spawn_worker(command, folder)
    return {
        "session": token,
        "directory": str(folder),
        "pid": record["pid"],
        "duration_seconds": args.duration,
        "probe": args.probe,
        "next": "status --session " + token,
        "stop": "stop --session " + token,
    }


def handoff(folder, original=None, baseline_note=None, waiting_for=None):
    """A private resume record. Never put passwords, diagnoses, or health answers here."""
    data = read_json(folder / "handoff.json", {})
    if original is not None:
        if original not in {"on", "off"}:
            raise ValueError("original Location Services must be on or off")
        data["original_location_services"] = original
    if baseline_note is not None:
        if len(baseline_note) > 500:
            raise ValueError("Keep the private baseline note to 500 characters or less")
        data["baseline_note"] = baseline_note
    if waiting_for is not None:
        data["waiting_for"] = waiting_for
    if any(value is not None for value in [original, baseline_note, waiting_for]):
        data["updated_at"] = time.time()
        atomic_json(folder / "handoff.json", data)
    return data


def status(folder):
    record = read_json(folder / "process.json")
    alive = process_alive(**record)
    state = read_json(folder / "state.json", {"status": "starting"})
    observed = read_json(folder / "verification.json", [])
    evidence = Evidence(sender_stopped=not alive)
    events = []
    try:
        for line in (folder / "events.jsonl").read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            events.append(event)
            name = event.get("event")
            if name == "MFi_v3_authenticated":
                evidence.authenticated = True
            if name == "identification_accepted":
                evidence.identified = True
            if name == "location_subscribed":
                evidence.subscribed = True
            if name == "location_unsubscribed":
                evidence.subscribed = False
            if name == "location_link_acknowledged":
                evidence.packets += 1
    except FileNotFoundError:
        pass
    for entry in observed:
        if entry["event"] in EVENTS:
            setattr(evidence, entry["event"], True)
    resume = read_json(folder / "handoff.json", {})
    config = read_json(folder / "config.json", {})
    remaining = (
        max(0, config.get("started_at", 0) + config.get("duration", 0) - time.time())
        if alive
        else 0
    )
    return {
        "session": folder.name,
        "process_alive": alive,
        "remaining_seconds_approx": round(remaining, 1),
        "handoff": {
            "baseline_recorded": bool(resume.get("baseline_note")),
            "original_location_services": resume.get("original_location_services"),
            "waiting_for": resume.get("waiting_for"),
        },
        "worker": state,
        "facts": {f.name: getattr(evidence, f.name) for f in fields(evidence)},
        "verification": observed,
        "completion": completion(evidence),
        "recent_events": events[-8:],
    }


def verify(folder, event, source):
    current = status(folder)
    facts = current["facts"]
    if event in {"real_location_restored", "notification_rechecked_after_restore"}:
        if current["process_alive"]:
            raise ValueError("Stop the sender before verifying restoration")
    if event == "notification_enabled" and not facts["location_adopted"]:
        raise ValueError(
            "Verify actual map movement before completing this local-location workflow"
        )
    if event == "notification_rechecked_after_restore" and not facts["real_location_restored"]:
        raise ValueError("Verify real location restoration before rechecking the notification")
    records = read_json(folder / "verification.json", [])
    records.append(evidence_record(event, source))
    atomic_json(folder / "verification.json", records)
    return status(folder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sessions", help="Find local session IDs without contacting the phone")
    doctor = commands.add_parser("doctor", help="Read-only environment check")
    doctor.add_argument("--device", action="store_true", help="Read model/OS through trusted USB")
    check = commands.add_parser("check-identity", help="Validate local certificate/key consistency")
    check.add_argument("--identity-dir", default=str(APP_HOME / "identity"))
    launch = commands.add_parser(
        "start", help="Start a bounded USB worker with IP networking denied"
    )
    launch.add_argument("--identity-dir", default=str(APP_HOME / "identity"))
    launch.add_argument("--duration", type=float, default=600)
    launch.add_argument("--probe", action="store_true", help="Handshake only: no NMEA transmission")
    target = launch.add_mutually_exclusive_group(required=True)
    target.add_argument("--hong-kong", action="store_true", help="Use Hong Kong Central")
    target.add_argument("--latitude", type=float, help="Explicit user-authorized target latitude")
    launch.add_argument("--longitude", type=float)
    for name in ["status", "stop", "verify", "report", "handoff", "_worker"]:
        command = commands.add_parser(name)
        command.add_argument("--session", required=True)
        if name == "handoff":
            command.add_argument("--original-location-services", choices=["on", "off"])
            command.add_argument(
                "--baseline-note", help="Private local baseline; never health answers"
            )
            command.add_argument(
                "--waiting-for",
                choices=[
                    "none",
                    "connect",
                    "trust",
                    "mirror-unlock",
                    "location-adoption",
                    "eligibility",
                    "health-setup",
                    "unplug",
                    "restoration",
                    "notification-recheck",
                ],
            )
        if name == "verify":
            command.add_argument("--event", choices=sorted(EVENTS), required=True)
            command.add_argument("--source", choices=sorted(SOURCES), required=True)
    args = parser.parse_args()
    try:
        if args.command == "sessions":
            items = []
            for record in sorted(
                (APP_HOME / "sessions").glob("*/process.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            ):
                data = status(record.parent)
                items.append(
                    {
                        k: data[k]
                        for k in [
                            "session",
                            "process_alive",
                            "handoff",
                            "completion",
                            "remaining_seconds_approx",
                        ]
                    }
                )
            output(items)
        elif args.command == "doctor":
            data = {
                "macos": sys.platform == "darwin",
                "python": sys.version.split()[0],
                "uv": bool(shutil.which("uv")),
                "dependencies": {
                    m: importlib.util.find_spec(m) is not None
                    for m in ["cryptography", "pymobiledevice3"]
                },
                "local_only_sandbox": Path("/usr/bin/sandbox-exec").is_file(),
                "iphone_mirroring_installed": Path(
                    "/System/Applications/iPhone Mirroring.app"
                ).exists(),
                "sends_location": False,
            }
            if args.device:
                from bpkit.runner import connect_usb

                async def inspect():
                    async with asyncio.timeout(15):
                        phone = await connect_usb()
                        try:
                            return {
                                "model": phone.short_info.get("ProductType"),
                                "ios": phone.product_version,
                            }
                        finally:
                            await phone.close()

                try:
                    data["device"] = asyncio.run(inspect())
                except Exception as error:
                    data["device"] = {
                        "connected": False,
                        "error_type": type(error).__name__,
                        "next": "Connect one USB iPhone, unlock it, and trust this Mac",
                    }
            output(data)
        elif args.command == "check-identity":
            from bpkit.runner import load_identity

            load_identity(args.identity_dir)
            output({"key_matches_certificate": True, "device_acceptance_verified": False})
        elif args.command == "start":
            if args.hong_kong:
                args.latitude, args.longitude = 22.2819, 114.1589
            elif args.longitude is None:
                raise ValueError("--latitude requires --longitude")
            output(start(args))
        elif args.command == "_worker":
            from bpkit.runner import run_worker

            folder = Path(args.session).resolve()

            def emit(event, **values):
                print(json.dumps({"event": event, **values}), flush=True)

            asyncio.run(run_worker(folder, emit))
        else:
            folder = resolve_session(args.session)
            if args.command == "stop":
                stop_process(read_json(folder / "process.json"))
            if args.command == "handoff":
                output(
                    handoff(
                        folder,
                        args.original_location_services,
                        args.baseline_note,
                        args.waiting_for,
                    )
                )
            elif args.command == "verify":
                output(verify(folder, args.event, args.source))
            else:
                output(status(folder))
    except (OSError, ValueError, RuntimeError) as error:
        # CLI-owned messages have no credential/device contents; do not dump third-party tracebacks.
        output({"error": type(error).__name__, "detail": str(error)})
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
