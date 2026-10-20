"""Offline installation scenarios: no Python/Git on PATH, spaces and cancellation."""

import os
import subprocess
from pathlib import Path

import pytest
from distribution import ROOT


def test_beginner_launcher_is_distributed():
    from distribution import runtime_files

    files = {p.relative_to(ROOT).as_posix() for p in runtime_files()}
    assert {
        "install.command",
        "scripts/run.command",
        "references/beginner.zh-CN.md",
        "references/beginner.en.md",
        "references/agents.md",
    } <= files


def test_cancel_does_not_download_or_write(tmp_path):
    env = dict(os.environ, HOME=str(tmp_path))
    result = subprocess.run(
        ["/bin/bash", str(ROOT / "install.command")],
        input="q\n",
        text=True,
        capture_output=True,
        env=env,
    )
    assert result.returncode == 0
    assert not list(tmp_path.iterdir())


def test_installer_without_python_git_or_uv_on_path(tmp_path):
    home = tmp_path / "小白 home"
    home.mkdir()
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "uname").write_text("#!/bin/sh\nprintf 'Darwin\\n'\n")
    (bindir / "uname").chmod(0o755)
    # Built-in macOS utilities only; fake uv records the runtime setup contract.
    for name in ["dirname", "mkdir", "chmod", "mktemp", "rm", "cp"]:
        import shutil

        (bindir / name).symlink_to(shutil.which(name))
    tools = home / "Library/Application Support/apple-watch-hypertension/tools"
    tools.mkdir(parents=True)
    uv = tools / "uv"
    python = Path(os.sys.executable)
    uv.write_text(
        "#!/bin/bash\n"
        "if [[ \"$1\" == --version ]]; then echo 'uv 0.9.25'; exit 0; fi\n"
        'if [[ "$1" == run ]]; then shift 6; exec ' + repr(str(python)) + ' "$@"; fi\n'
        'if [[ "$1" == sync ]]; then echo runtime-ready; exit 0; fi\n'
        "exit 90\n"
    )
    uv.chmod(0o755)
    result = subprocess.run(
        ["/bin/bash", str(ROOT / "install.command"), "--agent", "codex"],
        text=True,
        capture_output=True,
        env=dict(os.environ, HOME=str(home), PATH=str(bindir)),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (home / ".agents/skills/apple-watch-hypertension/SKILL.md").is_file()
    assert "runtime-ready" in result.stdout
    second = subprocess.run(
        ["/bin/bash", str(ROOT / "install.command"), "--agent", "codex"],
        text=True,
        capture_output=True,
        env=dict(os.environ, HOME=str(home), PATH=str(bindir)),
    )
    assert second.returncode != 0


@pytest.mark.parametrize("failure", ["network", "checksum"])
def test_bootstrap_failure_never_installs_skill(tmp_path, failure):
    import shutil

    home = tmp_path / "home"
    home.mkdir()
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for name in ["dirname", "mkdir", "chmod", "mktemp", "rm", "shasum"]:
        (bindir / name).symlink_to(shutil.which(name))
    (bindir / "uname").write_text(
        '#!/bin/sh\nif [ "$1" = -s ]; then echo Darwin; else echo arm64; fi\n'
    )
    (bindir / "uname").chmod(0o755)
    curl = bindir / "curl"
    if failure == "network":
        curl.write_text("#!/bin/sh\nexit 22\n")
    else:
        curl.write_text(
            "#!/bin/bash\nwhile [[ $# -gt 0 ]]; do\n"
            'if [[ "$1" == -o ]]; then printf corrupted > "$2"; exit 0; fi\n'
            "shift\ndone\nexit 99\n"
        )
    curl.chmod(0o755)
    result = subprocess.run(
        ["/bin/bash", str(ROOT / "install.command"), "--agent", "claude"],
        text=True,
        capture_output=True,
        env=dict(os.environ, HOME=str(home), PATH=str(bindir)),
    )
    assert result.returncode != 0
    assert not (home / ".claude").exists()
    assert not (home / "Library").exists()
    assert "Setup complete" not in result.stdout
