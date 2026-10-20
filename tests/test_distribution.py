import hashlib
import zipfile
from pathlib import Path

import pytest
import yaml
from build_release import build
from distribution import NAME, ROOT, runtime_files
from install import install


def test_installer_copies_complete_skill_and_refuses_overwrite(tmp_path):
    result = install(tmp_path)
    assert (result / "SKILL.md").exists()
    assert (result / "scripts/bpkit/runner.py").exists()
    assert not (result / "tests").exists()
    assert not (result / ".venv").exists()
    with pytest.raises(ValueError):
        install(tmp_path)


def test_artifacts_have_correct_roots_metadata_and_checksums(tmp_path):
    artifacts = build(tmp_path)
    with zipfile.ZipFile(artifacts[0]) as archive:
        assert NAME + "/SKILL.md" in archive.namelist()
    with zipfile.ZipFile(artifacts[1]) as archive:
        assert "SKILL.md" in archive.namelist()
        metadata = yaml.safe_load(archive.read("SKILL.md").decode().split("---")[1])
        assert all(k in metadata for k in ["description_zh", "description_en", "version", "author"])
        assert metadata["name"] == NAME
        for name in archive.namelist():
            assert not name.endswith((".pk8", ".p7b", ".apk", ".log", ".jsonl"))
            assert not any(part in name.split("/") for part in [".git", ".venv", "__pycache__"])
    for line in artifacts[2].read_text().splitlines():
        digest, filename = line.split()
        assert hashlib.sha256((tmp_path / filename).read_bytes()).hexdigest() == digest
    assert build(tmp_path / "second")[0].read_bytes() == artifacts[0].read_bytes()


def test_skill_links_resolve_and_required_resources_ship():
    import re

    files = {p.relative_to(ROOT).as_posix() for p in runtime_files()}
    for filename in ["SKILL.md", "references/operations.md"]:
        for link in re.findall(r"\]\(([^)]+)\)", (ROOT / filename).read_text()):
            if not link.startswith("https://"):
                assert (Path(filename).parent / link).as_posix() in files
