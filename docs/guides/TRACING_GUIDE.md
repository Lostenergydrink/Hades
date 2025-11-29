# Hades Tracing Setup Guide

## ✅ Tracing is Already Configured!

Your Hades project already has OpenTelemetry tracing set up and ready to use.

## How It Works

### Architecture

```
Hades Orchestrator
    ↓ (traces operations)
OpenTelemetry SDK
    ↓ (sends spans via gRPC)
AI Toolkit Trace Collector (localhost:4317)
    ↓ (stores and displays)
VS Code Tracing Panel
```

### What Gets Traced

The Agent Framework automatically traces:
- **Router decisions** - Which agent was selected and why
- **Agent executions** - Each agent's handle() method
- **Multi-hop workflows** - Plans with multiple agents
- **Context operations** - Registry scans, file operations
- **Errors and exceptions** - Failed operations with stack traces

### Configuration

**File:** `agent_app/observability.py`

```python
setup_observability(
    otlp_endpoint="http://localhost:4317",  # AI Toolkit gRPC endpoint
    enable_sensitive_data=True  # Captures prompts/completions
)
```

**Enabled by default** in `AgentOrchestrator`:
```python
orchestrator = AgentOrchestrator(enable_tracing=True)  # Default
```

## Usage

### 1. Start Trace Collector

The AI Toolkit trace collector should already be running (we just started it).

**Manual start:** Press `Ctrl+Shift+P` → "AI Toolkit: Open Tracing"

### 2. Run Your Agent

```powershell
# Any agent operation will be traced
python .\scripts\main.py "check syntax" --start .

# Or use the test script
python .\scripts\test_tracing.py
```

### 3. View Traces

1. Open the **"Tracing"** panel in VS Code (should be in the AI Toolkit sidebar)
2. You'll see a list of trace spans with:
   - Operation names (e.g., "StyxAgent.handle")
   - Duration
   - Success/failure status
   - Input/output data
3. Click any span to see details:
   - Full request/response
   - Nested spans (sub-operations)
   - Error details if failed

## Test Tracing

Run the test script to verify everything works:

```powershell
python .\scripts\test_tracing.py
```

Expected output:
```
============================================================
Testing Hades Tracing Setup
============================================================

1. Enabling tracing...
   ✓ Tracing enabled

2. Creating orchestrator...
   ✓ Orchestrator created

3. Loading project context...
   ✓ Context loaded: <project-path>

4. Running test task (this will create trace spans)...
   ✓ Task completed: True

============================================================
✓ Tracing test complete!
============================================================
```

Then check the Tracing panel for new spans.

## What You'll See in Traces

### Example: "check syntax" task

```
📊 Trace Tree:
├─ orchestrator.run
│  ├─ router.decide
│  │  └─ registry.scan  (0.5s)
│  ├─ code_refactor.handle
│  │  ├─ check_syntax
│  │  └─ format_diagnostics
│  └─ result_formatting
```

### Span Attributes

Each span includes:
- `agent.name` - Which agent executed
- `agent.task` - The task description
- `agent.success` - Whether it succeeded
- `agent.output` - Result output
- `context.root` - Project path
- `duration_ms` - Execution time

## Troubleshooting

### "No traces appearing"

1. **Check collector is running:**
   ```powershell
   # Should see "Tracing" panel in VS Code AI Toolkit
   # Or run: netstat -an | findstr 4317
   ```

2. **Check for import errors:**
   ```powershell
   python -c "from agent_framework.observability import setup_observability; print('OK')"
   ```

3. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### "agent-framework not found"

Install dependencies:
```powershell
pip install -r requirements.txt
```

### "Connection refused on localhost:4317"

Restart the trace collector:
- `Ctrl+Shift+P` → "AI Toolkit: Open Tracing"

## Advanced Configuration

### Custom Endpoint

If you're using a remote collector:

```python
from agent_app.observability import ensure_tracing
ensure_tracing(otlp_endpoint="http://your-collector:4317")
```

### Disable Sensitive Data

To exclude prompts/completions from traces:

Edit `agent_app/observability.py`:
```python
setup_observability(
    otlp_endpoint=otlp_endpoint,
    enable_sensitive_data=False,  # Changed from True
)
```

### Disable Tracing Entirely

```python
orchestrator = AgentOrchestrator(enable_tracing=False)
```

Or set environment variable:
```powershell
$env:HADES_DISABLE_TRACING = "1"
```

## Integration with Phase 2

When building the "code → test" workflow in Phase 2, tracing will show:

1. **Router** decides to use StyxAgent
2. **StyxAgent** modifies files
3. **Checkpoint** created (if risky)
4. **TestRunnerAgent** runs tests
5. **Rollback** if tests fail

All of this will be visible in the trace viewer with timing, inputs, and outputs.

## Metrics from Traces

Tracing also helps measure Phase 1 metrics:
- `registry_scan_ms` - Time to scan project files
- `agent_execution_ms` - Individual agent performance
- `multi_hop_ms` - End-to-end workflow duration

Export trace data to calculate these metrics for roadmap progress tracking.

---

**Status:** ✅ Tracing fully configured and ready to use!
