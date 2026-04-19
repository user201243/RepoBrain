from __future__ import annotations

import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from repobrain.config import RepoBrainConfig
from repobrain.engine.providers import EmbeddingProvider, tokenize
from repobrain.engine.scanner import FileCandidate, RepositoryScanner
from repobrain.engine.store import MetadataStore
from repobrain.models import FileEvidence, ParsedDocument, PatchReviewChange, PatchReviewReport


@dataclass(slots=True)
class _PatchChangeSeed:
    file_path: str
    status: str
    previous_path: str | None = None


@dataclass(slots=True)
class _PatchItem:
    change: PatchReviewChange
    candidate: FileCandidate | None = None
    document: ParsedDocument | None = None


class PatchReviewer:
    def __init__(
        self,
        config: RepoBrainConfig,
        scanner: RepositoryScanner,
        store: MetadataStore,
        embedder: EmbeddingProvider,
    ) -> None:
        self.config = config
        self.scanner = scanner
        self.store = store
        self.embedder = embedder

    def review(self, *, base: str | None = None, files: list[str] | None = None) -> PatchReviewReport:
        if base and files:
            raise ValueError("`patch-review` accepts either `base` or `files`, not both.")
        if not self.store.indexed():
            raise RuntimeError("Repository has not been indexed yet. Run `repobrain index` first.")

        mode = "working_tree"
        base_ref: str | None = None
        if files:
            mode = "files"
            seeds = self._file_list_changes(files)
        elif base:
            mode = "base"
            base_ref = str(base).strip() or None
            seeds = self._git_base_changes(base_ref or "")
        else:
            seeds = self._git_working_tree_changes()

        patch_items = self._build_patch_items(seeds, mode=mode)
        changed_files = [item.change for item in patch_items]
        supported_items = [item for item in patch_items if item.change.supported]

        warnings: list[str] = []
        if not changed_files:
            warnings.append("No supported changed files were detected for patch review.")

        changed_paths = [item.change.file_path for item in patch_items]
        changed_targets = self._changed_targets(supported_items)
        related_edges = self.store.get_related_edges(changed_paths, targets=changed_targets, limit=48)
        related_files, structural_counts = self._related_files_from_edges(related_edges, changed_paths, changed_targets)
        candidate_files = self._candidate_files(supported_items, changed_paths, changed_targets, related_files, structural_counts)

        adjacent_files = [item for item in candidate_files if item.role not in {"test", "config"}][:5]
        suggested_tests = [item for item in candidate_files if item.role == "test"][:4]
        config_surfaces = [item for item in candidate_files if item.role == "config"][:4]

        warnings.extend(self._warnings(patch_items, adjacent_files, suggested_tests, config_surfaces, structural_counts))
        risk_score = self._risk_score(patch_items, suggested_tests, config_surfaces)
        risk_label = self._risk_label(risk_score)
        summary = self._summary(changed_files, adjacent_files, suggested_tests, config_surfaces, risk_label)
        next_steps = self._next_steps(adjacent_files, suggested_tests, config_surfaces, warnings)

        return PatchReviewReport(
            repo_root=str(self.config.resolved_repo_root),
            mode=mode,
            base_ref=base_ref,
            changed_files=changed_files,
            adjacent_files=adjacent_files,
            suggested_tests=suggested_tests,
            config_surfaces=config_surfaces,
            risk_score=risk_score,
            risk_label=risk_label,
            summary=summary,
            warnings=self._dedupe_strings(warnings),
            next_steps=next_steps,
        )

    def _build_patch_items(self, seeds: list[_PatchChangeSeed], *, mode: str) -> list[_PatchItem]:
        record_map = {
            row["path"]: row
            for row in self.store.get_file_records([seed.file_path for seed in seeds] + [seed.previous_path for seed in seeds if seed.previous_path])
        }
        items: list[_PatchItem] = []
        for seed in seeds:
            candidate = self.scanner.candidate_for_path(seed.file_path)
            document: ParsedDocument | None = None
            symbols: list[str] = []
            language = "unknown"
            role = self.scanner.detect_role(seed.file_path)
            supported = candidate is not None
            exists = (self.config.resolved_repo_root / seed.file_path).exists()

            if candidate is not None:
                document = self.scanner.parse(candidate)
                language = candidate.language
                role = candidate.role
                symbols = [symbol.name for symbol in document.symbols[:6]]
            else:
                row = record_map.get(seed.file_path) or record_map.get(seed.previous_path or "")
                if row is not None:
                    language = str(row["language"])
                    role = str(row["role"])
            if seed.status == "selected":
                exists = exists
            change = PatchReviewChange(
                file_path=seed.file_path,
                status=seed.status,
                exists=exists,
                supported=supported,
                language=language,
                role=role,
                previous_path=seed.previous_path,
                symbols=symbols,
            )
            if mode == "files" and not exists:
                change.exists = False
            items.append(_PatchItem(change=change, candidate=candidate, document=document))
        return items

    def _git_working_tree_changes(self) -> list[_PatchChangeSeed]:
        output = self._git("status", "--porcelain=1", "--untracked-files=all")
        seeds: list[_PatchChangeSeed] = []
        for raw_line in output.splitlines():
            line = raw_line.rstrip()
            if not line:
                continue
            status_code = line[:2]
            payload = line[3:].strip()
            if status_code == "??":
                seeds.append(_PatchChangeSeed(file_path=self._normalize_rel_path(payload), status="untracked"))
                continue
            previous_path: str | None = None
            file_path = payload
            if " -> " in payload:
                previous_raw, file_raw = payload.split(" -> ", 1)
                previous_path = self._normalize_rel_path(previous_raw)
                file_path = file_raw
            normalized_path = self._normalize_rel_path(file_path)
            status = self._status_from_code(status_code)
            seeds.append(_PatchChangeSeed(file_path=normalized_path, status=status, previous_path=previous_path))
        return self._dedupe_changes(seeds)

    def _git_base_changes(self, base_ref: str) -> list[_PatchChangeSeed]:
        if not base_ref:
            raise ValueError("`base` is required for base patch review.")
        merge_base = self._git("merge-base", base_ref, "HEAD").strip()
        if not merge_base:
            raise ValueError(f"Unable to resolve merge-base for `{base_ref}`.")
        output = self._git("diff", "--name-status", "--find-renames", merge_base, "HEAD")
        seeds: list[_PatchChangeSeed] = []
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split("\t")
            code = parts[0]
            if code.startswith("R") and len(parts) >= 3:
                seeds.append(
                    _PatchChangeSeed(
                        file_path=self._normalize_rel_path(parts[2]),
                        status="renamed",
                        previous_path=self._normalize_rel_path(parts[1]),
                    )
                )
            elif code.startswith("D") and len(parts) >= 2:
                seeds.append(_PatchChangeSeed(file_path=self._normalize_rel_path(parts[1]), status="deleted"))
            elif code.startswith("A") and len(parts) >= 2:
                seeds.append(_PatchChangeSeed(file_path=self._normalize_rel_path(parts[1]), status="added"))
            elif len(parts) >= 2:
                seeds.append(_PatchChangeSeed(file_path=self._normalize_rel_path(parts[1]), status="modified"))
        return self._dedupe_changes(seeds)

    def _file_list_changes(self, files: list[str]) -> list[_PatchChangeSeed]:
        seeds: list[_PatchChangeSeed] = []
        for raw_path in files:
            cleaned = str(raw_path).strip()
            if not cleaned:
                continue
            path = Path(cleaned)
            if path.is_absolute():
                raise ValueError("`patch-review --files` accepts repo-relative paths only.")
            normalized = self._normalize_rel_path(cleaned)
            if normalized.startswith("../"):
                raise ValueError("`patch-review --files` paths must stay within the repo root.")
            seeds.append(_PatchChangeSeed(file_path=normalized, status="selected"))
        if not seeds:
            raise ValueError("`patch-review --files` requires at least one repo-relative path.")
        return self._dedupe_changes(seeds)

    def _candidate_files(
        self,
        patch_items: list[_PatchItem],
        changed_paths: list[str],
        changed_targets: list[str],
        related_files: dict[str, int],
        structural_counts: dict[str, int],
    ) -> list[FileEvidence]:
        if not patch_items:
            return []

        query_text = self._candidate_query_text(patch_items)
        file_scores: dict[str, float] = defaultdict(float)
        file_roles: dict[str, str] = {}
        file_languages: dict[str, str] = {}
        file_reasons: dict[str, set[str]] = defaultdict(set)
        changed_set = set(changed_paths)
        query_tokens = set(tokenize(query_text))

        for rank, hit in enumerate(self.store.search_fts(query_text, limit=24), start=1):
            if hit.file_path in changed_set:
                continue
            file_scores[hit.file_path] += max(1.1 - (rank * 0.03), 0.1)
            file_roles[hit.file_path] = hit.role
            file_languages[hit.file_path] = hit.language
            file_reasons[hit.file_path].update(hit.reasons)

        for rank, hit in enumerate(self.store.search_vectors(query_text, self.embedder, limit=24), start=1):
            if hit.file_path in changed_set:
                continue
            file_scores[hit.file_path] += max(float(hit.score) * 0.9, 0.05) + max(0.4 - (rank * 0.01), 0.0)
            file_roles[hit.file_path] = hit.role
            file_languages[hit.file_path] = hit.language
            file_reasons[hit.file_path].update(hit.reasons)

        for file_path, edge_count in related_files.items():
            if file_path in changed_set:
                continue
            file_scores[file_path] += min(edge_count * 0.28, 0.84)
            file_reasons[file_path].add("structural_neighbor")

        for file_path, file_score in list(file_scores.items()):
            path_tokens = set(tokenize(file_path.replace("/", " ").replace(".", " ")))
            overlap = len(query_tokens & path_tokens)
            if overlap:
                file_scores[file_path] = file_score + min(overlap * 0.08, 0.24)
                file_reasons[file_path].add("path_overlap")
            if structural_counts.get(file_path, 0) >= 2:
                file_scores[file_path] += 0.12
                file_reasons[file_path].add("multi_edge_support")
            if file_roles.get(file_path) == "test":
                file_scores[file_path] += 0.1
            if file_roles.get(file_path) == "config":
                file_scores[file_path] += 0.08

        for token in changed_targets:
            for file_path in list(file_scores):
                if token and token in file_path.lower():
                    file_scores[file_path] += 0.05
                    file_reasons[file_path].add("symbol_hint")

        ranked: list[FileEvidence] = []
        for file_path, score in sorted(file_scores.items(), key=lambda item: item[1], reverse=True):
            ranked.append(
                FileEvidence(
                    file_path=file_path,
                    language=file_languages.get(file_path, "unknown"),
                    role=file_roles.get(file_path, self.scanner.detect_role(file_path)),
                    score=round(score, 6),
                    reasons=sorted(file_reasons[file_path]),
                )
            )
        return ranked[:10]

    def _candidate_query_text(self, patch_items: list[_PatchItem]) -> str:
        terms: list[str] = []
        for item in patch_items:
            terms.extend(tokenize(item.change.file_path.replace("/", " ")))
            terms.extend(tokenize(item.change.previous_path or ""))
            terms.extend(tokenize(" ".join(item.change.symbols)))
            if item.document is not None:
                terms.extend(tokenize(" ".join(item.document.imports[:6])))
                terms.extend(tokenize(" ".join(item.document.hints[:4])))
                for symbol in item.document.symbols[:4]:
                    terms.extend(tokenize(symbol.signature))
        deduped: list[str] = []
        for term in terms:
            if len(term) < 3 or term in deduped:
                continue
            deduped.append(term)
        return " ".join(deduped[:18]) or "patch review changed files"

    def _related_files_from_edges(
        self,
        edges: list[dict[str, str | None]],
        changed_paths: list[str],
        changed_targets: list[str],
    ) -> tuple[dict[str, int], dict[str, int]]:
        changed_set = set(changed_paths)
        target_tokens = {item.lower() for item in changed_targets}
        related_files: dict[str, int] = defaultdict(int)
        structural_counts: dict[str, int] = defaultdict(int)

        for edge in edges:
            source_file = str(edge.get("source_file", "") or "").strip()
            target_file = str(edge.get("target_file", "") or "").strip()
            target = str(edge.get("target", "") or "").strip().lower()

            if source_file and source_file not in changed_set and (target_file in changed_set or target in target_tokens):
                related_files[source_file] += 1
                structural_counts[source_file] += 1
            if target_file and target_file not in changed_set and source_file in changed_set:
                related_files[target_file] += 1
                structural_counts[target_file] += 1
        return related_files, structural_counts

    def _changed_targets(self, patch_items: list[_PatchItem]) -> list[str]:
        targets: list[str] = []
        for item in patch_items:
            targets.extend(symbol.lower() for symbol in item.change.symbols if symbol)
            if item.document is not None:
                targets.extend(import_name.lower() for import_name in item.document.imports[:8] if import_name)
        deduped: list[str] = []
        for target in targets:
            if target and target not in deduped:
                deduped.append(target)
        return deduped

    def _warnings(
        self,
        patch_items: list[_PatchItem],
        adjacent_files: list[FileEvidence],
        suggested_tests: list[FileEvidence],
        config_surfaces: list[FileEvidence],
        structural_counts: dict[str, int],
    ) -> list[str]:
        warnings: list[str] = []
        if any(item.change.role == "config" for item in patch_items) or config_surfaces:
            warnings.append("Patch touches configuration or auth wiring surfaces. Re-check env and callback settings before shipping.")
        if any(item.change.status in {"deleted", "renamed"} for item in patch_items):
            warnings.append("Patch includes deleted or renamed files. Re-check imports, callbacks, and packaging paths.")
        if not suggested_tests:
            warnings.append("No obvious test coverage was found for this patch. Add or run targeted tests before merging.")
        if len(adjacent_files) <= 1:
            warnings.append("Evidence is concentrated in one nearby file. Inspect the surrounding runtime surface manually.")
        if adjacent_files and max(structural_counts.values(), default=0) <= 1:
            warnings.append("Structural adjacency is weak. Cross-check imports and callbacks manually before editing more files.")
        if not any(item.change.supported for item in patch_items):
            warnings.append("No supported changed files were detected for code-aware patch review.")
        return warnings

    def _risk_score(
        self,
        patch_items: list[_PatchItem],
        suggested_tests: list[FileEvidence],
        config_surfaces: list[FileEvidence],
    ) -> float:
        score = 0.20
        score += min(max(len(patch_items) - 1, 0) * 0.15, 0.30)
        if any(item.change.role == "config" for item in patch_items) or config_surfaces:
            score += 0.20
        if not suggested_tests:
            score += 0.15
        if any(item.change.status in {"deleted", "renamed"} for item in patch_items):
            score += 0.15
        role_families = {self._role_family(item.change.role) for item in patch_items if self._role_family(item.change.role)}
        if len(role_families) > 1:
            score += 0.10
        return round(max(0.05, min(score, 0.95)), 3)

    def _risk_label(self, risk_score: float) -> str:
        if risk_score < 0.35:
            return "low"
        if risk_score < 0.65:
            return "moderate"
        return "high"

    def _summary(
        self,
        changed_files: list[PatchReviewChange],
        adjacent_files: list[FileEvidence],
        suggested_tests: list[FileEvidence],
        config_surfaces: list[FileEvidence],
        risk_label: str,
    ) -> str:
        return (
            f"Patch review found {len(changed_files)} changed file(s), {len(adjacent_files)} adjacent runtime file(s), "
            f"{len(suggested_tests)} suggested test surface(s), and {len(config_surfaces)} config surface(s). "
            f"Overall patch risk is {risk_label}."
        )

    def _next_steps(
        self,
        adjacent_files: list[FileEvidence],
        suggested_tests: list[FileEvidence],
        config_surfaces: list[FileEvidence],
        warnings: list[str],
    ) -> list[str]:
        steps: list[str] = []
        if adjacent_files:
            steps.append(f"Inspect adjacent runtime files first: {', '.join(item.file_path for item in adjacent_files[:2])}.")
        if suggested_tests:
            steps.append(f"Run or update targeted tests: {', '.join(item.file_path for item in suggested_tests[:2])}.")
        if config_surfaces:
            steps.append(f"Verify config and callback wiring in: {', '.join(item.file_path for item in config_surfaces[:2])}.")
        if any("No obvious test coverage" in warning for warning in warnings):
            steps.append("Add a focused regression test before merging this patch.")
        return self._dedupe_strings(steps)[:4]

    def _git(self, *args: str) -> str:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=self.config.resolved_repo_root,
                text=True,
                capture_output=True,
                check=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Git is required for patch-review working-tree and base modes.") from exc
        except subprocess.CalledProcessError as exc:
            error_text = (exc.stderr or exc.stdout or "").strip()
            if "not a git repository" in error_text.lower():
                raise RuntimeError("Patch review working-tree and base modes require a git repository. Use `--files` outside git.") from exc
            if args and args[0] == "merge-base":
                raise ValueError(f"Invalid base ref `{args[1]}` for patch review.") from exc
            raise RuntimeError(error_text or "Git command failed during patch review.") from exc
        return completed.stdout

    def _status_from_code(self, status_code: str) -> str:
        if "R" in status_code:
            return "renamed"
        if "D" in status_code:
            return "deleted"
        if "A" in status_code:
            return "added"
        return "modified"

    def _normalize_rel_path(self, raw_path: str) -> str:
        normalized = str(Path(raw_path.strip())).replace("\\", "/")
        return normalized.lstrip("./")

    def _dedupe_changes(self, seeds: list[_PatchChangeSeed]) -> list[_PatchChangeSeed]:
        seen: set[tuple[str, str, str | None]] = set()
        deduped: list[_PatchChangeSeed] = []
        for seed in seeds:
            key = (seed.file_path, seed.status, seed.previous_path)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(seed)
        return deduped

    def _role_family(self, role: str) -> str:
        if role in {"route", "service", "job", "config", "test"}:
            return role
        return ""

    def _dedupe_strings(self, items: list[str]) -> list[str]:
        deduped: list[str] = []
        for item in items:
            cleaned = " ".join(str(item).split())
            if cleaned and cleaned not in deduped:
                deduped.append(cleaned)
        return deduped
