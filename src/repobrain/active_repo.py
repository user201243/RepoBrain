from __future__ import annotations

import os
from pathlib import Path

ACTIVE_REPO_FILE_ENV = "REPOBRAIN_ACTIVE_REPO_FILE"


def active_repo_file() -> Path:
    override = os.getenv(ACTIVE_REPO_FILE_ENV)
    if override:
        return Path(override)
    return Path.home() / ".repobrain" / "active_repo.txt"


def read_active_repo() -> Path | None:
    path = active_repo_file()
    if not path.exists():
        return None
    raw_value = path.read_text(encoding="utf-8").strip()
    if not raw_value:
        return None
    repo_root = Path(raw_value).expanduser().resolve()
    if not repo_root.exists():
        return None
    return repo_root


def write_active_repo(repo_root: str | Path) -> Path:
    resolved = Path(repo_root).expanduser().resolve()
    path = active_repo_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(resolved), encoding="utf-8")
    return path


def resolve_repo_root(repo_arg: str | Path | None, *, prefer_active: bool = True) -> Path:
    if repo_arg:
        return Path(repo_arg).expanduser().resolve()
    if prefer_active:
        active_repo = read_active_repo()
        if active_repo is not None:
            return active_repo
    return Path(".").resolve()
