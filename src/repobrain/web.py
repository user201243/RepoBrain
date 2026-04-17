from __future__ import annotations

import html
import sys
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from repobrain.active_repo import read_active_repo, write_active_repo
from repobrain.engine.core import RepoBrainEngine
from repobrain.ux import build_report, payload_to_text


def _html_page(
    *,
    repo_input: str = "",
    active_repo: str = "",
    message: str = "",
    result_title: str = "",
    result_body: str = "",
    query_text: str = "",
    query_mode: str = "query",
) -> str:
    active_block = "<p class='muted'>No active repo yet. Import a project path below.</p>"
    if active_repo:
        active_block = f"<p><strong>Active repo:</strong> <code>{html.escape(active_repo)}</code></p>"

    result_block = ""
    if result_title or result_body:
        result_block = (
            f"<section class='panel'><h2>{html.escape(result_title or 'Result')}</h2>"
            f"<pre>{html.escape(result_body)}</pre></section>"
        )

    message_block = ""
    if message:
        message_block = f"<div class='notice'>{html.escape(message)}</div>"

    query_options = []
    for value, label in (
        ("query", "Query"),
        ("trace", "Trace"),
        ("impact", "Impact"),
        ("targets", "Targets"),
    ):
        selected = " selected" if value == query_mode else ""
        query_options.append(f"<option value='{value}'{selected}>{label}</option>")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RepoBrain Web</title>
  <style>
    :root {{
      --ink: #14211c;
      --paper: #f7f2e8;
      --panel: rgba(255, 252, 244, 0.9);
      --line: #d7ccb9;
      --accent: #0f766e;
      --accent-2: #1d4ed8;
      --muted: #69756d;
      --shadow: 0 20px 60px rgba(45, 34, 16, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.18), transparent 34rem),
        radial-gradient(circle at bottom right, rgba(29, 78, 216, 0.12), transparent 28rem),
        linear-gradient(135deg, #f9f3e8 0%, #efe5d3 100%);
    }}
    main {{
      width: min(1080px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }}
    .hero, .grid {{
      display: grid;
      gap: 18px;
    }}
    .hero {{ grid-template-columns: 1.05fr 0.95fr; }}
    .grid {{ grid-template-columns: repeat(2, 1fr); margin-top: 18px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 22px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }}
    h1 {{ margin: 0 0 10px; font-size: clamp(2.4rem, 7vw, 4.6rem); line-height: 0.92; letter-spacing: -0.06em; }}
    h2 {{ margin: 0 0 14px; font-size: 1.05rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent); }}
    p, li {{ line-height: 1.65; }}
    .muted {{ color: var(--muted); }}
    form {{ display: grid; gap: 12px; }}
    input[type="text"], textarea, select {{
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(255,255,255,0.78);
      color: var(--ink);
      font: inherit;
    }}
    textarea {{ min-height: 132px; resize: vertical; }}
    .row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }}
    button, .link-button {{
      border: 0;
      border-radius: 999px;
      padding: 11px 16px;
      background: var(--accent);
      color: white;
      cursor: pointer;
      font: inherit;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
    .secondary {{ background: var(--accent-2); }}
    .ghost {{
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--line);
    }}
    .notice {{
      margin: 18px 0 0;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid #b9d6cf;
      background: rgba(15, 118, 110, 0.08);
    }}
    pre {{
      margin: 0;
      overflow-x: auto;
      padding: 16px;
      border-radius: 16px;
      color: #f8f7f2;
      background: #17211d;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    }}
    @media (max-width: 860px) {{
      .hero, .grid {{ grid-template-columns: 1fr; }}
      main {{ padding-top: 16px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <article class="panel">
        <h1>RepoBrain Web</h1>
        <p class="muted">Local browser UI for importing a project, indexing it once, then querying without repeating repo paths.</p>
        {active_block}
        {message_block}
      </article>
      <article class="panel">
        <h2>Fast Import</h2>
        <form method="post" action="/import">
          <label for="repo_path">Project path</label>
          <input id="repo_path" name="repo_path" type="text" value="{html.escape(repo_input)}" placeholder="C:\\path\\to\\your-project">
          <div class="row">
            <button type="submit">Import + Index</button>
          </div>
        </form>
        <p class="muted">This will initialize RepoBrain state, set the active repo, and build the local index in one step.</p>
      </article>
    </section>

    <section class="grid">
      <article class="panel">
        <h2>Active Repo Actions</h2>
        <form method="post" action="/index">
          <button type="submit">Re-index Active Repo</button>
        </form>
        <div class="row" style="margin-top:12px;">
          <form method="post" action="/review">
            <button type="submit" class="ghost">Scan Project Review</button>
          </form>
          <form method="post" action="/ship">
            <button type="submit" class="secondary">Ship Gate</button>
          </form>
          <form method="post" action="/baseline">
            <button type="submit" class="ghost">Save Baseline</button>
          </form>
          <a class="link-button ghost" href="/doctor">Doctor</a>
          <a class="link-button secondary" href="/report">Open Report</a>
        </div>
        <p class="muted">Use Project Review for detailed gaps, Ship Gate for a blunt release verdict, and Save Baseline to track drift after each hardening pass.</p>
      </article>

      <article class="panel">
        <h2>Grounded Question</h2>
        <form method="post" action="/query">
          <label for="mode">Mode</label>
          <select id="mode" name="mode">
            {''.join(query_options)}
          </select>
          <label for="query">Question</label>
          <textarea id="query" name="query" placeholder="Where is payment retry logic implemented?">{html.escape(query_text)}</textarea>
          <button type="submit">Run</button>
        </form>
      </article>
    </section>

    {result_block}
  </main>
</body>
</html>
"""


def _engine_from_repo(repo_root: Path) -> RepoBrainEngine:
    return RepoBrainEngine(repo_root)


def _import_and_index(repo_path: str) -> tuple[str, str, str]:
    repo_root = Path(repo_path).expanduser().resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        raise ValueError("Project path does not exist or is not a directory.")
    engine = _engine_from_repo(repo_root)
    init_payload = engine.init_workspace(force=False)
    stats = engine.index_repository()
    write_active_repo(repo_root)
    message = f"Imported and indexed: {repo_root}"
    result = payload_to_text({**init_payload, "active_repo": str(repo_root)}) + "\n\n" + payload_to_text(stats)
    return str(repo_root), message, result


def _active_engine() -> tuple[Path, RepoBrainEngine]:
    repo_root = read_active_repo()
    if repo_root is None:
        raise ValueError("No active repo yet. Import a project path first.")
    return repo_root, _engine_from_repo(repo_root)


def _report_html(repo_root: Path) -> str:
    engine = _engine_from_repo(repo_root)
    report_path = build_report(engine)
    return report_path.read_text(encoding="utf-8")


def _action_result(mode: str, query_text: str) -> tuple[str, str, str]:
    repo_root, engine = _active_engine()
    if mode == "trace":
        payload = engine.trace(query_text)
        title = "Trace"
    elif mode == "impact":
        payload = engine.impact(query_text)
        title = "Impact"
    elif mode == "targets":
        payload = engine.targets(query_text)
        title = "Targets"
    else:
        payload = engine.query(query_text)
        title = "Query"
    return str(repo_root), title, payload_to_text(payload)


def _doctor_result() -> tuple[str, str]:
    repo_root, engine = _active_engine()
    return str(repo_root), payload_to_text(engine.doctor())


def _review_result() -> tuple[str, str]:
    repo_root, engine = _active_engine()
    return str(repo_root), payload_to_text(engine.review())


def _ship_result() -> tuple[str, str]:
    repo_root, engine = _active_engine()
    return str(repo_root), payload_to_text(engine.ship())


def _baseline_result() -> tuple[str, str]:
    repo_root, engine = _active_engine()
    report = engine.review(compare_baseline=False)
    return str(repo_root), payload_to_text(engine.save_review_baseline(report))


def _index_result() -> tuple[str, str]:
    repo_root, engine = _active_engine()
    return str(repo_root), payload_to_text(engine.index_repository())


def _application(default_repo: str = ""):
    def app(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        active_repo = read_active_repo()
        active_repo_text = str(active_repo) if active_repo else default_repo

        if method == "GET" and path == "/":
            html_text = _html_page(repo_input=active_repo_text, active_repo=active_repo_text)
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html_text.encode("utf-8")]

        if method == "GET" and path == "/doctor":
            try:
                repo_text, result = _doctor_result()
                html_text = _html_page(active_repo=repo_text, repo_input=repo_text, result_title="Doctor", result_body=result)
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [html_text.encode("utf-8")]
            except Exception as exc:
                html_text = _html_page(active_repo=active_repo_text, repo_input=active_repo_text, message=str(exc))
                start_response("400 Bad Request", [("Content-Type", "text/html; charset=utf-8")])
                return [html_text.encode("utf-8")]

        if method == "GET" and path == "/report":
            try:
                repo_root = read_active_repo()
                if repo_root is None:
                    raise ValueError("No active repo yet. Import a project path first.")
                report_html = _report_html(repo_root)
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [report_html.encode("utf-8")]
            except Exception as exc:
                html_text = _html_page(active_repo=active_repo_text, repo_input=active_repo_text, message=str(exc))
                start_response("400 Bad Request", [("Content-Type", "text/html; charset=utf-8")])
                return [html_text.encode("utf-8")]

        if method == "POST":
            size = int(environ.get("CONTENT_LENGTH") or 0)
            raw_body = environ["wsgi.input"].read(size).decode("utf-8")
            fields = {key: values[0] for key, values in parse_qs(raw_body).items()}

            try:
                if path == "/import":
                    repo_text, message, result = _import_and_index(fields.get("repo_path", ""))
                    html_text = _html_page(
                        active_repo=repo_text,
                        repo_input=repo_text,
                        message=message,
                        result_title="Import + Index",
                        result_body=result,
                    )
                elif path == "/index":
                    repo_text, result = _index_result()
                    html_text = _html_page(active_repo=repo_text, repo_input=repo_text, message="Active repo re-indexed.", result_title="Index", result_body=result)
                elif path == "/review":
                    repo_text, result = _review_result()
                    html_text = _html_page(active_repo=repo_text, repo_input=repo_text, message="Project review generated.", result_title="Project Review", result_body=result)
                elif path == "/ship":
                    repo_text, result = _ship_result()
                    html_text = _html_page(active_repo=repo_text, repo_input=repo_text, message="Ship gate completed.", result_title="Ship Readiness", result_body=result)
                elif path == "/baseline":
                    repo_text, result = _baseline_result()
                    html_text = _html_page(active_repo=repo_text, repo_input=repo_text, message="Baseline snapshot saved.", result_title="Baseline Saved", result_body=result)
                elif path == "/query":
                    query_text = fields.get("query", "").strip()
                    mode = fields.get("mode", "query").strip() or "query"
                    if not query_text:
                        raise ValueError("Query text is required.")
                    repo_text, title, result = _action_result(mode, query_text)
                    html_text = _html_page(
                        active_repo=repo_text,
                        repo_input=repo_text,
                        result_title=title,
                        result_body=result,
                        query_text=query_text,
                        query_mode=mode,
                    )
                else:
                    raise ValueError(f"Unsupported route: {path}")
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [html_text.encode("utf-8")]
            except Exception as exc:
                html_text = _html_page(
                    active_repo=active_repo_text,
                    repo_input=fields.get("repo_path", active_repo_text),
                    query_text=fields.get("query", ""),
                    query_mode=fields.get("mode", "query"),
                    message=str(exc),
                )
                start_response("400 Bad Request", [("Content-Type", "text/html; charset=utf-8")])
                return [html_text.encode("utf-8")]

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not Found"]

    return app


def serve_web(repo_root: str = "", host: str = "127.0.0.1", port: int = 8765, open_browser: bool = False) -> int:
    default_repo = repo_root.strip()
    if default_repo:
        write_active_repo(default_repo)

    url = f"http://{host}:{port}/"
    if open_browser:
        webbrowser.open(url)
    else:
        sys.stdout.write(f"RepoBrain Web running at {url}\n")
        sys.stdout.flush()

    app = _application(default_repo=default_repo)
    with make_server(host, port, app) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
    return 0
