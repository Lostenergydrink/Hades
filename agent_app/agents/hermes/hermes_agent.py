from __future__ import annotations

from agent_app.types import Diagnostic

from ..base import AgentRequest, AgentResult, ToolLimitedAgent


class HermesAgent(ToolLimitedAgent):
    name = "web_automation"
    description = "Maintains Playwright/Puppeteer suites, selectors, and traces."
    allowed_tools = ("playwright", "puppeteer", "trace_viewer")
    guardrails = (
        "No general shell commands; only automation tooling.",
        "Stores artifacts under tests/e2e/.artifacts.",
        "Reports selector diffs for every change.",
    )

    def handle(self, request: AgentRequest) -> AgentResult:
        # Placeholder diagnostic indicating the agent is not yet implemented
        diagnostic = Diagnostic(
            severity="info",
            message="Web automation agent scaffolding exists. Implement Playwright task execution before routing browser automation work.",
            source="web_automation",
        )
        
        return AgentResult(
            output=(
                "Web automation agent scaffolding exists. Implement Playwright task "
                "execution before routing browser automation work."
            ),
            success=False,
            diagnostics=[diagnostic],
            metadata={"pending": True},
        )

