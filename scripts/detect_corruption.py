"""
File Corruption Detection Script

Scans Python files for signs of corruption:
1. Abnormal file sizes
2. ASCII art pattern spam
3. Internal reasoning text leakage
4. Repetitive content patterns

Usage:
    python scripts/detect_corruption.py
"""

from pathlib import Path
import re
from typing import List, Tuple


# File size thresholds (in bytes)
SIZE_WARNING = 20_000  # 20KB
SIZE_CRITICAL = 50_000  # 50KB

# Corruption patterns
ASCII_ART_PATTERN = re.compile(r'\.{16}\*{2,}')  # ................**
MONOLOGUE_PATTERNS = [
    r"We'll proceed",
    r"Need to ensure",
    r"unstoppable",
    r"glimpsed",
    r"mania",
    r"Let's call",
    r"We'll patch",
]

# High repetition threshold
MAX_LINE_REPETITION = 50  # Same line repeated more than this is suspicious


def check_file_size(file_path: Path) -> Tuple[bool, str]:
    """Check if file size is abnormal."""
    size = file_path.stat().st_size
    
    if size > SIZE_CRITICAL:
        return True, f"CRITICAL: File is {size:,} bytes (>{SIZE_CRITICAL:,})"
    elif size > SIZE_WARNING:
        return True, f"WARNING: File is {size:,} bytes (>{SIZE_WARNING:,})"
    
    return False, ""


def check_ascii_art(content: str) -> Tuple[bool, str]:
    """Check for ASCII art spam patterns."""
    matches = ASCII_ART_PATTERN.findall(content)
    
    if len(matches) > 10:  # More than 10 occurrences is suspicious
        return True, f"ASCII art pattern found {len(matches)} times"
    
    return False, ""


def check_monologue(content: str) -> Tuple[bool, str]:
    """Check for internal monologue leakage."""
    found_patterns = []
    
    for pattern in MONOLOGUE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            found_patterns.append(pattern)
    
    if len(found_patterns) >= 2:  # Multiple patterns suggest corruption
        return True, f"Internal monologue detected: {', '.join(found_patterns[:3])}"
    
    return False, ""


def check_repetition(content: str) -> Tuple[bool, str]:
    """Check for highly repetitive content."""
    lines = content.split('\n')
    line_counts = {}
    
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 10:  # Ignore empty/short lines
            line_counts[stripped] = line_counts.get(stripped, 0) + 1
    
    for line, count in line_counts.items():
        if count > MAX_LINE_REPETITION:
            preview = line[:50] + "..." if len(line) > 50 else line
            return True, f"Line repeated {count} times: {preview}"
    
    return False, ""


def scan_file(file_path: Path) -> List[str]:
    """Scan a single file for corruption signs."""
    issues = []
    
    # Skip self (this detection script contains pattern examples)
    if file_path.name == "detect_corruption.py":
        return issues
    
    # Check file size
    is_issue, msg = check_file_size(file_path)
    if is_issue:
        issues.append(f"SIZE: {msg}")
    
    # Read content for pattern checks
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        issues.append(f"READ ERROR: {e}")
        return issues
    
    # Check for ASCII art
    is_issue, msg = check_ascii_art(content)
    if is_issue:
        issues.append(f"ASCII ART: {msg}")
    
    # Check for monologue
    is_issue, msg = check_monologue(content)
    if is_issue:
        issues.append(f"MONOLOGUE: {msg}")
    
    # Check for repetition
    is_issue, msg = check_repetition(content)
    if is_issue:
        issues.append(f"REPETITION: {msg}")
    
    return issues


def main():
    """Main scan function."""
    print("=" * 70)
    print("FILE CORRUPTION DETECTION SCAN")
    print("=" * 70)
    print()
    
    project_root = Path(__file__).parent.parent
    corrupted_files = []
    total_scanned = 0
    
    # Scan all Python files
    for py_file in project_root.rglob("*.py"):
        # Skip virtual environments and caches
        if any(part in py_file.parts for part in ['.venv', 'venv', '__pycache__', '.git']):
            continue
        
        total_scanned += 1
        issues = scan_file(py_file)
        
        if issues:
            relative_path = py_file.relative_to(project_root)
            corrupted_files.append((relative_path, issues))
    
    # Report results
    print(f"Scanned {total_scanned} Python files\n")
    
    if corrupted_files:
        print(f"⚠️  FOUND {len(corrupted_files)} FILE(S) WITH ISSUES:\n")
        
        for file_path, issues in corrupted_files:
            print(f"📄 {file_path}")
            for issue in issues:
                print(f"   • {issue}")
            print()
        
        print("=" * 70)
        print("RECOMMENDATION: Inspect these files manually and restore if corrupted")
        print("=" * 70)
        return 1
    else:
        print("✅ No corruption detected in any Python files")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    exit(main())
