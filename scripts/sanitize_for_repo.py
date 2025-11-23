#!/usr/bin/env python3
"""Scan codebase for hardcoded paths and personal info before repo creation.

Usage:
    python scripts/sanitize_for_repo.py

Exit codes:
    0: Clean - safe to publish
    1: Issues found - review before publishing
"""
import re
from pathlib import Path


# Patterns to detect
PATTERNS = {
    'e_drive_ai': r'E:\\AI',
    'venv_specific': r'E:\\AI\\venvs\\[^\s\'"]+',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
}


def scan_file(file_path):
    """Scan a single file for sensitive patterns."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return []

    findings = []
    for pattern_name, pattern in PATTERNS.items():
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'file': str(file_path.relative_to(Path(__file__).parent.parent)),
                'line': line_num,
                'pattern': pattern_name,
                'match': match.group()
            })

    return findings


def main():
    root = Path(__file__).parent.parent
    
    # Files to scan
    extensions = ['.py', '.ps1', '.md', '.toml', '.json', '.txt', '.yml', '.yaml']
    ignore_dirs = {'.venv', '.git', '__pycache__', '.obsidian', 'metrics', 'node_modules'}
    
    all_findings = []
    
    print("Scanning codebase for hardcoded paths and personal info...")
    print()
    
    for ext in extensions:
        for file_path in root.rglob(f'*{ext}'):
            if any(ignore in file_path.parts for ignore in ignore_dirs):
                continue
            findings = scan_file(file_path)
            all_findings.extend(findings)
    
    if not all_findings:
        print("RESULT: Clean - No hardcoded paths or personal info found")
        print("Safe to publish to GitHub")
        print()
        return 0
    
    print(f"RESULT: Found {len(all_findings)} issues")
    print()
    
    # Group by file
    by_file = {}
    for finding in all_findings:
        file = finding['file']
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(finding)
    
    for file, findings in sorted(by_file.items()):
        print(f"FILE: {file}")
        for f in findings:
            print(f"  Line {f['line']:4d}: [{f['pattern']:20s}] {f['match']}")
        print()
    
    print("ACTIONS REQUIRED:")
    print("  1. Replace hardcoded E:\\\\AI paths with configurable defaults")
    print("  2. Remove any email addresses if found")
    print("  3. Re-run this script until clean")
    print()
    
    return 1


if __name__ == '__main__':
    exit(main())
