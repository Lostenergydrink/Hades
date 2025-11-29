from __future__ import annotations

from pathlib import Path

from agent_app.output_sanitizer import OutputSanitizer
from agent_app.python_tools import analyze_imports, check_syntax, format_import_report
from agent_app.script_tools import write_launcher
from agent_app.types import ChangeManifest, Diagnostic, FileChange, RiskLevel

from ..base import AgentRequest, AgentResult, ToolLimitedAgent


class StyxAgent(ToolLimitedAgent):
	name = "code_refactor"
	description = "Owns read/write code changes, AST inspections, and launchers."
	allowed_tools = ("apply_patch", "file_system", "lsp_symbols")
	guardrails = (
		"Cannot execute shell commands.",
		"Cannot run git operations or manage dependencies.",
		"Must limit edits to requested scope.",
		"Only change inside annotated regions.",
		"Never overwrite entire file.",
		"Reject unstructured blobs.",
	)
	
	def __init__(self) -> None:
		super().__init__()
		self._sanitizer = OutputSanitizer()

	def handle(self, request: AgentRequest) -> AgentResult:
		normalized = request.normalized_task
		
		# Launcher creation doesn't need an entrypoint
		if "launcher" in normalized:
			return self._handle_launcher(request)
		
		# Other tasks require a valid entrypoint
		try:
			target = request.registry.default_entrypoint()
		except FileNotFoundError:
			return AgentResult(
				output="No Python files found in project. Cannot determine entry point.",
				success=False,
			)
		
		if normalized.startswith("check syntax"):
			return self._handle_syntax(target)
		if "import" in normalized:
			return self._handle_imports(target, request)
		return AgentResult(
			output=(
				"Code agent does not yet support this task. "
				"Try refining the request or route through Router."
			),
			success=False,
		)

	def _handle_syntax(self, target: Path) -> AgentResult:
		issues = check_syntax(target)
		if not issues:
			return AgentResult(output=f"No syntax errors detected in {target}.")
		
		# Convert to Diagnostic objects
		diagnostics = [
			Diagnostic(
				severity="error",
				message=issue.message,
				file=issue.path,
				line=issue.line,
				column=issue.column,
				source="ast",
			)
			for issue in issues
		]
		
		rendered = "\n".join(str(d) for d in diagnostics)
		return AgentResult(
			output=rendered,
			success=False,
			diagnostics=diagnostics,
		)

	def _handle_imports(self, target: Path, request: AgentRequest) -> AgentResult:
		report = analyze_imports(target, request.context)
		
		# Convert missing imports to warnings
		diagnostics = [
			Diagnostic(
				severity="warning",
				message=f"Missing import: {missing}",
				file=target,
				code="import-error",
				source="import-analyzer",
			)
			for missing in report.missing
		]
		
		return AgentResult(
			output=format_import_report(report),
			diagnostics=diagnostics,
		)

	def _handle_launcher(self, request: AgentRequest) -> AgentResult:
		ctx = request.context
		launch_path = ctx.root / "launch_generated.ps1"
		write_launcher(ctx, launch_path)
		
		# Create ChangeManifest for generated launcher files
		bat_path = launch_path.with_suffix(".bat")
		changes = ChangeManifest(
			files=[
				FileChange(path=launch_path, operation="create"),
				FileChange(path=bat_path, operation="create"),
			],
			summary="Generated launcher scripts",
			risk=RiskLevel.SAFE,
		)
		
		return AgentResult(
			output=f"Launcher refreshed: {launch_path} and {bat_path}",
			changes=changes,
			artifacts=[launch_path, bat_path],
		)
	
	def validate_file_edit(self, content: str, operation: str = "edit") -> tuple[bool, str | None]:
		"""
		Safety net: Validate file edit operations.
		
		Args:
			content: The content being written
			operation: The operation type (edit, create, overwrite)
		
		Returns:
			(is_valid, error_reason)
		"""
		# Reject if content is too large
		if len(content) > 50000:
			return False, f"File content too large: {len(content)} characters exceeds 50,000 limit"
		
		# Reject unstructured blobs (no line breaks in first 1000 chars)
		if len(content) > 1000 and "\n" not in content[:1000]:
			return False, "Rejected unstructured blob: no line breaks detected"
		
		# Reject whole-file overwrites without markers
		if operation == "overwrite" and len(content) > 500:
			if "# BEGIN REGION" not in content and "# EDIT START" not in content:
				return False, "Overwrite rejected: must use annotated regions for large edits"
		
		# Check for suspicious patterns
		lines = content.split("\n")
		if len(lines) > 100:
			unique_ratio = len(set(lines)) / len(lines)
			if unique_ratio < 0.1:
				return False, "Rejected repetitive content (< 10% unique lines)"
		
		return True, None