# Hades Scripts

This directory contains operational scripts for launching, testing, and maintaining Hades.

## Entry Points

- `launch_hades.ps1`: PowerShell script to launch Hades with proper environment setup.
- `main.py`: The main Python entry point for the agent.

## Utility Scripts

- `clean.ps1`: Removes temporary files, caches, and build artifacts.

## Running Scripts

### Launch the Agent
```powershell
.\launch_hades.ps1
```

### Run Python Entry Point
```powershell
python main.py
```

### Clean Temporary Files
```powershell
.\clean.ps1
```

## Tasks

For consistent task execution across the team, use the provided task runner:

### Using tasks.json (VS Code)
Press `Ctrl+Shift+P` and select "Tasks: Run Task", then choose:
- `Launch Hades`
- `Run Tests`
- `Clean Workspace`

### Using make.ps1
```powershell
.\make.ps1 launch    # Launch the agent
.\make.ps1 test      # Run all tests
.\make.ps1 lint      # Run linting
.\make.ps1 clean     # Clean temporary files
```
