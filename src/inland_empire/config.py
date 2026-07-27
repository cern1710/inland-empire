"""Loads application configuration from config/config.yaml.

config/config.yaml is gitignored since it holds real credentials,
whereas config/config.example.yaml is a committed template.
"""

import os
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.yaml"
EXAMPLE_CONFIG_PATH = CONFIG_DIR / "config.example.yaml"

CONFIG_PATH_ENV_VAR = "INLAND_EMPIRE_CONFIG"


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Loads the app config.

    Resolution order:
        1. explicit `config_path` argument
        2. INLAND_EMPIRE_CONFIG environment variable
        3. config/config.yaml
    """
    path = Path(config_path or os.environ.get(CONFIG_PATH_ENV_VAR, DEFAULT_CONFIG_PATH))

    if not path.exists():
        raise FileNotFoundError(
            f"No config file at {path}. Copy {EXAMPLE_CONFIG_PATH.relative_to(REPO_ROOT)} "
            f"to {DEFAULT_CONFIG_PATH.relative_to(REPO_ROOT)} and fill in your own values."
        )

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
