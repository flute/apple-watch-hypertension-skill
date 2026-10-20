"""The only live-device code path. Caller must explicitly start a bounded session."""

import asyncio
import math
import signal
import time

from local_mfi_v3_helper import validate_identity

from .protocol import Link
from .session import atomic_json, read_json


def load_identity(directory):
    from pathlib import Path

    folder = Path(directory).expanduser().resolve()
    material = []
    for filename in ["certificate.p7b", "identity.pk8"]:
        with (folder / filename).open("rb") as stream:
            raw = stream.read(16385)
        if not 1 <= len(raw) <= 16384:
            raise ValueError("Identity files must contain 1..16384 bytes")
        material.append(raw)
    cert, encoded_key = material
    return cert, validate_identity(cert, encoded_key)


async def connect_usb():
    from pymobiledevice3.lockdown import create_using_usbmux
    from pymobiledevice3.usbmux import list_devices

    devices = [d for d in await list_devices() if d.is_usb]
    if len(devices) != 1:
        raise RuntimeError("Connect exactly one unlocked, trusted USB iPhone")
    phone = await create_using_usbmux(
        serial=devices[0].serial, connection_type="USB", autopair=False
    )
    return phone


async def run_worker(folder, emit, connector=connect_usb):
    config = read_json(folder / "config.json")
    cert, key = load_identity(config["identity_dir"])
    phone = stream = None
    state = {"status": "starting", "sender_stopped": False}
    atomic_json(folder / "state.json", state)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    task = asyncio.current_task()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, task.cancel)
    try:
        # Includes pairing/service/handshake delays: waiting for a human never extends this budget.
        budget = asyncio.timeout(config["duration"])
        async with budget:
            phone = await connector()
            stream = await phone.start_lockdown_service("com.apple.carkit.service")
            emit("CarKit_open")
            offset = float(await phone.get_value(key="TimeIntervalSince1970")) - time.time()
            if not math.isfinite(offset) or abs(offset) > 3600:
                raise RuntimeError("Device clock differs by over one hour; verify device time")
            emit("NMEA_clock_aligned", offset_seconds=round(offset, 2))
            state["status"] = "running"
            atomic_json(folder / "state.json", state)
            link = Link(
                stream,
                cert,
                key,
                send=not config["probe"],
                emit=emit,
                clock_offset=offset,
                latitude=config["latitude"],
                longitude=config["longitude"],
            )
            await link.run(config["duration"], stop)
            state["status"] = "finished"
    except TimeoutError:
        if budget.expired():
            state["status"] = "expired"
            emit("duration_expired")
        else:
            state["status"] = "error"
            state["error_type"] = "ProtocolTimeout"
            emit("protocol_timeout")
    except asyncio.CancelledError:
        state["status"] = "stopped"
        emit("stop_requested")
    except Exception as error:
        state["status"] = "error"
        # Error text from third-party libraries may contain device identifiers; keep it local-safe.
        state["error_type"] = type(error).__name__
        emit("error", type=type(error).__name__)
    finally:
        for resource in [stream, phone]:
            if resource is not None:
                try:
                    await asyncio.wait_for(resource.close(), 2)
                except Exception:
                    emit("close_warning")
        state["sender_stopped"] = True
        atomic_json(folder / "state.json", state)
        emit("CarKit_closed_no_further_NMEA")
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.remove_signal_handler(sig)
    return state
