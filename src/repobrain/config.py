from __future__ import annotations

import json
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _string_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _strip_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    return json.dumps(str(value))


def load_env_file(repo_root: str | Path) -> Path | None:
    env_path = Path(repo_root).resolve() / ".env"
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = _strip_env_value(value)
    return env_path


@dataclass(slots=True)
class ProjectConfig:
    name: str = "RepoBrain"
    repo_roots: list[str] = field(default_factory=lambda: ["."])
    state_dir: str = ".repobrain"
    context_budget: int = 12000


@dataclass(slots=True)
class IndexingConfig:
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(
        default_factory=lambda: [
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            ".pytest_cache",
            ".pytest_tmp",
            "pytest_tmp",
            "pytest_tmp_run",
            "pytest-cache-files-*",
            "node_modules",
            "dist",
            "build",
            ".repobrain",
        ]
    )
    max_file_size_bytes: int = 200_000
    chunk_max_lines: int = 80
    chunk_overlap_lines: int = 12


@dataclass(slots=True)
class ProviderConfig:
    embedding: str = "local"
    reranker: str = "local"
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ParsingConfig:
    prefer_tree_sitter: bool = True
    tree_sitter_languages: list[str] = field(default_factory=lambda: ["python", "typescript", "javascript"])


@dataclass(slots=True)
class RepoBrainConfig:
    project: ProjectConfig = field(default_factory=ProjectConfig)
    indexing: IndexingConfig = field(default_factory=IndexingConfig)
    parsing: ParsingConfig = field(default_factory=ParsingConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    config_path: Path | None = None
    repo_root: Path | None = None

    @property
    def resolved_repo_root(self) -> Path:
        if self.repo_root is None:
            raise RuntimeError("Repo root is not configured.")
        return self.repo_root

    @property
    def state_path(self) -> Path:
        return self.resolved_repo_root / self.project.state_dir

    @property
    def metadata_db_path(self) -> Path:
        return self.state_path / "metadata.db"

    @property
    def vectors_dir(self) -> Path:
        return self.state_path / "vectors"

    @property
    def cache_dir(self) -> Path:
        return self.state_path / "cache"

    @classmethod
    def default(cls, repo_root: str | Path) -> "RepoBrainConfig":
        root = Path(repo_root).resolve()
        return cls(config_path=root / "repobrain.toml", repo_root=root)

    @classmethod
    def load(cls, repo_root: str | Path) -> "RepoBrainConfig":
        root = Path(repo_root).resolve()
        load_env_file(root)
        config_path = root / "repobrain.toml"
        base = cls.default(root)
        if not config_path.exists():
            return base

        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        project_data = data.get("project", {})
        indexing_data = data.get("indexing", {})
        parsing_data = data.get("parsing", {})
        providers_data = data.get("providers", {})

        base.project = ProjectConfig(
            name=str(project_data.get("name", base.project.name)),
            repo_roots=_string_list(project_data.get("repo_roots", base.project.repo_roots)),
            state_dir=str(project_data.get("state_dir", base.project.state_dir)),
            context_budget=int(project_data.get("context_budget", base.project.context_budget)),
        )
        base.indexing = IndexingConfig(
            include=_string_list(indexing_data.get("include", base.indexing.include)),
            exclude=_string_list(indexing_data.get("exclude", base.indexing.exclude)),
            max_file_size_bytes=int(indexing_data.get("max_file_size_bytes", base.indexing.max_file_size_bytes)),
            chunk_max_lines=int(indexing_data.get("chunk_max_lines", base.indexing.chunk_max_lines)),
            chunk_overlap_lines=int(indexing_data.get("chunk_overlap_lines", base.indexing.chunk_overlap_lines)),
        )
        base.parsing = ParsingConfig(
            prefer_tree_sitter=bool(parsing_data.get("prefer_tree_sitter", base.parsing.prefer_tree_sitter)),
            tree_sitter_languages=_string_list(
                parsing_data.get("tree_sitter_languages", base.parsing.tree_sitter_languages)
            ),
        )
        provider_options = {k: v for k, v in providers_data.items() if k not in {"embedding", "reranker"}}
        base.providers = ProviderConfig(
            embedding=str(providers_data.get("embedding", base.providers.embedding)),
            reranker=str(providers_data.get("reranker", base.providers.reranker)),
            options=provider_options,
        )
        base.config_path = config_path
        base.repo_root = root
        return base

    def write_default(self, force: bool = False) -> Path:
        if self.config_path is None:
            self.config_path = self.resolved_repo_root / "repobrain.toml"
        if self.config_path.exists() and not force:
            return self.config_path

        provider_lines = [
            "[providers]",
            f'embedding = "{self.providers.embedding}"',
            f'reranker = "{self.providers.reranker}"',
        ]
        provider_lines.extend(
            f"{key} = {_toml_value(value)}"
            for key, value in sorted(self.providers.options.items())
        )
        self.config_path.write_text(
            "\n".join(
                [
                    "[project]",
                    f"name = {_toml_value(self.project.name)}",
                    f"repo_roots = {_toml_value(self.project.repo_roots)}",
                    f"state_dir = {_toml_value(self.project.state_dir)}",
                    f"context_budget = {self.project.context_budget}",
                    "",
                    "[indexing]",
                    f"include = {_toml_value(self.indexing.include)}",
                    f"exclude = {_toml_value(self.indexing.exclude)}",
                    f"max_file_size_bytes = {self.indexing.max_file_size_bytes}",
                    f"chunk_max_lines = {self.indexing.chunk_max_lines}",
                    f"chunk_overlap_lines = {self.indexing.chunk_overlap_lines}",
                    "",
                    "[parsing]",
                    f"prefer_tree_sitter = {str(self.parsing.prefer_tree_sitter).lower()}",
                    f"tree_sitter_languages = {_toml_value(self.parsing.tree_sitter_languages)}",
                    "",
                    *provider_lines,
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return self.config_path
