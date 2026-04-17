from __future__ import annotations

import shutil
from pathlib import Path

import pytest


FIXTURES = Path(__file__).parent / "fixtures"


def _copy_fixture(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination)


@pytest.fixture()
def mixed_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "sample_repo"
    repo_root.mkdir()
    _copy_fixture(FIXTURES / "python_service", repo_root / "backend")
    _copy_fixture(FIXTURES / "ts_app", repo_root / "frontend")
    return repo_root


@pytest.fixture(autouse=True)
def isolate_active_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPOBRAIN_ACTIVE_REPO_FILE", str(tmp_path / "active_repo.txt"))
