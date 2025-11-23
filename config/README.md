# Configuration Files

This directory contains configuration files for the Apex Agent.

## Files

- `hades_config.toml`: Main configuration file for the Apex Agent system.

## Configuration Sections

### [agent]
Controls the core agent behavior, including model selection, token limits, and temperature settings.

### [guardrails]
Defines safety and operational limits for agent execution, including strict mode, timeouts, and logging preferences.

### [registry]
Configures the project registry scanning behavior, including default entry points and exclusion patterns.

### [logging]
Sets logging preferences, including log level and output file location.

### [testing]
Defines testing framework and coverage requirements.

## Usage

The configuration is loaded automatically by `agent_app/config.py`. To modify agent behavior, edit the values in `hades_config.toml`.
