import asyncio
from datetime import UTC, datetime

import pytest
from bpkit.protocol import MARKER, Link, ident, nmea, packet, param, params
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils


def test_reference_packet_checksum_and_negative_corruption():
    raw = packet(0x40, 100, 88, 10, b"hello")
    assert raw[:9].hex() == "ff5a000f4064580a92"
    assert sum(raw[:9]) % 256 == sum(raw[9:]) % 256 == 0
    assert params(param(0, b"one") + param(0, b"two")) == [(0, b"one"), (0, b"two")]
    with pytest.raises(ValueError):
        params(b"\x00\x10\x00\x00abc")


def test_nmea_coordinates_rounding_clock_and_checksum():
    lines = nmea(latitude=-89.999999999, longitude=180, clock_offset=60).splitlines()
    assert ",9000.0000,S,18000.0000,E," in lines[0]
    assert datetime.now(UTC).strftime("%d%m%y") in lines[1]
    assert lines[1].split("*")[0].endswith(",,,A")
    for line in lines:
        body, expected = line[1:].split("*")
        checksum = 0
        for char in body.encode():
            checksum ^= char
        assert checksum == int(expected, 16)
    for latitude, longitude in [(91, 0), (0, -181), (float("nan"), 0)]:
        with pytest.raises(ValueError):
            nmea(latitude=latitude, longitude=longitude)


class Stream:
    def __init__(self):
        self.sent = []

    async def sendall(self, data):
        self.sent.append(data)


def make_link(**kw):
    return Link(Stream(), b"synthetic-certificate", ec.generate_private_key(ec.SECP256R1()), **kw)


async def test_challenge_is_prehashed_raw_p256_and_not_logged():
    events = []
    link = make_link(emit=lambda e, **kw: events.append((e, kw)))
    link.ready = True
    digest = b"Q" * 32
    await link.handle(0xAA02, param(0, digest))
    raw = link.s.sent[-1]
    assert int.from_bytes(raw[13:15], "big") == 0xAA03
    signature = params(raw[15:-1])[0][1]
    assert len(signature) == 64
    r, s = int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big")
    link.key.public_key().verify(
        utils.encode_dss_signature(r, s), digest, ec.ECDSA(utils.Prehashed(hashes.SHA256()))
    )
    assert digest.hex() not in str(events)


async def test_fragments_duplicate_packets_and_corrupt_header():
    link = make_link()
    link.ack = 66
    frame = packet(0x40, 67, 99, 10, b"@@\x00\x06\xaa\x05")
    for byte in frame:
        await link.feed(bytes([byte]))
    assert link.authed
    await link.feed(frame)
    assert link.ack == 67
    corrupt = bytearray(frame)
    corrupt[8] ^= 1
    with pytest.raises(ValueError):
        await link.feed(bytes(corrupt))


async def test_probe_sends_no_nmea_and_quits_after_all_three_gates():
    link = make_link()
    link.authed = link.identified = link.subscribed = True
    link.active = {1, 2}
    await link.run(0.5)
    assert link.s.sent[0] == MARKER
    assert link.count == 0


async def test_no_location_before_authentication_and_identification():
    link = make_link(send=True)
    link.subscribed = True
    link.active = {1, 2}

    # Make the stream silent; a short deadline must still stop.
    async def silent(_size):
        await asyncio.sleep(60)

    link.s.recv_any = silent
    await link.run(0.05)
    assert link.count == 0


async def test_send_uses_separate_parameters_for_requested_sentences_only():
    link = make_link(send=True)
    link.authed = link.identified = link.subscribed = True
    link.active = {2}
    link.ready = True

    async def silent(_size):
        await asyncio.sleep(60)

    link.s.recv_any = silent
    await link.run(0.05)
    frames = [f for f in link.s.sent if f.startswith(b"\xffZ") and f[7] == 10]
    fields = params(frames[0][15:-1])
    assert len(fields) == 1 and fields[0][0] == 0
    assert fields[0][1].startswith(b"$GPRMC,") and fields[0][1].endswith(b"\r\n\0")


def test_identity_advertises_location_only_no_unimplemented_carplay():
    fields = dict(params(ident()))
    assert 22 in fields
    assert fields[6].endswith(bytes.fromhex("fffb"))
    assert [i for i, _ in params(fields[16])] == [0, 1, 2]


async def test_subscription_controls_sentences_interval_and_stop():
    link = make_link()
    await link.handle(0xFFFA, param(1) + param(0x8001, (1500).to_bytes(4, "big")))
    assert link.subscribed and link.active == {1}
    assert link.interval >= 1.5
    await link.handle(0xFFFC, b"")
    assert not link.subscribed and not link.active
