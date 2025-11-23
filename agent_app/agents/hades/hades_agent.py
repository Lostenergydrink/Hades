from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from agent_app.output_sanitizer import should_reject_output

from ..base import AgentRequest, AgentResult, RouteDecision, HadesAgentProtocol, ToolLimitedAgent


@dataclass(frozen=True)
class RoutingRule:
    keywords: tuple[str, ...]
    target_agent: str
    reasoning: str
    confidence: float = 0.85

    def matches(self, text: str) -> bool:
        return all(keyword in text for keyword in self.keywords)


class HadesAgent(ToolLimitedAgent, HadesAgentProtocol):
    name = "router"
    description = "Decides which specialist agent should handle a request."
    allowed_tools = ("registry",)
    guardrails = (
        "Read-only access to repository metadata.",
        "Cannot modify files or run shell commands.",
    )

    def __init__(self, specialists: dict[str, ToolLimitedAgent]) -> None:
        super().__init__()
        self._specialists = specialists
        self._rules: tuple[RoutingRule, ...] = (
            RoutingRule(("playwright",), "web_automation", "Playwright keyword detected"),
            RoutingRule(("browser",), "web_automation", "Browser automation requested"),
            RoutingRule(("lint",), "lint_format", "Lint keyword detected"),
            RoutingRule(("format",), "lint_format", "Formatting requested"),
            RoutingRule(("syntax",), "code_refactor", "Syntax check requested"),
            RoutingRule(("import",), "code_refactor", "Import analysis requested"),
            RoutingRule(("launcher",), "code_refactor", "Launcher generation touches code"),
            RoutingRule(("test",), "test_runner", "Tests requested"),
            RoutingRule(("coverage",), "test_runner", "Coverage requested"),
            RoutingRule(("run", "npm"), "terminal_ops", "Shell execution implied"),
            RoutingRule(("status", "git"), "terminal_ops", "Git command requested"),
        )

    def decide(self, request: AgentRequest) -> RouteDecision:
        # Safety net: Veto nonsense inputs
        should_reject, reject_reason = should_reject_output(request.task, max_length=5000)
        if should_reject:
            return RouteDecision(
                target_agent="router",
                confidence=0.0,
                reasoning=f"Request rejected: {reject_reason}",
            )
        
        normalized = request.normalized_task
        for rule in self._rules:
            if rule.matches(normalized):
                return RouteDecision(
                    target_agent=rule.target_agent,
                    confidence=rule.confidence,
                    reasoning=rule.reasoning,
                )
        plan: list[str] = []
        if "test" in normalized and ("fix" in normalized or "refactor" in normalized):
            plan = ["code_refactor", "test_runner"]
        return RouteDecision(
            target_agent="code_refactor" if not plan else plan[0],
            confidence=0.55,
            reasoning="Fallback to code agent for unspecified requests.",
            plan=plan,
        )

    def handle(self, request: AgentRequest) -> AgentResult:
        summary_lines = request.registry.summary().to_lines()
        output = "Router requires clarification. Current context:\n" + "\n".join(summary_lines)
        return AgentResult(output=output, success=False, metadata={"needs_clarification": True})

    @property
    def specialists(self) -> dict[str, ToolLimitedAgent]:
        return self._specialists

    def list_specialists(self) -> Iterable[str]:
        return self._specialists.keys()
