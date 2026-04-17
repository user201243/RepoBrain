from __future__ import annotations

from pathlib import Path

from repobrain.engine.core import RepoBrainEngine
from repobrain.models import ReviewFinding, ReviewFocus, ReviewReport, ReviewSeverity


def _make_report(repo_root: Path, score: float, readiness: str, finding_titles: list[str]) -> ReviewReport:
    findings = [
        ReviewFinding(
            severity=ReviewSeverity.HIGH,
            category="production",
            title=title,
            summary=f"Summary for {title}",
            file_paths=["app/main.py"],
            recommendation=f"Fix {title}",
        )
        for title in finding_titles
    ]
    return ReviewReport(
        repo_root=str(repo_root),
        focus=ReviewFocus.FULL,
        readiness=readiness,
        score=score,
        summary="Synthetic review report for history tests.",
        findings=findings,
        next_steps=["Harden the riskiest finding first."],
        stats={},
        category_counts={"production": len(findings)},
        severity_counts={"high": len(findings)},
    )


def test_review_history_summary_tracks_direction_and_recurring_findings(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    engine = RepoBrainEngine(repo_root)
    engine.init_workspace(force=True)

    first = _make_report(
        repo_root,
        score=4.8,
        readiness="not_ready",
        finding_titles=[
            "Secrets may be baked into the Docker image",
            "No obvious CI guardrail was found",
        ],
    )
    second = _make_report(
        repo_root,
        score=6.1,
        readiness="needs_hardening",
        finding_titles=[
            "No obvious CI guardrail was found",
            "Formatting and lint guardrails are missing or incomplete",
        ],
    )
    current = _make_report(
        repo_root,
        score=7.4,
        readiness="promising",
        finding_titles=[
            "No obvious CI guardrail was found",
        ],
    )

    engine.save_review_baseline(first)
    engine.save_review_baseline(second)
    history_files = sorted(engine.review_artifacts.history_dir.glob("*.json"))
    summary = engine.review_artifacts.history_summary(current)

    assert len(history_files) == 2
    assert summary["saved_snapshots"] == 2
    assert summary["direction"] == "improving"
    assert summary["score_change"] == 2.6
    assert len(summary["points"]) == 3
    assert summary["points"][-1]["current"] is True
    assert summary["points"][-1]["score"] == 7.4
    assert summary["recurring_findings"][0]["title"] == "No obvious CI guardrail was found"
    assert summary["recurring_findings"][0]["count"] == 3
