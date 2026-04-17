from __future__ import annotations

import io
from urllib.parse import urlencode
from pathlib import Path

from repobrain.web import _action_result, _application, _doctor_result, _import_and_index, _review_result


def test_web_import_and_query_flow(mixed_repo: Path) -> None:
    repo_text, message, result = _import_and_index(str(mixed_repo))

    assert repo_text == str(mixed_repo.resolve())
    assert "Imported and indexed" in message
    assert "RepoBrain Index Complete" in result

    active_repo, title, query_result = _action_result("query", "Where is payment retry logic implemented?")
    assert active_repo == str(mixed_repo.resolve())
    assert title == "Query"
    assert "RepoBrain Result" in query_result

    doctor_repo, doctor_result = _doctor_result()
    assert doctor_repo == str(mixed_repo.resolve())
    assert "RepoBrain Doctor" in doctor_result

    review_repo, review_result = _review_result()
    assert review_repo == str(mixed_repo.resolve())
    assert "RepoBrain Review" in review_result


def test_web_home_page_renders_import_form(mixed_repo: Path) -> None:
    app = _application(default_repo=str(mixed_repo))
    status_headers: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_headers["status"] = status
        status_headers["headers"] = headers

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "GET",
                "PATH_INFO": "/",
                "wsgi.input": io.BytesIO(b""),
                "CONTENT_LENGTH": "0",
            },
            start_response,
        )
    ).decode("utf-8")

    assert status_headers["status"] == "200 OK"
    assert "RepoBrain Web" in body
    assert "Import + Index" in body
    assert "Scan Project Review" in body
    assert "Ship Gate" in body
    assert "Save Baseline" in body
    assert str(mixed_repo) in body


def test_web_review_route_renders_project_review(mixed_repo: Path) -> None:
    _import_and_index(str(mixed_repo))
    app = _application(default_repo=str(mixed_repo))
    status_headers: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_headers["status"] = status
        status_headers["headers"] = headers

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "POST",
                "PATH_INFO": "/review",
                "wsgi.input": io.BytesIO(urlencode({}).encode("utf-8")),
                "CONTENT_LENGTH": "0",
            },
            start_response,
        )
    ).decode("utf-8")

    assert status_headers["status"] == "200 OK"
    assert "Project Review" in body
    assert "RepoBrain Review" in body


def test_web_ship_route_renders_ship_gate(mixed_repo: Path) -> None:
    _import_and_index(str(mixed_repo))
    app = _application(default_repo=str(mixed_repo))
    status_headers: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_headers["status"] = status
        status_headers["headers"] = headers

    body = b"".join(
        app(
            {
                "REQUEST_METHOD": "POST",
                "PATH_INFO": "/ship",
                "wsgi.input": io.BytesIO(urlencode({}).encode("utf-8")),
                "CONTENT_LENGTH": "0",
            },
            start_response,
        )
    ).decode("utf-8")

    assert status_headers["status"] == "200 OK"
    assert "Ship Readiness" in body
    assert "RepoBrain Ship Gate" in body
