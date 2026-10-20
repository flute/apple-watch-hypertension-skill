import asyncio
import time

import pytest
from bpkit.protocol import MARKER, csm, packet, param, params, u16
from bpkit.runner import run_worker
from bpkit.session import atomic_json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import pkcs7
from test_local_mfi_v3_helper import encode_key, make_certificate


class PhoneStream:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.sequence = 20
        self.closed = False
        self.location = []

    async def sendall(self, raw):
        if raw == MARKER:
            return
        flags, sequence, _, session = raw[4:8]
        if flags & 0x80:
            sync = bytes([1, 30]) + u16(65535) + u16(2000) + u16(100) + bytes([4, 3, 10, 0, 1])
            await self.queue.put(MARKER + packet(0xC0, self.sequence, sequence, 0, sync))
            await self.message(0xAA00, sequence)
        elif session == 10:
            message_id = int.from_bytes(raw[13:15], "big")
            await self.queue.put(packet(0x40, self.sequence, sequence, 0))
            if message_id == 0xAA01:
                await self.message(0xAA02, sequence, param(0, b"Q" * 32))
            elif message_id == 0xAA03:
                await self.message(0xAA05, sequence)
                await self.message(0x1D00, sequence)
            elif message_id == 0x1D01:
                await self.message(0x1D02, sequence)
                await self.message(0xFFFA, sequence, param(1) + param(2))
            elif message_id == 0xFFFB:
                self.location.append(params(raw[15:-1]))

    async def message(self, message_id, ack, body=b""):
        self.sequence = (self.sequence + 1) & 255
        await self.queue.put(packet(0x40, self.sequence, ack, 10, csm(message_id, body)))

    async def recv_any(self, _size):
        return await self.queue.get()

    async def close(self):
        self.closed = True


class Phone:
    def __init__(self):
        self.stream = PhoneStream()
        self.closed = False

    async def start_lockdown_service(self, name):
        assert name == "com.apple.carkit.service"
        return self.stream

    async def get_value(self, key):
        assert key == "TimeIntervalSince1970"
        return time.time() + 60

    async def close(self):
        self.closed = True


@pytest.fixture
def config(tmp_path):
    folder = tmp_path / "session"
    folder.mkdir()
    identity = tmp_path / "identity"
    identity.mkdir()
    key = ec.generate_private_key(ec.SECP256R1())
    (identity / "certificate.p7b").write_bytes(
        pkcs7.serialize_certificates([make_certificate(key)], serialization.Encoding.DER)
    )
    (identity / "identity.pk8").write_bytes(encode_key(key))
    return folder, {
        "duration": 0.3,
        "probe": False,
        "latitude": 22.2819,
        "longitude": 114.1589,
        "identity_dir": str(identity),
    }


async def test_full_fake_phone_handshake_sends_then_times_out_and_closes(config):
    folder, settings = config
    atomic_json(folder / "config.json", settings)
    phone = Phone()

    async def connect():
        return phone

    events = []
    state = await run_worker(folder, lambda e, **kw: events.append((e, kw)), connect)
    assert state["sender_stopped"] and state["status"] == "expired"
    assert phone.closed and phone.stream.closed
    assert phone.stream.location
    assert all([i for i, _ in pair] == [0, 0] for pair in phone.stream.location)
    names = [e for e, _ in events]
    assert "MFi_v3_authenticated" in names and "location_link_acknowledged" in names
    assert names[-1] == "CarKit_closed_no_further_NMEA"
    assert next(kw["offset_seconds"] for e, kw in events if e == "NMEA_clock_aligned") > 59


async def test_probe_does_not_send_location_and_closes(config):
    folder, settings = config
    settings["probe"] = True
    atomic_json(folder / "config.json", settings)
    phone = Phone()

    async def connect():
        return phone

    state = await run_worker(folder, lambda *_a, **_kw: None, connect)
    assert not phone.stream.location and phone.closed
    assert state["sender_stopped"] and state["status"] == "finished"


async def test_human_wait_during_connection_is_bounded(config):
    folder, settings = config
    settings["duration"] = 0.02
    atomic_json(folder / "config.json", settings)

    async def connect():
        await asyncio.sleep(30)

    start = time.monotonic()
    state = await run_worker(folder, lambda *_a, **_kw: None, connect)
    assert time.monotonic() - start < 1
    assert state["status"] == "expired" and state["sender_stopped"]


async def test_protocol_timeout_is_not_normal_budget_expiry(config, monkeypatch):
    import bpkit.runner as runner

    folder, settings = config
    settings["duration"] = 30
    atomic_json(folder / "config.json", settings)
    phone = Phone()

    async def connect():
        return phone

    async def fail(*_a, **_kw):
        raise TimeoutError("negotiation failed")

    monkeypatch.setattr(runner.Link, "run", fail)
    events = []
    state = await run_worker(folder, lambda e, **kw: events.append(e), connect)
    assert state["status"] == "error" and state["error_type"] == "ProtocolTimeout"
    assert "protocol_timeout" in events and "duration_expired" not in events
    assert phone.closed
