from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[import-not-found, no-redef]


def _find_project_root() -> Path:
    """Find project root by looking for config directory."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "config" / "hades_config.toml").exists():
            return current
        current = current.parent
    # Fallback to current directory if not found
    return Path.cwd()


PROJECT_ROOT = _find_project_root()


def load_config_from_toml(config_path: Path | None = None) -> dict:
    """Load configuration from TOML file."""
    if config_path is None:
        config_path = PROJECT_ROOT / "config" / "hades_config.toml"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, "rb") as f:
        return tomllib.load(f)


@dataclass
class AgentConfig:
    apex_root: Path = PROJECT_ROOT
    # Intentionally empty to avoid bias toward historical projects. Override via
    # env vars or CLI arguments when launching the agent.
    default_projects: tuple[Path, ...] = ()
    
    @classmethod
    def from_toml(cls, config_path: Path | None = None) -> "AgentConfig":
        """Create AgentConfig from TOML file."""
        _toml_config = load_config_from_toml(config_path)
        config = cls()
        # Additional configuration loading logic can be added here
        # TODO: Parse toml_config sections when needed
        return config


CONFIG = AgentConfig.from_toml()
