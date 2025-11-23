#!/usr/bin/env python3
"""Replace Hades with Hades throughout codebase."""
from pathlib import Path


REPLACEMENTS = [
    ('Hades', 'Hades'),
    ('hades', 'hades'),
    ('hades', 'hades'),
    ('HADES', 'HADES'),
    ('launch_hades.ps1', 'launch_hades.ps1'),
]


def replace_in_file(file_path):
    """Replace all occurrences in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"ERROR: {file_path}: {e}")
        return False


def main():
    root = Path(__file__).parent.parent
    
    # Files to process
    extensions = ['.py', '.ps1', '.md', '.toml', '.json', '.txt', '.yml', '.yaml']
    ignore_dirs = {'.venv', '.git', '__pycache__', '.obsidian', 'metrics', 'node_modules'}
    
    modified = []
    
    print("Replacing Hades with Hades...")
    print()
    
    for ext in extensions:
        for file_path in root.rglob(f'*{ext}'):
            if any(ignore in file_path.parts for ignore in ignore_dirs):
                continue
            
            if replace_in_file(file_path):
                rel_path = file_path.relative_to(root)
                modified.append(str(rel_path))
                print(f"  Modified: {rel_path}")
    
    print()
    print(f"RESULT: Modified {len(modified)} files")
    
    # Rename script file itself
    old_script = root / 'scripts' / 'launch_hades.ps1'
    new_script = root / 'scripts' / 'launch_hades.ps1'
    
    if old_script.exists():
        old_script.rename(new_script)
        print(f"  Renamed: scripts/launch_hades.ps1 -> scripts/launch_hades.ps1")
    
    print()
    print("Rebranding complete!")
    print()


if __name__ == '__main__':
    main()
