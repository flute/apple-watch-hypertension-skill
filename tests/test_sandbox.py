import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS sandbox-exec")
def test_sender_sandbox_denies_ip_but_allows_unix_socket_pair():
    profile = Path(__file__).resolve().parents[1] / "scripts/local-only.sb"
    source = """import socket
left, right = socket.socketpair()
left.sendall(b"local")
assert right.recv(5) == b"local"
left.close(); right.close()
s = socket.socket()
try:
    s.connect(("127.0.0.1", 9))
except PermissionError:
    print("IP denied; Unix sockets allowed")
else:
    raise AssertionError("IP networking was not denied")
finally:
    s.close()
"""
    result = subprocess.run(
        ["/usr/bin/sandbox-exec", "-f", str(profile), sys.executable, "-c", source],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert "IP denied" in result.stdout
