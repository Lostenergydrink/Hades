#!/usr/bin/env python3
"""Rename agents to Hades mythology theme."""
from pathlib import Path


# Agent rename mapping
AGENT_RENAMES = {
    'router': 'hades',
    'code': 'styx',
    'lint': 'furies',
    'terminal': 'thanatos',
    'test': 'persephone',
    'web_automation': 'hermes',
}

# Text replacements for classes and references
TEXT_REPLACEMENTS = [
    ('HadesAgent', 'HadesAgent'),
    ('hades_agent', 'hades_agent'),
    ('StyxAgent', 'StyxAgent'),
    ('StyxAgent', 'StyxAgent'),
    ('styx_agent', 'styx_agent'),
    ('FuriesAgent', 'FuriesAgent'),
    ('FuriesAgent', 'FuriesAgent'),
    ('furies_agent', 'furies_agent'),
    ('ThanatosAgent', 'ThanatosAgent'),
    ('ThanatosAgent', 'ThanatosAgent'),
    ('thanatos_agent', 'thanatos_agent'),
    ('PersephoneAgent', 'PersephoneAgent'),
    ('persephone_agent', 'persephone_agent'),
    ('HermesAgent', 'HermesAgent'),
    ('hermes_agent', 'hermes_agent'),
]


def rename_directories(root):
    """Rename agent directories."""
    agents_dir = root / 'agent_app' / 'agents'
    
    print("Renaming agent directories...")
    for old_name, new_name in AGENT_RENAMES.items():
        old_path = agents_dir / old_name
        new_path = agents_dir / new_name
        
        if old_path.exists():
            old_path.rename(new_path)
            print(f"  Renamed: {old_name}/ -> {new_name}/")
            
            # Rename agent file inside
            old_file = new_path / f'{old_name}_agent.py'
            new_file = new_path / f'{new_name}_agent.py'
            if old_file.exists():
                old_file.rename(new_file)
                print(f"  Renamed: {old_name}_agent.py -> {new_name}_agent.py")
    print()


def update_file_content(file_path):
    """Update text content in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        for old, new in TEXT_REPLACEMENTS:
            content = content.replace(old, new)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"ERROR: {file_path}: {e}")
        return False


def update_all_references(root):
    """Update all text references in codebase."""
    extensions = ['.py', '.md', '.toml', '.json', '.txt']
    ignore_dirs = {'.venv', '.git', '__pycache__', '.obsidian', 'metrics', 'node_modules'}
    
    modified = []
    
    print("Updating text references...")
    for ext in extensions:
        for file_path in root.rglob(f'*{ext}'):
            if any(ignore in file_path.parts for ignore in ignore_dirs):
                continue
            
            if update_file_content(file_path):
                rel_path = file_path.relative_to(root)
                modified.append(str(rel_path))
                print(f"  Modified: {rel_path}")
    
    print(f"\nUpdated {len(modified)} files")
    print()


def main():
    root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("Hades Mythology Rename")
    print("=" * 60)
    print()
    
    print("Mapping:")
    for old, new in AGENT_RENAMES.items():
        print(f"  {old:20s} -> {new}")
    print()
    
    # Step 1: Rename directories and files
    rename_directories(root)
    
    # Step 2: Update all text references
    update_all_references(root)
    
    print("=" * 60)
    print("Mythology rename complete!")
    print("=" * 60)
    print()
    print("Agent Pantheon:")
    print("  Hades      - Router/Orchestrator")
    print("  Styx       - Code/Refactor")
    print("  Furies     - Lint/Format/Enforcement")
    print("  Thanatos   - Terminal/Ops")
    print("  Persephone - Test Runner")
    print("  Hermes     - Web Automation")
    print()


if __name__ == '__main__':
    main()
