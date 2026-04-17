from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from repobrain.config import RepoBrainConfig
from repobrain.models import ReviewDelta, ReviewReport


READINESS_ORDER = {
    "not_ready": 0,
    "needs_hardening": 1,
    "promising": 2,
}
HIGH_SIGNAL_SEVERITIES = {"critical", "high"}


class ReviewArtifactsStore:
    def __init__(self, config: RepoBrainConfig) -> None:
        self.config = config

    @property
    def reviews_dir(self) -> Path:
        return self.config.state_path / "reviews"

    @property
    def history_dir(self) -> Path:
        return self.reviews_dir / "history"

    def baseline_path(self, label: str = "baseline") -> Path:
        return self.reviews_dir / f"{self._safe_label(label)}.json"

    def load_baseline(self, label: str = "baseline") -> dict[str, object] | None:
        path = self.baseline_path(label)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def save_baseline(self, report: ReviewReport, label: str = "baseline") -> dict[str, str]:
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        captured_at = datetime.now(timezone.utc)
        saved_at = captured_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        review_payload = report.to_dict()
        review_payload["delta"] = None
        payload = {
            "label": self._safe_label(label),
            "saved_at": saved_at,
            "review": review_payload,
        }

        baseline_path = self.baseline_path(label)
        history_stamp = captured_at.strftime("%Y%m%dT%H%M%S%fZ")
        history_path = self.history_dir / f"{history_stamp}-{self._safe_label(label)}.json"
        serialized = json.dumps(payload, indent=2)
        baseline_path.write_text(serialized, encoding="utf-8")
        history_path.write_text(serialized, encoding="utf-8")
        return {
            "label": self._safe_label(label),
            "baseline_path": str(baseline_path),
            "history_path": str(history_path),
            "saved_at": saved_at,
        }

    def list_history(self, label: str = "baseline", limit: int = 8) -> list[dict[str, object]]:
        safe_label = self._safe_label(label)
        if limit <= 0 or not self.history_dir.exists():
            return []

        entries: list[dict[str, object]] = []
        for path in sorted(self.history_dir.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if str(payload.get("label", "")) != safe_label:
                continue
            review = payload.get("review", {})
            if not isinstance(review, dict):
                continue
            findings = review.get("findings", [])
            finding_titles = [
                str(item.get("title", "Untitled finding"))
                for item in findings
                if isinstance(item, dict)
            ]
            entries.append(
                {
                    "name": str(payload.get("saved_at", "")) or path.stem,
                    "saved_at": str(payload.get("saved_at", "")),
                    "score": round(float(review.get("score", 0.0)), 1),
                    "readiness": str(review.get("readiness", "unknown")),
                    "finding_count": len(findings) if isinstance(findings, list) else 0,
                    "finding_titles": finding_titles,
                }
            )
            if len(entries) >= limit:
                break

        entries.reverse()
        return entries

    def history_summary(self, report: ReviewReport, label: str = "baseline", limit: int = 6) -> dict[str, object]:
        saved_points = self.list_history(label=label, limit=max(limit - 1, 0))
        current_titles = [finding.title for finding in report.findings]
        points = [
            {**entry, "current": False}
            for entry in saved_points
        ]
        points.append(
            {
                "name": "Current",
                "saved_at": "",
                "score": round(report.score, 1),
                "readiness": report.readiness,
                "finding_count": len(report.findings),
                "finding_titles": current_titles,
                "current": True,
            }
        )

        score_change = 0.0
        direction = "new"
        if saved_points:
            anchor = saved_points[0]
            baseline_score = float(anchor.get("score", report.score))
            baseline_readiness = str(anchor.get("readiness", report.readiness))
            score_change = round(report.score - baseline_score, 1)
            baseline_rank = READINESS_ORDER.get(baseline_readiness, 0)
            current_rank = READINESS_ORDER.get(report.readiness, 0)
            if current_rank > baseline_rank or score_change >= 0.4:
                direction = "improving"
            elif current_rank < baseline_rank or score_change <= -0.4:
                direction = "regressing"
            else:
                direction = "flat"

        title_counts: Counter[str] = Counter()
        for point in points:
            for title in point.get("finding_titles", []):
                title_counts[str(title)] += 1

        recurring_findings = [
            {"title": title, "count": count}
            for title, count in title_counts.most_common()
            if count >= 2
        ][:3]
        scores = [float(point.get("score", 0.0)) for point in points]
        return {
            "label": self._safe_label(label),
            "direction": direction,
            "score_change": round(score_change, 1),
            "saved_snapshots": len(saved_points),
            "latest_saved_at": str(saved_points[-1].get("saved_at", "")) if saved_points else "",
            "best_score": round(max(scores), 1) if scores else round(report.score, 1),
            "worst_score": round(min(scores), 1) if scores else round(report.score, 1),
            "points": points,
            "recurring_findings": recurring_findings,
        }

    def compare(self, report: ReviewReport, label: str = "baseline") -> ReviewDelta | None:
        payload = self.load_baseline(label)
        if not payload:
            return None

        baseline_review = payload.get("review", {})
        if not isinstance(baseline_review, dict):
            return None

        baseline_score = float(baseline_review.get("score", report.score))
        baseline_readiness = str(baseline_review.get("readiness", report.readiness))
        baseline_findings = baseline_review.get("findings", [])
        if not isinstance(baseline_findings, list):
            baseline_findings = []

        current_signatures = {self._signature_from_finding(item.to_dict()) for item in report.findings}
        baseline_signatures = {self._signature_from_finding(item) for item in baseline_findings if isinstance(item, dict)}
        current_title_map = {self._signature_from_finding(item.to_dict()): item.title for item in report.findings}
        baseline_title_map = {self._signature_from_finding(item): str(item.get("title", "Untitled finding")) for item in baseline_findings if isinstance(item, dict)}

        new_signatures = sorted(current_signatures - baseline_signatures)
        resolved_signatures = sorted(baseline_signatures - current_signatures)
        new_findings = [current_title_map[item] for item in new_signatures[:3]]
        resolved_findings = [baseline_title_map[item] for item in resolved_signatures[:3]]
        score_delta = round(report.score - baseline_score, 1)

        status = self._status(
            baseline_readiness=baseline_readiness,
            current_readiness=report.readiness,
            score_delta=score_delta,
            new_signatures=new_signatures,
            resolved_signatures=resolved_signatures,
        )
        return ReviewDelta(
            baseline_label=str(payload.get("label", self._safe_label(label))),
            baseline_saved_at=str(payload.get("saved_at", "")),
            status=status,
            baseline_score=baseline_score,
            current_score=report.score,
            score_delta=score_delta,
            baseline_readiness=baseline_readiness,
            current_readiness=report.readiness,
            new_findings=new_findings,
            resolved_findings=resolved_findings,
        )

    def _status(
        self,
        *,
        baseline_readiness: str,
        current_readiness: str,
        score_delta: float,
        new_signatures: list[str],
        resolved_signatures: list[str],
    ) -> str:
        baseline_rank = READINESS_ORDER.get(baseline_readiness, 0)
        current_rank = READINESS_ORDER.get(current_readiness, 0)
        if current_rank > baseline_rank:
            return "improved"
        if current_rank < baseline_rank:
            return "regressed"
        if score_delta >= 0.4 or (resolved_signatures and score_delta >= 0):
            return "improved"
        if score_delta <= -0.4 or (new_signatures and score_delta <= 0):
            return "regressed"
        return "unchanged"

    def _signature_from_finding(self, finding: dict[str, object]) -> str:
        severity = str(finding.get("severity", "unknown")).strip().lower()
        category = str(finding.get("category", "unknown")).strip().lower()
        title = str(finding.get("title", "untitled")).strip().lower()
        return f"{severity}|{category}|{title}"

    def _safe_label(self, label: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", label.strip()).strip("-")
        return normalized or "baseline"
