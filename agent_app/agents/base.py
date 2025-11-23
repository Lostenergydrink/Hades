from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agent_app.context_inspector import ProjectContext
from agent_app.registry import ProjectRegistry

# Import enhanced types from types.py (AgentResult is now defined there)
from agent_app.types import AgentResult  # noqa: F401 - Re-exported for backward compatibility


@dataclass(slots=True)
class AgentRequest:
    """Normalized payload every agent receives."""

    task: str
    context: ProjectContext
    registry: ProjectRegistry
    upstream_results: list[AgentResult] = field(default_factory=list)  # Phase 1: Multi-hop context passing

    @property
    def normalized_task(self) -> str:
        return self.task.lower().strip()


@dataclass(slots=True)
class RouteDecision:
    """Router decision shared back to the orchestrator for execution."""

    target_agent: str
    confidence: float
    reasoning: str
    plan: list[str] = field(default_factory=list)


class ToolLimitedAgent(ABC):
    """Base class that enforces metadata + simple guardrails per agent."""

    name: str
    description: str
    allowed_tools: tuple[str, ...]
    guardrails: tuple[str, ...]

    def __init__(self) -> None:
        if not getattr(self, "name", None):  # pragma: no cover - sanity check
            raise ValueError("Agent subclasses must define a name")

    @abstractmethod
    def handle(self, request: AgentRequest) -> AgentResult:
        raise NotImplementedError


class HadesAgentProtocol(ABC):
    """Protocol used by the orchestrator to obtain routing decisions."""

    @abstractmethod
    def decide(self, request: AgentRequest) -> RouteDecision:
        raise NotImplementedError

    @abstractmethod
    def handle(self, request: AgentRequest) -> AgentResult:
        """Routers can also surface clarifying questions straight to the user."""
        raise NotImplementedError
