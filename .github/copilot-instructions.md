# GitHub Copilot Instructions for Hades

🚨 **CRITICAL: Read `.copilot-safety.md` before any operations** 🚨

## Primary Safety Rules

### When Running Scripts with Potential Large Output:
**ALWAYS provide the command for the user to run manually:**

```
For guardrail protection, please run this command directly in your terminal:

<command here>

Then let me know if it worked or if you got any errors.
```

**NEVER:**
- Use `get_terminal_output` for test/trace/debug scripts
- Use `run_in_terminal` and then fetch output
- Ask to "check the output" yourself

### When Reading Files:
1. Check file size with `get_file_info` first
2. Use `grep_search` or `semantic_search` for large files
3. Read with `limit` parameter for unknown files
4. Never read files in `metrics/`, logs, or build outputs without size check

### Signs You're About to Cause Issues:
- About to run a test script and check output
- About to read a file without knowing size
- About to fetch terminal output from running process
- User is running verbose/tracing scripts

**STOP and provide manual commands instead.**

## This Protects:
- Your context from overflow
- The development session from crashes
- User's time and patience

## Full Details:
See `.copilot-safety.md` for complete incident history and guidelines.

---
**Last Updated:** 2025-11-22  
**Status:** 🚨 ENFORCED
