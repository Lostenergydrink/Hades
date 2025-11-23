#!/usr/bin/env python3
"""Update documentation to use mythology names."""
from pathlib import Path


# Documentation text replacements
DOC_REPLACEMENTS = [
    # Generic agent references
    ('Code / Refactor agent', 'Styx (Code/Refactor)'),
    ('Code Agent', 'Styx'),
    ('Code agent', 'Styx'),
    ('Lint & Format agent', 'Furies (Lint/Format)'),
    ('Lint Agent', 'Furies'),
    ('Lint agent', 'Furies'),
    ('Terminal / Ops agent', 'Thanatos (Terminal/Ops)'),
    ('Terminal Agent', 'Thanatos'),
    ('Terminal agent', 'Thanatos'),
    ('Test Runner / QA agent', 'Persephone (Test Runner)'),
    ('Test Runner agent', 'Persephone'),
    ('Test Agent', 'Persephone'),
    ('Test agent', 'Persephone'),
    ('Web Automation agent', 'Hermes (Web Automation)'),
    ('Web Agent', 'Hermes'),
    ('Web agent', 'Hermes'),
    ('Router agent', 'Hades (Router)'),
    ('Router Agent', 'Hades'),
    
    # Context-specific phrases
    ('escalates to Code Agent', 'escalates to Styx'),
    ('asking Code Agent to integrate', 'asking Styx to integrate'),
    ('through Code Agent', 'through Styx'),
    ('handed to the Code agent', 'handed to Styx'),
    ('Code / Refactor', 'Styx (Code/Refactor)'),
    ('Lint & Format', 'Furies (Lint/Format)'),
    ('Terminal / Ops', 'Thanatos (Terminal/Ops)'),
    ('Test Runner / QA', 'Persephone (Test Runner)'),
    ('Web Automation', 'Hermes (Web Automation)'),
]


def update_file(file_path):
    """Update text in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for old, new in DOC_REPLACEMENTS:
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
    
    # Only update markdown documentation
    extensions = ['.md']
    ignore_dirs = {'.venv', '.git', '__pycache__', '.obsidian', 'metrics', 'node_modules'}
    
    modified = []
    
    print("Updating documentation with mythology names...")
    print()
    
    for ext in extensions:
        for file_path in root.rglob(f'*{ext}'):
            if any(ignore in file_path.parts for ignore in ignore_dirs):
                continue
            
            if update_file(file_path):
                rel_path = file_path.relative_to(root)
                modified.append(str(rel_path))
                print(f"  Updated: {rel_path}")
    
    print()
    print(f"Updated {len(modified)} documentation files")
    print()


if __name__ == '__main__':
    main()
