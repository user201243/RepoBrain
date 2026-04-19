from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from repobrain.active_repo import write_active_repo
from repobrain.engine.core import RepoBrainEngine
from repobrain.models import ReviewFocus
from repobrain.workspace import (
    add_workspace_project,
    remember_workspace_note,
    set_current_workspace_project,
    workspace_projects_payload,
    workspace_query_payload,
    workspace_summary_payload,
)


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    handler: Callable[[dict[str, object]], object]


class RepoBrainMCPServer:
    MAX_QUERY_LENGTH = 2000

    def __init__(self, engine: RepoBrainEngine, engine_factory: Callable[[str | Path], RepoBrainEngine] = RepoBrainEngine) -> None:
        self.engine = engine
        self.engine_factory = engine_factory
        self.tools = {
            "index_repository": ToolDefinition(
                "index_repository",
                "Scan the repository, build the metadata store, and persist vectors.",
                lambda args: self.engine.index_repository(),
            ),
            "search_codebase": ToolDefinition(
                "search_codebase",
                "Retrieve grounded snippets and ranked files for a natural-language code query.",
                lambda args: self.engine.query(str(args["query"])).to_dict(),
            ),
            "trace_flow": ToolDefinition(
                "trace_flow",
                "Trace likely call flow and dependency edges for a repo question.",
                lambda args: self.engine.trace(str(args["query"])).to_dict(),
            ),
            "analyze_impact": ToolDefinition(
                "analyze_impact",
                "Estimate impacted files and dependency edges for a requested change.",
                lambda args: self.engine.impact(str(args["query"])).to_dict(),
            ),
            "suggest_edit_targets": ToolDefinition(
                "suggest_edit_targets",
                "Return ranked files that are safest to inspect or edit next.",
                lambda args: self.engine.targets(str(args["query"])).to_dict(),
            ),
            "build_change_context": ToolDefinition(
                "build_change_context",
                "Return a compact grounded change context for an agent planner.",
                lambda args: self.engine.build_change_context(str(args["query"])),
            ),
            "review_patch": ToolDefinition(
                "review_patch",
                "Review the current patch or an explicit diff target set and surface adjacent files, tests, config touchpoints, and risk warnings.",
                lambda args: self.engine.patch_review(
                    base=str(args.get("base", "")).strip() or None,
                    files=list(args.get("files", [])) if isinstance(args.get("files"), list) else None,
                ).to_dict(),
            ),
            "review_codebase": ToolDefinition(
                "review_codebase",
                "Scan the repository and summarize the most important production, security, and code-quality gaps.",
                lambda args: self.engine.review(focus=ReviewFocus(str(args.get("focus", ReviewFocus.FULL.value)))).to_dict(),
            ),
            "assess_ship_readiness": ToolDefinition(
                "assess_ship_readiness",
                "Run the production ship gate across review findings, index health, parser posture, providers, and benchmark signals.",
                lambda args: self.engine.ship(baseline_label=str(args.get("baseline_label", "baseline"))).to_dict(),
            ),
            "list_workspace_projects": ToolDefinition(
                "list_workspace_projects",
                "List tracked repos in the shared RepoBrain workspace and show the active repo.",
                lambda args: workspace_projects_payload(),
            ),
            "track_workspace_project": ToolDefinition(
                "track_workspace_project",
                "Track another repo in the shared workspace and optionally make it active.",
                lambda args: self._track_workspace_project(str(args["repo"]), activate=bool(args.get("activate", True))),
            ),
            "switch_workspace_project": ToolDefinition(
                "switch_workspace_project",
                "Switch the active repo for this MCP session and the shared workspace registry.",
                lambda args: self._switch_workspace_project(str(args["project"])),
            ),
            "read_repo_memory": ToolDefinition(
                "read_repo_memory",
                "Read the persisted summary memory for the active repo or another tracked repo.",
                lambda args: workspace_summary_payload(args.get("project")),
            ),
            "remember_repo_note": ToolDefinition(
                "remember_repo_note",
                "Persist a manual repo note so future workspace queries retain the key thread.",
                lambda args: remember_workspace_note(str(args["note"]), args.get("project")),
            ),
            "search_workspace": ToolDefinition(
                "search_workspace",
                "Run the same grounded query across every tracked repo and compare the strongest evidence per project.",
                lambda args: workspace_query_payload(
                    str(args["query"]),
                    current_repo=self.engine.config.resolved_repo_root,
                    context=str(args.get("context", "")).strip() or None,
                    engine_factory=self.engine_factory,
                ),
            ),
        }

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": tool.name, "description": tool.description} for tool in self.tools.values()]

    def _activate_repo(self, repo_root: str | Path) -> Path:
        resolved = Path(repo_root).expanduser().resolve()
        self.engine = self.engine_factory(resolved)
        write_active_repo(resolved)
        return resolved

    def _track_workspace_project(self, repo_root: str, *, activate: bool = True) -> dict[str, object]:
        payload = add_workspace_project(repo_root, make_current=activate)
        if activate:
            self._activate_repo(str(payload.get("current_repo", repo_root)))
        return payload

    def _switch_workspace_project(self, project: str) -> dict[str, object]:
        payload = set_current_workspace_project(project)
        current_repo = str(payload.get("current_repo", "")).strip()
        if not current_repo:
            raise ValueError("Workspace switch did not produce an active repo.")
        self._activate_repo(current_repo)
        return payload

    def _validate_tool_call(self, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        if tool_name == "index_repository" or tool_name == "list_workspace_projects":
            return {}
        if tool_name == "review_codebase":
            focus = str(arguments.get("focus", ReviewFocus.FULL.value)).strip().lower()
            if focus not in {item.value for item in ReviewFocus}:
                raise ValueError(f"`focus` for tool `{tool_name}` must be one of: {', '.join(item.value for item in ReviewFocus)}.")
            return {"focus": focus}
        if tool_name == "review_patch":
            base = str(arguments.get("base", "")).strip()
            raw_files = arguments.get("files", [])
            if base and raw_files:
                raise ValueError("`review_patch` accepts either `base` or `files`, not both.")
            if raw_files and not isinstance(raw_files, list):
                raise ValueError("`files` for tool `review_patch` must be a JSON array of repo-relative paths.")
            files = [str(item).strip() for item in raw_files if str(item).strip()] if isinstance(raw_files, list) else []
            if "files" in arguments and not files:
                raise ValueError("`files` for tool `review_patch` cannot be empty.")
            return {"base": base or None, "files": files or None}
        if tool_name == "assess_ship_readiness":
            baseline_label = str(arguments.get("baseline_label", "baseline")).strip() or "baseline"
            return {"baseline_label": baseline_label}
        if tool_name == "track_workspace_project":
            repo = str(arguments.get("repo", "")).strip()
            if not repo:
                raise ValueError("`repo` is required for tool `track_workspace_project`.")
            return {"repo": repo, "activate": bool(arguments.get("activate", True))}
        if tool_name == "switch_workspace_project":
            project = str(arguments.get("project", "")).strip()
            if not project:
                raise ValueError("`project` is required for tool `switch_workspace_project`.")
            return {"project": project}
        if tool_name == "read_repo_memory":
            project = str(arguments.get("project", "")).strip()
            return {"project": project or None}
        if tool_name == "remember_repo_note":
            note = str(arguments.get("note", "")).strip()
            if not note:
                raise ValueError("`note` is required for tool `remember_repo_note`.")
            project = str(arguments.get("project", "")).strip()
            return {"note": note, "project": project or None}
        if tool_name == "search_workspace":
            query = arguments.get("query")
            if not isinstance(query, str) or not query.strip():
                raise ValueError("`query` is required for tool `search_workspace`.")
            if len(query) > self.MAX_QUERY_LENGTH:
                raise ValueError(
                    f"`query` for tool `{tool_name}` exceeds the maximum length of {self.MAX_QUERY_LENGTH} characters."
                )
            context = str(arguments.get("context", "")).strip()
            return {"query": query.strip(), "context": context}

        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"`query` is required for tool `{tool_name}`.")
        if len(query) > self.MAX_QUERY_LENGTH:
            raise ValueError(f"`query` for tool `{tool_name}` exceeds the maximum length of {self.MAX_QUERY_LENGTH} characters.")
        return {"query": query.strip()}

    def serve_stdio(self) -> int:
        banner = {"server": "RepoBrain", "transport": "stdio-json", "tools": self.list_tools()}
        sys.stdout.write(json.dumps(banner) + "\n")
        sys.stdout.flush()

        for line in sys.stdin:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                request = json.loads(stripped)
                if request.get("method") == "tools/list":
                    response = {"tools": self.list_tools()}
                elif request.get("method") == "tools/call":
                    tool_name = str(request["name"])
                    arguments = request.get("arguments", {})
                    if not isinstance(arguments, dict):
                        raise ValueError("`arguments` must be a JSON object.")
                    validated = self._validate_tool_call(tool_name, arguments)
                    response = {"result": self.tools[tool_name].handler(validated)}
                else:
                    response = {"error": f"Unsupported method: {request.get('method')}"}
            except Exception as exc:  # pragma: no cover - defensive transport handling
                response = {"error": str(exc)}
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        return 0


def serve_mcp(repo_root: str) -> int:
    engine = RepoBrainEngine(repo_root)
    server = RepoBrainMCPServer(engine)
    return server.serve_stdio()
