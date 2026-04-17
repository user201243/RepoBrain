from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Callable

from repobrain.engine.core import RepoBrainEngine
from repobrain.models import ReviewFocus


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    handler: Callable[[dict[str, object]], object]


class RepoBrainMCPServer:
    MAX_QUERY_LENGTH = 2000

    def __init__(self, engine: RepoBrainEngine) -> None:
        self.engine = engine
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
        }

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": tool.name, "description": tool.description} for tool in self.tools.values()]

    def _validate_tool_call(self, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        if tool_name == "index_repository":
            return {}
        if tool_name == "review_codebase":
            focus = str(arguments.get("focus", ReviewFocus.FULL.value)).strip().lower()
            if focus not in {item.value for item in ReviewFocus}:
                raise ValueError(f"`focus` for tool `{tool_name}` must be one of: {', '.join(item.value for item in ReviewFocus)}.")
            return {"focus": focus}
        if tool_name == "assess_ship_readiness":
            baseline_label = str(arguments.get("baseline_label", "baseline")).strip() or "baseline"
            return {"baseline_label": baseline_label}

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
