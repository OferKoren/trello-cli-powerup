from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path.home() / ".trello-cli"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class Config:
    key: str = ""
    token: str = ""
    default_board_id: str = ""

    @property
    def authed(self) -> bool:
        return bool(self.key and self.token)


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    data = json.loads(CONFIG_PATH.read_text())
    return Config(
        key=data.get("key", ""),
        token=data.get("token", ""),
        default_board_id=data.get("default_board_id", ""),
    )


def save_config(cfg: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2))
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except OSError:
        pass


def require_auth(cfg: Config) -> None:
    if not cfg.authed:
        raise SystemExit(
            "Not authenticated. Run `trello auth setup` first "
            "(get key + token at https://trello.com/app-key)."
        )


def require_board(cfg: Config) -> str:
    if not cfg.default_board_id:
        raise SystemExit(
            "No default board set. Run `trello board ls` then `trello board use <id-or-name>`."
        )
    return cfg.default_board_id
