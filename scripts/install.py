#!/usr/bin/env python3
"""Copy this skill without dependencies, credentials, build files or overwriting an installation."""

import argparse
import shutil
import sys
from pathlib import Path

from distribution import NAME, ROOT, runtime_files


def install(parent, root=ROOT):
    parent = Path(parent).expanduser().resolve()
    destination = parent / NAME
    if destination.exists() or destination.is_symlink():
        raise ValueError(
            "Installation exists; choose a new directory or move the old copy yourself"
        )
    parent.mkdir(parents=True, exist_ok=True)
    files = runtime_files(root)
    destination.mkdir()
    try:
        for source in files:
            target = destination / source.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--agent", choices=["codex", "claude"])
    target.add_argument(
        "--target", type=Path, help="Parent skills directory of another local agent"
    )
    args = parser.parse_args(argv)
    parent = args.target
    if args.agent:
        parent = Path.home() / (".agents/skills" if args.agent == "codex" else ".claude/skills")
    try:
        print(install(parent))
    except (OSError, ValueError) as error:
        print("Installation failed: " + str(error), file=sys.stderr)
        return 1
    print("Reload skills or start a new conversation. No device settings were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
