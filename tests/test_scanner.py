from __future__ import annotations

from pathlib import Path

from repobrain.config import RepoBrainConfig
from repobrain.engine.scanner import FileCandidate, ParseArtifacts, RepositoryScanner
from repobrain.models import Symbol


class StubParserAdapter:
    name = "tree_sitter_stub"

    def __init__(self, languages: set[str]) -> None:
        self.languages = languages

    def can_parse(self, language: str) -> bool:
        return language in self.languages

    def parse(self, candidate: FileCandidate, content: str, scanner: RepositoryScanner) -> ParseArtifacts | None:
        if not self.can_parse(candidate.language):
            return None
        return ParseArtifacts(
            symbols=[Symbol("from_stub", "function", 1, 1, "def from_stub():")],
            imports=["stub.import"],
            parser_name=self.name,
            parser_detail="test-stub",
        )

    def describe_language(self, language: str) -> dict[str, object]:
        ready = self.can_parse(language)
        return {"ready": ready, "source": "test-stub" if ready else "", "error": "" if ready else "disabled"}


def test_scanner_prefers_optional_parser_when_ready(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "service.py").write_text("def real_symbol():\n    return True\n", encoding="utf-8")

    config = RepoBrainConfig.default(repo_root)
    scanner = RepositoryScanner(config, parser_adapters=[StubParserAdapter({"python"})])
    candidate = scanner.scan()[0]
    document = scanner.parse(candidate)

    assert document.parser_name == "tree_sitter_stub"
    assert document.parser_detail == "test-stub"
    assert document.symbols[0].name == "from_stub"
    assert scanner.capabilities()["language_parsers"]["python"]["selected"] == "tree_sitter_stub"


def test_scanner_falls_back_to_heuristic_when_optional_parser_disabled(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "service.py").write_text("def real_symbol():\n    return True\n", encoding="utf-8")

    config = RepoBrainConfig.default(repo_root)
    config.parsing.prefer_tree_sitter = False
    scanner = RepositoryScanner(config, parser_adapters=[StubParserAdapter({"python"})])
    candidate = scanner.scan()[0]
    document = scanner.parse(candidate)

    assert document.parser_name == "heuristic"
    assert document.symbols[0].name == "real_symbol"
    assert scanner.capabilities()["language_parsers"]["python"]["selected"] == "heuristic"


def test_python_named_imports_create_import_call_edges(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "route.py").write_text(
        "from services.auth import login_with_google as start_google\n\n"
        "def handler():\n"
        "    return start_google()\n",
        encoding="utf-8",
    )

    config = RepoBrainConfig.default(repo_root)
    config.parsing.prefer_tree_sitter = False
    scanner = RepositoryScanner(config, parser_adapters=[])
    document = scanner.parse(scanner.scan()[0])

    assert "start_google" in document.imports
    assert any(edge.edge_type == "imports_call" and edge.target == "start_google" for edge in document.edges)


def test_typescript_named_imports_create_import_call_edges(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "route.ts").write_text(
        'import { handleGitHubCallback as handleCallback } from "../services/oauth";\n\n'
        "export async function githubCallback(code: string) {\n"
        "  return handleCallback(code);\n"
        "}\n",
        encoding="utf-8",
    )

    config = RepoBrainConfig.default(repo_root)
    config.parsing.prefer_tree_sitter = False
    scanner = RepositoryScanner(config, parser_adapters=[])
    document = scanner.parse(scanner.scan()[0])

    assert "handleCallback" in document.imports
    assert any(edge.edge_type == "imports_call" and edge.target == "handleCallback" for edge in document.edges)
