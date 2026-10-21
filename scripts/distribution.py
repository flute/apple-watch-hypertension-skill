"""One allowlist for installation and release packaging; never include local runtime data."""

from pathlib import Path

NAME = "apple-watch-hypertension"
ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = [
    "SKILL.md",
    "install.command",
    "README.md",
    "README.en.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "pyproject.toml",
    "uv.lock",
]


def runtime_files(root=ROOT):
    root = Path(root)
    result = [root / name for name in TOP_FILES]
    result += [p for p in (root / "scripts").rglob("*.py") if "__pycache__" not in p.parts]
    result += [root / "scripts/local-only.sb", root / "scripts/run.command"]
    result += list((root / "references").glob("*.md"))
    result += list((root / "references").glob("*.json"))
    for path in result:
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing or symlinked release input: " + str(path.relative_to(root)))
    return sorted(set(result))


def workbuddy_manifest(text):
    head, body = text.split("---", 2)[1:]
    extra = """version: "0.2.2"
author: flute
display_name: Apple Watch 高血压通知地区开通
display_name_en: Apple Watch Hypertension Notifications
description_zh: 帮助尚未开放高血压通知地区的用户开通 Apple Watch 高血压通知，完成后恢复真实定位并复查通知。
description_en: Set up and verify Apple Watch hypertension notifications on macOS with human assistance and real-location restoration.
"""
    return "---\n" + head.strip() + "\n" + extra + "---" + body
