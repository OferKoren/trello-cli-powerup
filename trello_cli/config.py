from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path.home() / ".trello-cli"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_PROFILE = "default"


@dataclass
class Config:
    key: str = ""
    token: str = ""
    default_board_id: str = ""
    power_up_id: str = ""
    power_up_secret: str = ""

    @property
    def authed(self) -> bool:
        return bool(self.key and self.token)


def _read_raw() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text())


def _write_raw(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2))
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except OSError:
        pass


def _migrate(data: dict) -> dict:
    """Convert old flat config to profiles format."""
    if "profiles" in data:
        return data
    profile = {k: data.get(k, "") for k in ("key", "token", "default_board_id", "power_up_id", "power_up_secret")}
    return {
        "active_profile": DEFAULT_PROFILE,
        "profiles": {DEFAULT_PROFILE: profile},
    }


def _profile_to_config(p: dict) -> Config:
    return Config(
        key=p.get("key", ""),
        token=p.get("token", ""),
        default_board_id=p.get("default_board_id", ""),
        power_up_id=p.get("power_up_id", ""),
        power_up_secret=p.get("power_up_secret", ""),
    )


def load_config() -> Config:
    data = _migrate(_read_raw())
    active = data.get("active_profile", DEFAULT_PROFILE)
    profile = data.get("profiles", {}).get(active, {})
    return _profile_to_config(profile)


def save_config(cfg: Config) -> None:
    data = _migrate(_read_raw())
    active = data.get("active_profile", DEFAULT_PROFILE)
    data.setdefault("profiles", {})[active] = asdict(cfg)
    _write_raw(data)


def list_profiles() -> tuple[str, dict[str, Config]]:
    """Return (active_name, {name: Config})."""
    data = _migrate(_read_raw())
    active = data.get("active_profile", DEFAULT_PROFILE)
    profiles = {name: _profile_to_config(p) for name, p in data.get("profiles", {}).items()}
    return active, profiles


def switch_profile(name: str) -> Config:
    data = _migrate(_read_raw())
    if name not in data.get("profiles", {}):
        raise SystemExit(f"Profile '{name}' not found. Use `trello auth ls` to see available profiles.")
    data["active_profile"] = name
    _write_raw(data)
    return _profile_to_config(data["profiles"][name])


def save_profile(name: str, cfg: Config) -> None:
    data = _migrate(_read_raw())
    data.setdefault("profiles", {})[name] = asdict(cfg)
    _write_raw(data)


def get_active_profile_name() -> str:
    data = _migrate(_read_raw())
    return data.get("active_profile", DEFAULT_PROFILE)


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


def require_power_up(cfg: Config) -> None:
    if not cfg.power_up_id:
        raise SystemExit(
            "Power-Up id not configured. Run `trello auth setup --power-up-id <id>` "
            "(get it from https://trello.com/power-ups/admin)."
        )
