"""Metric logging utilities for Apex Agent."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def get_metrics_path() -> Path:
    """Get the path to the metrics directory."""
    return Path(__file__).parent.parent / "metrics"


def log_registry_scan(duration_ms: float, file_count: int, metadata: dict[str, Any] | None = None) -> None:
    """
    Log a registry scan metric.
    
    Args:
        duration_ms: Duration of the scan in milliseconds
        file_count: Number of files scanned
        metadata: Additional metadata to log
    """
    metrics_file = get_metrics_path() / "registry_scan.log"
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "duration_ms": duration_ms,
        "file_count": file_count,
        "metadata": metadata or {},
    }
    
    # Ensure metrics directory exists
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Append to log file
    with open(metrics_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def log_agent_execution(
    agent_name: str,
    duration_ms: float,
    success: bool,
    metadata: dict[str, Any] | None = None
) -> None:
    """
    Log an agent execution metric.
    
    Args:
        agent_name: Name of the agent
        duration_ms: Duration of execution in milliseconds
        success: Whether the execution was successful
        metadata: Additional metadata to log
    """
    metrics_file = get_metrics_path() / "agent_execution.log"
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "duration_ms": duration_ms,
        "success": success,
        "metadata": metadata or {},
    }
    
    # Ensure metrics directory exists
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Append to log file
    with open(metrics_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
