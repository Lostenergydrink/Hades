from __future__ import annotations

from typing import Dict, Iterable

from .agents import (
    AgentRequest,
    AgentResult,
    StyxAgent,
    FuriesAgent,
    RouteDecision,
    HadesAgent,
    ThanatosAgent,
    PersephoneAgent,
    ToolLimitedAgent,
    HermesAgent,
)
from .checkpoint import CheckpointManager
from .context_inspector import ProjectContext
from .observability import ensure_tracing
from .registry import ProjectRegistry
from .types import RiskLevel


class AgentOrchestrator:
    """High-level coordinator that wires the router to specialist agents."""

    def __init__(self, enable_tracing: bool = True, enable_checkpoints: bool = True) -> None:
        self._enable_tracing = enable_tracing
        self._enable_checkpoints = enable_checkpoints
        self._router: HadesAgent | None = None
        self._agents: Dict[str, ToolLimitedAgent] = {}
        self._checkpoint_manager: CheckpointManager | None = None

    def _lazy_init(self) -> None:
        if self._agents:
            return
        self._agents = {
            "code_refactor": StyxAgent(),
            "lint_format": FuriesAgent(),
            "terminal_ops": ThanatosAgent(),
            "test_runner": PersephoneAgent(),
            "web_automation": HermesAgent(),
        }
        self._router = HadesAgent(self._agents)
        if self._enable_tracing:
            ensure_tracing()

    @property
    def agents(self) -> Dict[str, ToolLimitedAgent]:
        self._lazy_init()
        return self._agents

    @property
    def router(self) -> HadesAgent:
        self._lazy_init()
        assert self._router is not None  # mypy/runtime safety
        return self._router

    def run(self, task: str, *, context: ProjectContext) -> AgentResult:
        self._lazy_init()
        registry = ProjectRegistry(context)
        
        # Initialize checkpoint manager for this context
        if self._enable_checkpoints:
            self._checkpoint_manager = CheckpointManager(context.root)
        
        request = AgentRequest(task=task, context=context, registry=registry)
        decision = self.router.decide(request)
        result = self._execute_plan(decision, request)
        return result

    def _execute_plan(self, decision: RouteDecision, request: AgentRequest) -> AgentResult:
        executed: list[str] = []
        result = self._run_agent(decision.target_agent, request)
        executed.append(decision.target_agent)
        if not result.success:
            result.metadata.setdefault("plan", executed)
            result.metadata.setdefault("router_reasoning", decision.reasoning)
            result.metadata.setdefault("router_confidence", decision.confidence)
            return result
        for agent_name in decision.plan[1:]:
            follow_up = self._run_agent(agent_name, request)
            executed.append(agent_name)
            if not follow_up.success:
                follow_up.metadata.setdefault("plan", executed)
                follow_up.metadata.setdefault("router_reasoning", decision.reasoning)
                follow_up.metadata.setdefault("router_confidence", decision.confidence)
                return follow_up
            result = follow_up
        result.metadata.setdefault("plan", executed)
        result.metadata.setdefault("router_reasoning", decision.reasoning)
        result.metadata.setdefault("router_confidence", decision.confidence)
        return result

    def _run_agent(self, name: str, request: AgentRequest) -> AgentResult:
        agent = self.agents.get(name)
        if agent is None:
            return AgentResult(output=f"Unknown agent: {name}", success=False)
        
        # Pre-flight checkpointing: snapshot likely targets before writes
        pre_checkpoint_id = self._maybe_create_pre_checkpoint(name, request)
        
        result = agent.handle(request)
        
        # Create checkpoint if result has changes and risk is MEDIUM or higher
        if (
            self._enable_checkpoints
            and self._checkpoint_manager
            and result.changes
            and result.changes.risk in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL)
            and not result.changes.checkpoint_id  # Don't double-checkpoint
        ):
            try:
                checkpoint_id = self._checkpoint_manager.create_from_manifest(result.changes)
                result.metadata["checkpoint_created"] = checkpoint_id
            except Exception as e:
                # Don't fail the operation if checkpoint fails
                result.metadata["checkpoint_error"] = str(e)
        elif pre_checkpoint_id:
            # Surface that a pre-flight checkpoint was taken even if risk was low
            result.metadata.setdefault("checkpoint_created", pre_checkpoint_id)
        
        # Check if human confirmation is required
        if result.confirmation_required and not result.success:
            # Return early with confirmation request
            # The orchestrator/UI layer should re-prompt with confirmation
            result.metadata["needs_approval"] = True
            result.metadata["agent"] = name
            return result
        
        return result

    def _maybe_create_pre_checkpoint(self, name: str, request: AgentRequest) -> str | None:
        """
        Take a checkpoint before running an agent if the task suggests writes.

        This is a heuristic stop-gap until agents emit pre-change manifests.
        """
        if not (self._enable_checkpoints and self._checkpoint_manager):
            return None

        task = request.normalized_task
        files_to_snapshot: list = []

        # Styx launcher generation writes predictable files
        if name == "code_refactor" and "launcher" in task:
            launch_path = request.context.root / "launch_generated.ps1"
            files_to_snapshot.extend([launch_path, launch_path.with_suffix(".bat")])

        # Furies fix mode can rewrite the default entrypoint
        if name == "lint_format" and ("--fix" in task or " fix" in task or "format" in task):
            try:
                files_to_snapshot.append(request.registry.default_entrypoint())
            except FileNotFoundError:
                pass

        if not files_to_snapshot:
            return None

        try:
            return self._checkpoint_manager.create_checkpoint(files_to_snapshot, description=f"pre-flight:{name}")
        except Exception:
            return None
