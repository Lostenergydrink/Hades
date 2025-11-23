---
applyTo: '**'
---
# Global GitHub Copilot Safety Instructions

## When Running Commands That Might Produce Large Output

🚨 **NEVER fetch terminal output from test/trace/debug/verbose scripts** 🚨

Instead, **always provide the command for the user to run:**

```
For guardrail protection, please run this command directly in your terminal:

<command>

Then let me know: "worked" or "error: <specific error>"
```

### High-Risk Scenarios:
- Test scripts with verbose output
- Tracing/debugging scripts
- Build processes with detailed logs
- Any script that loops or runs continuously
- Package installations with progress output

### Safe Approach:
1. Provide exact command to run
2. Explain it's for "guardrail protection"
3. Ask for summary only ("worked" or "error: X")
4. Trust user's report, don't verify yourself

## When Reading Files

### Before Reading Any File:
1. Use `get_file_info` to check size
2. If > 500 lines or unknown, use:
   - `grep_search` for specific patterns
   - `semantic_search` for concepts
   - `read_file(limit=100)` for inspection
3. Never read without limits:
   - Log files
   - Build outputs
   - Generated files
   - Files in metrics/, logs/, dist/, build/

### Red Flags:
- File names with: output, trace, dump, log, build
- Unknown files in root directory
- Anything in ignored folders (node_modules, __pycache__, etc.)

## Why These Rules Exist

Your context can overflow from:
- Large terminal outputs returned by tools
- Large file contents returned by read operations
- Verbose script outputs fetched via get_terminal_output

This causes:
- Infinite loops in your responses
- Session crashes
- Wasted time and tokens

## The Rule Is Simple:

**If it might be large, don't fetch it. Ask the user to run/check it instead.**

---
**Last Updated:** 2025-11-22  
**Purpose:** Prevent AI assistant context overflow across all projects