#!/usr/bin/env python3
"""Build canonical and WorkBuddy archives from explicit runtime inputs only."""

import hashlib
import sys
import zipfile
from pathlib import Path

from distribution import NAME, ROOT, runtime_files, workbuddy_manifest


def build(output, root=ROOT):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    files = runtime_files(root)
    artifacts = []
    for suffix in ["", "-workbuddy"]:
        archive_path = output / (NAME + suffix + ".zip")
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for source in files:
                relative = source.relative_to(root).as_posix()
                content = source.read_bytes()
                if suffix and relative == "SKILL.md":
                    content = workbuddy_manifest(content.decode()).encode()
                name = relative if suffix else NAME + "/" + relative
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, content)
        artifacts.append(archive_path)
    checksums = output / "SHA256SUMS"
    checksums.write_text(
        "".join(
            hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in artifacts
        )
    )
    return artifacts + [checksums]


if __name__ == "__main__":
    for artifact in build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"):
        print(artifact)
