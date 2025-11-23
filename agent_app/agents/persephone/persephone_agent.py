from __future__ import annotations

from agent_app.types import Diagnostic

from ..base import AgentRequest, AgentResult, ToolLimitedAgent


class PersephoneAgent(ToolLimitedAgent):
    name = "persephone"
    description = "Owns pytest/npm test execution, coverage parsing, and flake tracking."
    allowed_tools = ("pytest", "npm_test", "coverage")
    guardrails = (
        "May only edit tests by collaborating with the code agent.",
        "Must record parsed failures before returning.",
        "Does not run arbitrary shell commands beyond test runners.",
    )

    def handle(self, request: AgentRequest) -> AgentResult:
        # Placeholder diagnostic indicating the agent is not yet implemented
        diagnostic = Diagnostic(
            severity="info",
            message="Test runner agent scaffolding is ready. Hook into pytest/playwright commands before routing test tasks.",
            source="test_runner",
        )
        
        return AgentResult(
            output=(
                "Test runner agent scaffolding is ready. Hook into pytest/playwright "
                "commands before routing test tasks."
            ),
            success=False,
            diagnostics=[diagnostic],
            metadata={"pending": True},
        )

