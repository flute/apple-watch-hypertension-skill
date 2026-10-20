#!/usr/bin/env python3
# Personal experimental port of framing/auth/location from youcci/playport (GPL-3.0).
# No cloud MFi service. Keys stay local. Closing the stream stops all NMEA updates.
import asyncio
import math
import struct
import time
from datetime import UTC, datetime

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils

MARKER = bytes.fromhex("ff550200ee10")


def u16(n):
    return struct.pack(">H", n)


def param(i, b=b""):
    return u16(len(b) + 4) + u16(i) + b


def string(i, s):
    return param(i, s.encode() + b"\0")


def params(b):
    out = []
    while b:
        if len(b) < 4:
            raise ValueError("truncated parameter")
        n, i = struct.unpack(">HH", b[:4])
        if n < 4 or n > len(b):
            raise ValueError("bad parameter size")
        out.append((i, b[4:n]))
        b = b[n:]
    return out


def csm(i, b=b""):
    return b"@@" + u16(len(b) + 6) + u16(i) + b


def packet(control, seq, ack, sid, payload=None):
    h = (
        b"\xff\x5a"
        + u16(9 if payload is None else len(payload) + 10)
        + bytes([control, seq, ack, sid])
    )
    h += bytes([-sum(h) & 255])
    return h if payload is None else h + payload + bytes([-sum(payload) & 255])


def ident():
    b = b"".join(
        string(i, v)
        for i, v in enumerate(["Local CarKit", "LocalGPS", "Personal", "S12LOCAL", "1.0", "1.0"])
    )
    b += param(6, b"".join(u16(x) for x in [0xAA01, 0xAA03, 0xFFFB]))
    b += param(7, b"".join(u16(x) for x in [0xAA00, 0xAA02, 0xAA04, 0xAA05, 0xFFFA, 0xFFFC]))
    b += param(8, b"\0") + param(9, u16(0)) + string(12, "en") + string(13, "en")
    b += param(16, param(0, u16(0)) + string(1, "USBHostTransport") + param(2))
    b += param(22, param(0, u16(0)) + string(1, "LocalGPS") + param(17) + param(18))
    return b


def coordinate(value, latitude):
    limit = 90 if latitude else 180
    if not math.isfinite(value) or not -limit <= value <= limit:
        raise ValueError("coordinate out of range")
    degrees, minute_units = divmod(round(abs(value) * 600000), 600000)
    hemisphere = ("S" if value < 0 else "N") if latitude else ("W" if value < 0 else "E")
    return f"{degrees:0{2 if latitude else 3}d}{minute_units / 10000:07.4f}", hemisphere


def nmea(latitude=22.2819, longitude=114.1589, clock_offset=0.0):
    now = datetime.fromtimestamp(time.time() + clock_offset, UTC)

    def line(b):
        ck = 0
        for c in b.encode():
            ck ^= c
        return "$" + b + "*" + format(ck, "02X") + "\r\n"

    t = now.strftime("%H%M%S") + ".00"
    lat, north = coordinate(latitude, True)
    lon, east = coordinate(longitude, False)
    return line(f"GPGGA,{t},{lat},{north},{lon},{east},1,08,1.0,10.0,M,0.0,M,,") + line(
        f"GPRMC,{t},A,{lat},{north},{lon},{east},0.00,0.00,{now:%d%m%y},,,A"
    )


class Link:
    def __init__(
        self,
        s,
        certificate,
        key,
        send=False,
        emit=None,
        clock_offset=0.0,
        latitude=22.2819,
        longitude=114.1589,
    ):
        self.s = s
        self.seq = 99
        self.ack = 0
        self.ready = False
        self.synced = False
        self.buf = b""
        self.cbuf = b""
        self.pending = {}
        self.retry = 4.0
        self.window = 1
        self.maxlen = 65535
        self.cert = certificate
        self.key = key
        self.emit = emit or (lambda event, **kw: None)
        self.clock_offset = clock_offset
        self.latitude = latitude
        self.longitude = longitude
        self.active = set()
        self.interval = 0.25
        self.last_sent = {}
        self.authed = False
        self.identified = False
        self.subscribed = False
        self.send = send
        self.count = 0

    async def write(self, control, sid=0, payload=None, seq=None):
        await self.s.sendall(
            packet(control, self.seq if seq is None else seq, self.ack, sid, payload)
        )

    async def message(self, i, b=b""):
        if len(self.pending) >= min(self.window, 1):
            raise RuntimeError("peer send window full")
        p = csm(i, b)
        if len(p) + 10 > self.maxlen:
            raise RuntimeError("message exceeds peer packet size")
        self.seq = (self.seq + 1) & 255
        self.pending[self.seq] = [p, time.monotonic(), 0, i]
        await self.write(0x40, 10, p)
        if i != 0xFFFB:
            self.emit("tx", message=hex(i), bytes=len(b))

    async def handle(self, i, b):
        self.emit("rx", message=hex(i), bytes=len(b))
        if i == 0xAA00:
            await self.message(0xAA01, param(0, self.cert))
        elif i == 0xAA02:
            challenges = [v for j, v in params(b) if j == 0]
            if len(challenges) != 1:
                raise ValueError("Expected exactly one authentication challenge")
            digest = challenges[0]
            if len(digest) != 32:
                raise ValueError("MFi v3 digest must be 32 bytes")
            der = self.key.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
            r, s = utils.decode_dss_signature(der)
            await self.message(0xAA03, param(0, r.to_bytes(32, "big") + s.to_bytes(32, "big")))
        elif i == 0xAA04:
            raise RuntimeError("iPhone rejected MFi authentication")
        elif i == 0xAA05:
            self.authed = True
            self.emit("MFi_v3_authenticated")
        elif i == 0x1D00:
            await self.message(0x1D01, ident())
        elif i == 0x1D02:
            self.identified = True
            self.emit("identification_accepted")
        elif i == 0x1D03:
            raise RuntimeError(
                "identification rejected: " + str([(hex(j), v.hex()) for j, v in params(b)])
            )
        elif i == 0xFFFA:
            fields = params(b)
            self.active = {j for j, v in fields if j in (1, 2) and not v}
            self.subscribed = bool(self.active)
            intervals = [
                int.from_bytes(v, "big") / 1000
                for j, v in fields
                if j in (0x8001, 0x8002) and len(v) == 4 and j - 0x8000 in self.active
            ]
            self.interval = max(0.25, max(intervals, default=0.25))
            self.emit("location_subscribed", sentences=sorted(self.active))
        elif i == 0xFFFC:
            self.subscribed = False
            self.active.clear()
            self.emit("location_unsubscribed")

    async def feed(self, data):
        self.buf += data
        if len(self.buf) > 131070:
            raise ValueError("receive buffer limit")
        while len(self.buf) >= 2:
            if self.buf.startswith(MARKER):
                self.buf = self.buf[6:]
                self.emit("marker_received")
                continue
            if self.buf[:2] != b"\xff\x5a":
                self.buf = self.buf[1:]
                continue
            if len(self.buf) < 9:
                return
            h = self.buf[:9]
            n = int.from_bytes(h[2:4], "big")
            if sum(h) & 255 or n < 9:
                raise ValueError("invalid iAP2 header")
            if len(self.buf) < n:
                return
            frame = self.buf[:n]
            self.buf = self.buf[n:]
            ctrl, seq, ack, sid = h[4:8]
            p = frame[9:-1] if n > 9 else None
            if n > 9 and sum(frame[9:]) & 255:
                raise ValueError("invalid payload checksum")
            if ctrl & 0x10:
                raise RuntimeError("peer reset")
            if ctrl & 0x80:
                if (
                    p is None
                    or len(p) < 13
                    or p[0] != 1
                    or p[1] < 1
                    or int.from_bytes(p[2:4], "big") < 11
                ):
                    raise ValueError("invalid sync")
                self.ack = seq
                self.synced = True
                self.window = max(1, min(30, p[1]))
                self.maxlen = int.from_bytes(p[2:4], "big")
                if bytes([10, 0, 1]) not in [p[k : k + 3] for k in range(10, len(p), 3)]:
                    raise ValueError("peer rejected control session")
                self.retry = max(0.5, int.from_bytes(p[4:6], "big") / 1000)
                await self.write(0x40)
                self.emit("peer_sync", window=self.window, maxlen=self.maxlen)
            if ctrl & 0x40:
                if self.synced and not self.ready:
                    self.ready = True
                    self.emit("link_ready")
                for s in list(self.pending):
                    if ((ack - s) & 255) < 128:
                        item = self.pending.pop(s)
                        if item[3] == 0xFFFB:
                            self.emit("location_link_acknowledged")
            if ctrl & 0x20 and p:
                for s in p:
                    if s in self.pending:
                        await self.write(0x40, 10, self.pending[s][0], seq=s)
            if ctrl in (0, 0x40) and p is not None:
                distance = (seq - self.ack) & 255
                if distance == 1:
                    self.ack = seq
                    if sid == 10:
                        self.cbuf += p
                    await self.write(0x40)
                    while len(self.cbuf) >= 6:
                        if self.cbuf[:2] != b"@@":
                            raise ValueError("invalid CSM marker")
                        size = int.from_bytes(self.cbuf[2:4], "big")
                        if size < 6:
                            raise ValueError("invalid CSM size")
                        if len(self.cbuf) < size:
                            break
                        msg = self.cbuf[:size]
                        self.cbuf = self.cbuf[size:]
                        await self.handle(int.from_bytes(msg[4:6], "big"), msg[6:])
                elif distance == 0 or distance > 128:
                    await self.write(0x40)
                else:
                    await self.write(
                        0x20, payload=bytes((self.ack + d) & 255 for d in range(1, distance))
                    )

    async def run(self, duration, stop_event=None):
        await self.s.sendall(MARKER)
        sync = bytes([1, 1]) + u16(65535) + u16(4000) + u16(100) + bytes([4, 3, 10, 0, 1])
        await self.write(0x80, payload=sync)
        start = time.monotonic()
        lastsyn = start
        lastfix = 0
        while time.monotonic() - start < duration and not (stop_event and stop_event.is_set()):
            now = time.monotonic()
            if not self.ready and now - lastsyn > 0.5:
                if now - start > 15:
                    raise TimeoutError("iAP2 negotiation timeout")
                await self.write(0x80, payload=sync)
                lastsyn = now
            for seq, (p, sent, retries, msg_id) in list(self.pending.items()):
                if now - sent > self.retry:
                    if retries >= 3:
                        raise TimeoutError("iAP2 acknowledgement timeout")
                    await self.write(0x40, 10, p, seq)
                    self.pending[seq] = [p, now, retries + 1, msg_id]
            if self.authed and self.identified and self.subscribed:
                if not self.send:
                    self.emit("probe_complete_no_location_sent")
                    return
                if now - lastfix >= self.interval and len(self.pending) < min(self.window, 1):
                    sentences = nmea(self.latitude, self.longitude, self.clock_offset).splitlines()
                    await self.message(
                        0xFFFB,
                        b"".join(string(0, sentences[i - 1] + "\r\n") for i in sorted(self.active)),
                    )
                    lastfix = now
                    self.count += 1
                    if self.count == 1 or self.count % 30 == 0:
                        self.emit("location_packets_sent", count=self.count)
            if not self.authed and now - start > 45:
                raise TimeoutError("MFi authentication timeout")
            try:
                data = await asyncio.wait_for(self.s.recv_any(65535), 0.2)
            except TimeoutError:
                continue
            if not data:
                raise EOFError("CarKit connection closed")
            await self.feed(data)
