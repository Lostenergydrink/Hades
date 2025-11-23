# 🚨 CRITICAL: Copilot Safety Guidelines for Hades Development

⚠️ **READ THIS BEFORE ANY SESSION** ⚠️

## Context
When GitHub Copilot (me) helps develop Hades, I can encounter issues with large outputs that your agent guardrails don't protect against. This file documents best practices for our collaboration and lessons learned from actual incidents.

## For Copilot (Me)

### Before Reading Any File:
1. ✅ Use `get_file_info` to check file size first
2. ✅ If file > 500 lines, use `grep_search` or `semantic_search` instead
3. ✅ Always use `read_file` with `limit` parameter for unknown files
4. ✅ Start with `read_file(limit=100)` for initial inspection

### Search Strategy:
```
Priority 1: semantic_search("specific concept")
Priority 2: grep_search("function_name", includePattern="specific_file.py")
Priority 3: read_file(limit=50) for small sections
Last Resort: read_file() without limits (only for known-small files)
```

### Red Flags:
- 🚨 Any .log, .txt, .json file in root (likely huge)
- 🚨 Files with "output", "trace", "dump" in name
- 🚨 Unknown files without size check first

## For User (You)

### When Requesting Help:
✅ **Good Requests:**
- "Find the `CommandSafetyChecker` class implementation"
- "Show me how `run_command` is defined"
- "Search for error handling in thanatos_agent.py"
- "Read first 100 lines of config.py"

❌ **Risky Requests:**
- "Read terminal_tools.py" (unknown size)
- "Show me everything in that file"
- "What's in metrics/?" (could be huge logs)

### If I Start Looping:
1. **Stop me immediately** (cancel button)
2. Rephrase request more specifically
3. Guide me to use targeted search

### Emergency Recovery:
If conversation becomes unstable:
1. Start new conversation
2. Reference this file first
3. Use specific, targeted queries

## File Size Reference

Safe to read directly (< 500 lines):
- Most agent files in `agent_app/agents/`
- Config files in `config/`
- Test files in `tests/`

Check before reading:
- Root-level .md files
- Anything in `metrics/`, `logs/`
- Generated files
- Build outputs

## Your Agent's Guardrails vs. My Limitations

**Your Guardrails Protect:** Production Hades system from bad inputs/outputs
**Doesn't Protect:** Me (Copilot) from VS Code returning huge data

**Solution:** This file + your vigilance during development

## Project Structure Reminders

```
agent_app/              # Core agent code (~200 lines per file)
  agents/               # Individual agents (modular)
    terminal/           # Thanatos (split into multiple files)
    code/              # Styx
    router/            # Hades (Router)
config/                # Config files (small)
tests/                 # Test files (small)
metrics/              # ⚠️  May contain large logs
scripts/              # Utility scripts
docs/                 # Documentation
```

## Best Practice: Modular Development

Since your codebase IS well-structured with small, focused files, I should rarely need to read large files. If I do, that's a sign to:
1. Ask for specific section/function names
2. Use search tools instead
3. Check file size first

---

## Actual Incident: Terminal Output Loop (2025-11-22)

**What Happened:**
1. User ran: `python.exe .\scripts\test_tracing.py`
2. Script produced massive output (likely loop or verbose tracing)
3. Terminal returned huge output to me via `get_terminal_output`
4. I got stuck processing/echoing the massive output
5. I "fixed" the script by simplifying it
6. I asked user to run again
7. **User correctly stopped me** - script simplification wouldn't prevent MY output overflow

**Root Cause:**
- NOT user error
- NOT the script necessarily (it might be working as designed)
- **MY** inability to handle large terminal outputs
- The "fix" I proposed wouldn't have helped ME, only changed what outputs

**Actual Solutions:**
1. ✅ **User should run scripts directly** without me watching output
2. ✅ **User reports results** to me ("it worked" / "got error X")
3. ✅ **Don't use `get_terminal_output`** for test scripts with verbose output
4. ❌ **Simplifying scripts doesn't help ME** if output is still large

**Lesson:** If I ask you to run a command that might produce large output and then I'll check it:
- 🛑 **Stop me and run it yourself instead**
- ✅ **Tell me the result summary only**
- ✅ **If there's an error, copy JUST the error**

## Critical Rules for Both of Us

### 🚨 When I'm About to Get Overwhelmed:

**Signs I'm going to loop:**
- I ask you to run a test/trace/debug script
- I say "let me check the output"
- The script has verbose logging/tracing
- The command runs in background or loops

**What You Should Do:**
1. Run it yourself in terminal
2. Check if it works
3. Report back: "worked fine" or "got error: [paste error only]"
4. **Don't let me fetch terminal output**

**What I Should Do:**
1. **Provide the exact command for you to run**
2. Explain: "For guardrail protection, please run this directly"
3. Ask you to report back: "worked" / "error: X"
4. **Never fetch terminal output** for test/trace/debug scripts
5. Trust your summary instead of fetching data

**Example Response:**
```
For guardrail protection, please run this command directly in your terminal:

python .\scripts\test_tracing.py

Then let me know if it worked or if you got any errors.
```

---

**Last Updated:** 2025-11-22  
**Purpose:** Prevent development-time issues while building production-safe Hades  
**Status:** 🚨 CRITICAL - Review before each session
