"""Synthetic identities only; no Apple credential is used by the test suite."""

import base64
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import pkcs7
from cryptography.x509.oid import NameOID
from local_mfi_v3_helper import ProviderError, validate_identity


def make_certificate(key, ca=False):
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "UNTRUSTED TEST ONLY")])
    now = datetime.now(UTC)
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(minutes=5))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )


def encode_key(key, format=serialization.PrivateFormat.PKCS8):
    return key.private_bytes(serialization.Encoding.DER, format, serialization.NoEncryption())


def test_key_consistency_and_reject_wrong_curve_container_and_mismatch():
    key = ec.generate_private_key(ec.SECP256R1())
    cert = pkcs7.serialize_certificates([make_certificate(key)], serialization.Encoding.DER)
    assert validate_identity(cert, encode_key(key)).curve.name == "secp256r1"
    for candidate in [
        encode_key(ec.generate_private_key(ec.SECP256R1())),
        b"bad",
        encode_key(key, serialization.PrivateFormat.TraditionalOpenSSL),
        encode_key(ec.generate_private_key(ec.SECP384R1())),
    ]:
        with pytest.raises(ProviderError):
            validate_identity(cert, candidate)
    with pytest.raises(ProviderError):
        validate_identity(b"bad", encode_key(key))
    ca = pkcs7.serialize_certificates([make_certificate(key, ca=True)], serialization.Encoding.DER)
    with pytest.raises(ProviderError):
        validate_identity(ca, encode_key(key))


def test_helper_jsonl_signs_prehashed_and_rejects_wrong_length(tmp_path):
    key = ec.generate_private_key(ec.SECP256R1())
    cert = pkcs7.serialize_certificates([make_certificate(key)], serialization.Encoding.DER)
    cert_file, key_file = tmp_path / "test.p7b", tmp_path / "test.pk8"
    cert_file.write_bytes(cert)
    key_file.write_bytes(encode_key(key))
    env = dict(
        os.environ, ACCESSORY_MFI_CERT_FILE=str(cert_file), ACCESSORY_MFI_KEY_FILE=str(key_file)
    )
    digest = b"Q" * 32
    requests = [
        {"op": "certificate"},
        {"op": "sign", "challenge": base64.b64encode(digest).decode()},
        {"op": "sign", "challenge": "AQ=="},
    ]
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parents[1] / "scripts/local_mfi_v3_helper.py")],
        input="\n".join(json.dumps(x) for x in requests) + "\n",
        text=True,
        capture_output=True,
        env=env,
        timeout=10,
        check=True,
    )
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert base64.b64decode(responses[0]["certificate"]) == cert
    raw = base64.b64decode(responses[1]["signature"])
    assert len(raw) == 64
    r, s = int.from_bytes(raw[:32], "big"), int.from_bytes(raw[32:], "big")
    key.public_key().verify(
        utils.encode_dss_signature(r, s), digest, ec.ECDSA(utils.Prehashed(hashes.SHA256()))
    )
    assert "exactly 32" in responses[2]["error"]
