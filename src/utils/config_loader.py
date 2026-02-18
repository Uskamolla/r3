from pathlib import Path
import os
import yaml

def _project_root() -> Path:
    # This file lives at src/utils/config_loader.py
    # parents[0] = src/utils/
    # parents[1] = src/          <-- this is what we return as "root"
    return Path(__file__).resolve().parents[1]

def load_config(config_path: str | None = None) -> dict:
    # Finds and loads configuration.yaml no matter where you run the code from.
    # It checks in this order:
    #   1. Path you pass directly as an argument
    #   2. CONFIG_PATH environment variable
    #   3. Default: src/config/configuration.yaml
    env_path = os.getenv("CONFIG_PATH")
    if config_path is None:
        config_path = env_path or str(_project_root() / "config" / "configuration.yaml")

    path = Path(config_path)
    if not path.is_absolute():
        path = _project_root() / path

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}